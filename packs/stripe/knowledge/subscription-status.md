---
summary: "What the subscription metrics count by Stripe status, and what active, trialing and canceled mean here."
tags: [stripe, subscriptions, definitions]
sl_refs:
  - "{{connection_id}}.stripe_subscriptions"
usage_mode: definition
refs: [test-mode-and-accounts]
meta:
  provenance: human_curated
---

Subscription metrics count rows of `stripe_subscriptions` by their current Stripe `status`.

- **`active_subscriptions`** counts `active` and `past_due`. A `past_due` subscription failed its
  latest payment but is still retried by Stripe and has not been canceled, so it is still a customer.
- **`trialing_subscriptions`** counts `trialing`. Trials are not part of active subscriptions.
- **`canceled_subscriptions`** counts `canceled`, grouped by the `canceled_date` dimension.
- **`new_subscriptions`** counts every subscription by `subscription_start_date`, whatever its
  status today.

`incomplete`, `incomplete_expired`, `unpaid` and `paused` are in none of these metrics.

## These are current-state numbers

The table holds each subscription's latest status only. `active_subscriptions` is how many are
active **now**, not how many were active in a past month. Asking for it by month does not give a
history. A history of active subscriptions needs snapshots, which this version does not provide.

`canceled_subscriptions` by `canceled_date` is a real time series, because `canceled_at` is
recorded once. A subscription that is set to cancel at period end keeps its status `active` until
that date, see the `cancel_at_period_end` dimension.

## Money is not modeled

MRR is not in this version. Subscription line items are stored in a JSON column, and the billing
interval and price are in JSON on the price object.
