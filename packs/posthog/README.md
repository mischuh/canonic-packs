# PostHog context pack

Curated `semantics/`, `contracts/`, and `knowledge/` content for [PostHog](https://posthog.com)
product analytics, installed once via `canonic pack add posthog` (or the `canonic setup` wizard's
pack branch) and then edited like any other accepted project context. It does not bypass review — it
starts the project with `provenance: human_curated` content instead of `inferred` content, so the
first review is "does this match my instance," not "is this a sane measure at all."

See `AMENDMENT-context-packs.md` in the `canonic` repo for the full mechanism spec this pack
implements against.

## Variants

| id | label | connector | source |
| --- | --- | --- | --- |
| `postgres` | PostHog Postgres batch export | `postgres` | [PostHog's documented Postgres batch export schema](https://posthog.com/docs/cdp/batch-exports/postgres) |

## What this installs

- `semantics/<connection_id>/ph_events.yaml`, `ph_persons.yaml` — one row per event / one row per
  `(team_id, distinct_id)`, joined many-to-one.
- `ph_events` also exposes three keys of its `properties` column as dimensions: `current_url`,
  `session_id` and `geoip_country_code`. They are `json_path` dimensions, so the pack needs canonic
  0.32.0 or newer (`min_canonic_version`). A row without the key groups under `NULL`.
- `contracts/metrics/{active_users,new_users,activated_users,activation_rate}.yaml` — DAU/WAU/MAU are
  one `active_users` metric queried at different time granularities, not three separate bindings.
- `contracts/guardrails/exclude-internal-traffic.yaml` — a `mandatory_filter` on `ph_events`,
  `severity: warn` by default, built from a plain company-email-domain answer during install.
- `knowledge/global/activation-definition.md`, `internal-traffic-caveat.md` — linked to the semantic
  entities above via `sl_refs`, so drift detection flags them if the underlying definition changes.

## Required params

| param | required | notes |
| --- | --- | --- |
| `connection_id` | yes | existing `canonic.yaml` connection, bound automatically by the wizard |
| `signup_event` | yes | picked from a live top-50 custom-event query, or typed |
| `activation_event` | yes | same picker as `signup_event` |
| `internal_email_domains` | no | comma-separated; derives `internal_user_filter` |
| `schema` | no | default `posthog_exports` |
| `events_table` / `persons_table` | no | default `events` / `persons` |

## Not in v1 (see the open questions in the amendment for the full list)

- Further JSON-derived dimensions (`$pathname`, `$browser`, `$referring_domain`, and any custom event
  property) and anything inside `person_properties`. Each is one more `json_path` entry in
  `models/events.yaml`.
- A sessions model — PostHog's sessions batch export has no fixed, documented column list.
- Retention (cohort week-over-week) — not expressible as a single metric binding; likely a curated
  report, not a `contracts/metrics/` binding.
- A generic multi-step funnel primitive — `activation_rate` is a concrete two-event instance; a
  general funnel primitive is a compiler-level question.
- BigQuery/Snowflake variants of this same `models/` content.
