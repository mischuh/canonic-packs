---
summary: "Why activation is one named event, not a multi-step funnel, in this pack's v1."
tags: [posthog, activation, definitions]
sl_refs:
  - "{{connection_id}}.ph_events"
refs: [internal-traffic-caveat]
usage_mode: definition
meta:
  provenance: human_curated
---

**Activation** in this pack is a single named event — whichever event you picked as
`activation_event` during install — not a multi-step funnel.

## Why one event, not a funnel

Most products can name one event that reliably marks "this user got real value," even when the
underlying journey has several steps (signed up → connected a data source → ran a query, say).
Picking that one event as the activation signal is a deliberate simplification: it is expressible
today as a single `distinct_count` metric with a `population_filter`
(see `contracts/metrics/activated_users.yaml`), which the compiler can compile, serve, and guard
like any other metric.

A generic multi-step funnel primitive (arbitrary N events, arbitrary order, arbitrary windows) is a
compiler-level feature, not something a context pack can approximate with today's metric kinds — see
the pack's `README.md` for the open-questions list. If your activation event genuinely needs to be a
funnel, treat `activated_users` as the closest single-event proxy and expect to replace it once a
funnel primitive ships.

## What this feeds

- `activated_users` — distinct users who fired the activation event.
- `activation_rate` — `activated_users / new_users`, `on_zero_denominator: null` (no signups yet →
  no rate, not a false zero).

## Internal traffic

These numbers are inflated by team/internal usage unless filtered — see
[[internal-traffic-caveat]].
