---
summary: "Which Stripe data is counted: live mode only, one pipeline per Stripe account, and the sync's freshness."
tags: [stripe, livemode, accounts, caveat]
sl_refs:
  - "{{connection_id}}.stripe_charges"
  - "{{connection_id}}.stripe_customers"
  - "{{connection_id}}.stripe_subscriptions"
  - "{{connection_id}}.stripe_refunds"
usage_mode: caveat
refs: [revenue-definitions]
meta:
  provenance: human_curated
---

## Live mode only

Charges, customers and subscriptions have a `livemode` column. The pack's `stripe-live-mode-*`
guardrails filter them to `livemode = true`, so test mode objects do not inflate revenue or customer
counts. Refunds have no such column, so the refunds guardrail reads `livemode` from the refunded
charge.

The guardrails ship at `severity: warn`. For a `mandatory_filter`, `warn` does not mean the filter is
optional. The predicate is always added to the query, and `warn` additionally lists the guardrail in
the result's `warnings`, so the agent can tell the user that test data was excluded. If you want to
analyze a sandbox, edit the guardrail filters under `contracts/guardrails/`.

## More than one Stripe account

Each row carries `_account_id`, exposed as the `stripe_account` dimension on charges. Stripe
recommends one schema per pipeline and the account id as the schema name. Install the pack once per
schema, or group by `stripe_account` if several accounts share a schema.

## Freshness

The tables come from Stripe's real-time sync to Postgres, which was in public preview when this
pack was written. A row can briefly show an earlier state while a change is syncing, and a table
only exists if it was selected for the pipeline in the Stripe dashboard.

Revenue metrics read refunds from the `amount_refunded` column on charges. `refunds_issued` reads
the `refunds` table. See [[revenue-definitions]].
