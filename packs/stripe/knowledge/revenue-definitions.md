---
summary: "How gross revenue, refunds and net revenue are defined, and which charges and dates they use."
tags: [stripe, revenue, definitions]
sl_refs:
  - "{{connection_id}}.stripe_charges"
  - "{{connection_id}}.stripe_refunds"
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
- **`refunds_issued`** is the sum of `amount` of succeeded refunds, bucketed by the day the refund was
  issued. It reads the `refunds` table, not the charges.

## Refunds are attributed to the charge date

`amount_refunded` sits on the original charge, so a refund is counted on the day the charge was
made, not the day the refund was issued. Net revenue for last month therefore changes when a charge
from last month is refunded next week. This keeps net revenue consistent with gross revenue of the
same period, which a refund-date view would not.

## Which refund metric to use

The refund metrics answer different questions, so two of them can differ for the same period and
both be correct.

| question | metric | refund is counted on |
| --- | --- | --- |
| How much of what we charged in March was refunded? | `refunded_amount`, `refund_rate`, `net_revenue` | the charge date |
| How much money did we refund in March? | `refunds_issued` | the refund date |

A charge from February that is refunded in March is in `refunds_issued` for March and in
`refunded_amount` for February. When you show both for one period, say which is which. Do not
subtract `refunds_issued` from `net_revenue`, that counts the refund twice.

To compare per month, query `gross_revenue` and `refunds_issued` side by side grouped by month.

## Which refunds are included

`refunds_issued` counts succeeded refunds in the chosen currency. The refunds table has no
`livemode` column, so test mode refunds are removed through the refunded charge. A refund with no
charge, which happens when it is linked only to a payment intent, cannot be classified and is
kept. `refunded_amount` never sees such a refund, because it reads `amount_refunded` on charges, so
`refunds_issued` can be higher than `refunded_amount` over the same period for that reason too.

## Why net revenue differs from the Stripe dashboard

`net_revenue` is "charged amount minus refunded amount". It is not Stripe's net volume or your
bookkeeping revenue. These are all outside it:

- Stripe processing fees and other balance transaction fees.
- Disputes and chargebacks.
- Payouts and their timing, which move cash and not revenue.
- Tax and shipping, which are included in the charge `amount` if your integration adds them.

Expect the number to be higher than the dashboard's net volume. Do not use it for reconciliation
against payouts.

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
