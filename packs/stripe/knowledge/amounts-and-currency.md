---
summary: "Stripe stores money as integers in the currency's smallest unit, and revenue here is reported in one currency chosen at install."
tags: [stripe, amounts, currency, caveat]
sl_refs:
  - "{{connection_id}}.stripe_charges"
usage_mode: caveat
refs: [revenue-definitions]
meta:
  provenance: human_curated
---

Every money column in the Stripe tables (`amount`, `amount_refunded`) is a `bigint` in the
currency's **smallest unit**. 1000 means 10.00 USD or 10.00 EUR, but 1000 JPY means 1000 yen,
because JPY has no minor unit. The measures in this pack divide by the `minor_unit_divisor`
chosen at install, 100 by default.

## One currency per answer

Charges in different currencies are never added together. The
`stripe-single-currency-charges` guardrail filters `stripe_charges` to the currency picked at
install, so a revenue number is always in that currency. Stripe stores currency codes in lowercase
(`usd`, `eur`).

If you sell in several currencies, either install the pack once per currency or group by the
`currency` dimension and treat each row as its own number. This pack does not convert currencies,
since the exchange rate Stripe used is not in these tables.

If the chosen currency has a different minor unit than 100, set `minor_unit_divisor` in the
installed measures. See [[revenue-definitions]] for which charges the revenue metrics count.
