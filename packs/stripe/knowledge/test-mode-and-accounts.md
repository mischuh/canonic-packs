---
summary: "Which Stripe data is counted: live mode only, one pipeline per Stripe account, and the sync's freshness."
tags: [stripe, livemode, accounts, caveat]
sl_refs:
  - "{{connection_id}}.stripe_charges"
  - "{{connection_id}}.stripe_customers"
  - "{{connection_id}}.stripe_subscriptions"
usage_mode: caveat
refs: [revenue-definitions]
meta:
  provenance: human_curated
---

## Live mode only

Every table has a `livemode` column. The pack's `stripe-live-mode-*` guardrails filter charges,
customers and subscriptions to `livemode = true`, so test mode objects do not inflate revenue or
customer counts. The guardrails ship at `severity: warn`. If you want to analyze a sandbox, edit the
guardrail filters under `contracts/guardrails/`.

## More than one Stripe account

Each row carries `_account_id`, exposed as the `stripe_account` dimension on charges. Stripe
recommends one schema per pipeline and the account id as the schema name. Install the pack once per
schema, or group by `stripe_account` if several accounts share a schema.

## Freshness

The tables come from Stripe's real-time sync to Postgres, which was in public preview when this
pack was written. A row can briefly show an earlier state while a change is syncing, and a table
only exists if it was selected for the pipeline in the Stripe dashboard.

Refunds are read from the `amount_refunded` column on charges, so the separate `refunds` table is
not needed. See [[revenue-definitions]].
