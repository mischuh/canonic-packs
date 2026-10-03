# Stripe context pack

Curated `semantics/`, `contracts/`, and `knowledge/` content for [Stripe](https://stripe.com)
payments, customers and subscriptions, installed once via `canonic pack add stripe` (or the
`canonic setup` wizard's pack branch) and then edited like any other accepted project context. It
does not bypass review. It starts the project with `provenance: human_curated` content instead of
`inferred` content, so the first review is "does this match my instance," not "is this a sane
measure at all."

See `AMENDMENT-context-packs.md` in the `canonic` repo for the full mechanism spec this pack
implements against.

**Requires canonic 0.31.0 or later.** The time dimensions use `dimensions[].expr`
(AMENDMENT-dimension-expr), because Stripe stores every timestamp as a `bigint` of Unix seconds.

## Variants

| id | label | connector | source |
| --- | --- | --- | --- |
| `postgres` | Stripe Data Pipeline real-time sync to Postgres | `postgres` | [Stripe's real-time sync schema](https://docs.stripe.com/data/data-pipeline/real-time-sync-to-postgres/schema) |

The real-time sync was in public preview when this pack was written. It maps Stripe API objects
one to one onto Postgres tables, which is what the models here follow.

## What this installs

- `semantics/<connection_id>/stripe_charges.yaml`, `stripe_customers.yaml`, `stripe_subscriptions.yaml`.
  Charges and subscriptions join many-to-one to customers.
- `contracts/metrics/`: `gross_revenue`, `refunded_amount`, `net_revenue`, `refund_rate`, `refunds_issued`,
  `successful_payments`, `new_customers`, `new_subscriptions`, `active_subscriptions`,
  `trialing_subscriptions`, `canceled_subscriptions`.
- `contracts/guardrails/`: a live-mode filter on each source and a single-currency filter on charges
  and refunds. All `mandatory_filter`, `severity: warn`. The filter is always applied, `warn` only
  adds an entry to the query result's `warnings`. Refunds have no `livemode` column, so their
  guardrail reads it from the refunded charge.
- `knowledge/global/`: amounts and currency, revenue definitions, subscription status, test mode
  and accounts. Linked to the semantic entities via `sl_refs`, so drift detection flags them if
  the underlying definition changes.

Time axes (`charge_date`, `customer_created_date`, `subscription_start_date`, `canceled_date`, `refund_date`) are
daily and in UTC.

`net_revenue` is charged amount minus refunded amount. It excludes Stripe fees, disputes and
payouts, so it is higher than the dashboard's net volume.

## Params

| param | required | notes |
| --- | --- | --- |
| `connection_id` | yes | existing `canonic.yaml` connection, bound automatically by the wizard |
| `currency` | yes | picked from the currencies of live charges, lowercase ISO code |
| `schema` | no | default `stripe` |
| `charges_table` / `customers_table` / `subscriptions_table` / `refunds_table` | no | default `charges` / `customers` / `subscriptions` / `refunds` |
| `minor_unit_divisor` | no | default `100`, use `1` for zero-decimal currencies such as JPY |

## Not in v1

- **MRR and its movements.** Subscription items are inside `subscriptions.items` (jsonb), with
  the price and billing interval embedded in each item. Summing them needs an unnest of that JSON
  array, and a semantic source can only point at a physical table or view, so there is no way to
  express it in a measure yet. A measure with a scalar subquery over `jsonb_array_elements` was
  tried and is rejected by the reference validator. Until sources can be defined by SQL, create a
  view that flattens the items and model that view yourself, see below.
- **A history of active subscriptions.** The tables hold current state only. Counting active
  subscriptions per past month needs snapshots.
- **Currency conversion.** Revenue is reported in the one currency chosen at install.
- **Net revenue on the refund date.** `net_revenue` attributes refunds to the charge date. Use
  `refunds_issued` for refunds by the day they were issued.
- **Disputes, fees, taxes and payouts.**
- **The warehouse Data Pipeline** (Snowflake, Redshift, Databricks, BigQuery). Its column lists
  were not verifiable from the public documentation when this pack was written, so it is a later
  variant of the same models.

## MRR workaround: a flattened items view

Until a source can be defined by SQL, flatten the line items into a view in the same schema and
model the view as an extra source in your project:

```sql
CREATE VIEW stripe.subscription_items_flat AS
SELECT s.id AS subscription_id, s.customer, s.status, s.currency, s.livemode,
       (i.value->'price'->>'unit_amount')::numeric
         * coalesce((i.value->>'quantity')::numeric, 1)
         / coalesce((i.value->'price'->'recurring'->>'interval_count')::numeric, 1)
         * CASE i.value->'price'->'recurring'->>'interval'
             WHEN 'year'  THEN 1.0 / 12
             WHEN 'month' THEN 1.0
             WHEN 'week'  THEN 52.0 / 12
             WHEN 'day'   THEN 365.0 / 12
           END AS monthly_amount
FROM stripe.subscriptions s,
     LATERAL jsonb_array_elements(s.items->'data') AS i;
```

A `sum(monthly_amount) / 100.0` measure over this view, filtered to `status IN ('active',
'past_due')`, `livemode` and one currency, is the current MRR. Trials are excluded, discounts are
not applied.
