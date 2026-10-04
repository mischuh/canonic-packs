---
summary: "Persons export only includes users with a person profile — anonymous pre-identify users are invisible to ph_persons."
tags: [posthog, persons, caveat]
sl_refs:
  - "{{connection_id}}.ph_events"
  - "{{connection_id}}.ph_persons"
usage_mode: caveat
meta:
  provenance: human_curated
---

Two gaps in what these tables show, both worth knowing before trusting a number at face value.

## Anonymous users are invisible to `ph_persons`

PostHog's Postgres persons export only includes users who have been given a **person profile**
(roughly: identified via `identify()`, an alias, or a group). A visitor who fires events before
`identify()` is called exists in `ph_events` (via `distinct_id`) but has no matching row in
`ph_persons` until they are identified — the `many_to_one` join from `ph_events` to `ph_persons`
simply returns no match for those rows. Any metric that requires the join (a person-property
dimension, `signup_date`) undercounts anonymous activity; metrics defined purely on `ph_events`
(`active_users`, `new_users`, `activated_users`) are unaffected.

## Internal/team traffic is not excluded by default

Every metric on `ph_events` is inflated by your own team's usage until the
`posthog-exclude-internal-traffic` guardrail's filter is tuned to your company's email domain(s) (set
during install, or edit `contracts/guardrails/exclude-internal-traffic.yaml` afterward). The guardrail
ships at `severity: warn`, not `error` — a fresh install often has not validated the filter against
real data yet, so a warning is annotated on results rather than blocking them. Tighten it to `error`
once you trust it.

See [[activation-definition]] for how these tables feed the activation metrics.
