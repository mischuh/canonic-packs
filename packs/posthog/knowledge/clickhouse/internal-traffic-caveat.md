---
summary: "What to know before trusting a number from PostHog's ClickHouse tables: one team only, internal traffic, duplicate events and a schema PostHog does not promise to keep."
tags: [posthog, caveat, clickhouse]
sl_refs:
  - "{{connection_id}}.ph_events"
usage_mode: caveat
meta:
  provenance: human_curated
---

Five things to know about these numbers before trusting them at face value.

## One team per query

A PostHog ClickHouse database holds the events of every project in the instance. Each project is a
`team_id`. The `posthog-team-scope` guardrail keeps every query to the team you chose during
install, so the numbers describe one project and not the sum of all of them. If you edit or remove
the guardrail, metrics add up every project.

## Internal and team traffic is not excluded by default

Every metric on `ph_events` is inflated by your own team's usage until the
`posthog-exclude-internal-traffic` guardrail's filter matches your company's email domain or
domains. They are set during install and can be edited afterwards in
`contracts/guardrails/exclude-internal-traffic.yaml`. The filter reads the email from the
`person_properties` of each event. The guardrail ships at `severity: warn`, so a warning is added to
results and nothing is blocked. Tighten it to `error` once you trust it.

## Duplicate events are possible

The events table is a ReplacingMergeTree keyed on the event, and ClickHouse removes duplicates only
when it merges parts, which is not guaranteed to have happened. PostHog's own queries do not
deduplicate either. The metrics in this pack count distinct users, which duplicates do not change.
`event_count` counts rows, so it can be slightly too high for recent data.

## Missing properties are empty strings

The property dimensions (`current_url`, `session_id`, `geoip_country_code`) read keys out of the
JSON text in `properties`. ClickHouse returns an empty string for a key that is not there, so
events without the key are grouped under an empty value and not under `NULL`.

## The schema is not a promise

Unlike the Postgres batch export, PostHog does not publish the ClickHouse tables as a stable
interface. This pack follows the `events` table as it is defined in PostHog's source today. PostHog
has work in progress that changes how `properties` is stored. If a query fails or a property
dimension returns only empty values after a PostHog upgrade, check the column type of `properties` first.

Persons are not modeled. PostHog keeps them in separate ClickHouse tables that need explicit
deduplication, and a semantic source can only point at a table or view. The events table carries
`person_id` and `person_properties` as they were when the event was recorded.

See [[activation-definition]] for how events feed the activation metrics.
