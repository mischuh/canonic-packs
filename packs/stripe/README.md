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
- `contracts/metrics/`: `gross_revenue`, `refunded_amount`, `net_revenue`, `refund_rate`,
  `successful_payments`, `new_customers`, `new_subscriptions`, `active_subscriptions`,
  `trialing_subscriptions`, `canceled_subscriptions`.
- `contracts/guardrails/`: a live-mode filter on each of the three sources and a single-currency
  filter on charges. All `mandatory_filter`, `severity: warn`.
- `knowledge/global/`: amounts and currency, revenue definitions, subscription status, test mode
  and accounts. Linked to the semantic entities via `sl_refs`, so drift detection flags them if
  the underlying definition changes.

Time axes (`charge_date`, `customer_created_date`, `subscription_start_date`, `canceled_date`) are
daily and in UTC.

## Params

| param | required | notes |
| --- | --- | --- |
| `connection_id` | yes | existing `canonic.yaml` connection, bound automatically by the wizard |
| `currency` | yes | picked from the currencies of live charges, lowercase ISO code |
| `schema` | no | default `stripe` |
| `charges_table` / `customers_table` / `subscriptions_table` | no | default `charges` / `customers` / `subscriptions` |
| `minor_unit_divisor` | no | default `100`, use `1` for zero-decimal currencies such as JPY |

## Not in v1

- **MRR and its movements.** Subscription items are inside `subscriptions.items` (jsonb) and the
  billing interval is inside `prices.recurring` (jsonb).
- **A history of active subscriptions.** The tables hold current state only. Counting active
  subscriptions per past month needs snapshots.
- **Currency conversion.** Revenue is reported in the one currency chosen at install.
- **Refund-date view.** Refunds are read from `charges.amount_refunded` and attributed to the
  charge date.
- **Disputes, fees, taxes and payouts.**
- **The warehouse Data Pipeline** (Snowflake, Redshift, Databricks, BigQuery). Its column lists
  were not verifiable from the public documentation when this pack was written, so it is a later
  variant of the same models.
