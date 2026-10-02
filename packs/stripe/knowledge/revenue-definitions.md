---
summary: "How gross revenue, refunds and net revenue are defined, and which charges and dates they use."
tags: [stripe, revenue, definitions]
sl_refs:
  - "{{connection_id}}.stripe_charges"
usage_mode: definition
refs: [amounts-and-currency, test-mode-and-accounts]
meta:
  provenance: human_curated
---

All three revenue metrics read `stripe_charges` and count only charges with `status = 'succeeded'`.
Pending and failed charges are not revenue.

- **`gross_revenue`** is the sum of `amount` of succeeded charges.
- **`refunded_amount`** is the sum of `amount_refunded` of succeeded charges.
- **`net_revenue`** is gross minus refunded, per charge.
- **`refund_rate`** is `refunded_amount` divided by `gross_revenue`.

## Refunds are attributed to the charge date

`amount_refunded` sits on the original charge, so a refund is counted on the day the charge was
made, not the day the refund was issued. Net revenue for last month therefore changes when a charge
from last month is refunded next week. This keeps net revenue consistent with gross revenue of the
same period, which a refund-date view would not.

## What is not subtracted

- **Disputes (chargebacks)** are not subtracted. A disputed charge still counts as revenue until it
  is refunded. Use the `disputed` dimension to see how much revenue is under dispute.
- **Stripe fees, taxes and shipping** are not separated. `amount` is what the customer was charged,
  including tax and shipping if your integration adds them to the charge.

## Time axis

`charge_date` is the charge's `created` timestamp converted to UTC. Days therefore start at
midnight UTC and not in your local time zone.

See [[amounts-and-currency]] for units and currencies and [[test-mode-and-accounts]] for which data
is included.
