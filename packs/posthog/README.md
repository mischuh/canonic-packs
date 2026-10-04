# PostHog context pack

Curated `semantics/`, `contracts/`, and `knowledge/` content for [PostHog](https://posthog.com)
product analytics, installed once via `canonic pack add posthog` (or the `canonic setup` wizard's
pack branch) and then edited like any other accepted project context. It does not bypass review. It
starts the project with `provenance: human_curated` content instead of `inferred` content, so the
first review is "does this match my instance," not "is this a sane measure at all."

See `AMENDMENT-context-packs.md` and `AMENDMENT-pack-variant-content.md` in the `canonic` specs for
the mechanism this pack implements against.

**Requires canonic 0.33.0 or later.** The two variants install different model files, which needs
variant-level content in `pack.yaml`. An older canonic cannot read this manifest.

## Variants

| id | label | connector | source |
| --- | --- | --- | --- |
| `postgres` | PostHog Postgres batch export | `postgres` | [PostHog's documented Postgres batch export schema](https://posthog.com/docs/cdp/batch-exports/postgres) |
| `clickhouse` | PostHog ClickHouse database (self-hosted) | `clickhouse` | [PostHog's events table definition](https://posthog.com/handbook/engineering/clickhouse/schema/sharded-events) |

The metrics, the internal traffic guardrail and the activation knowledge page are the same in both
variants. The models, the picker queries and the two caveat pages differ, because the SQL dialect
and the source schema differ.

The `clickhouse` variant reads PostHog's own database. PostHog does not publish that schema as a
stable interface, it can change with a PostHog upgrade, and this variant has been written from
PostHog's source and tested against a seeded ClickHouse database, not against a running PostHog
instance. The Postgres variant follows an export schema that PostHog documents.

## What this installs

Both variants:

- `contracts/metrics/{active_users,new_users,activated_users,activation_rate}.yaml`. DAU, WAU and MAU
  are one `active_users` metric queried at different time granularities, not three separate
  bindings.
- `contracts/guardrails/exclude-internal-traffic.yaml`, a `mandatory_filter` on `ph_events`,
  `severity: warn` by default, built from a plain company-email-domain answer during install.
- `knowledge/global/activation-definition.md` and `internal-traffic-caveat.md`, linked to the
  semantic entities via `sl_refs`, so drift detection flags them if the underlying definition
  changes. The caveat page is written per variant.
- `ph_events` exposes three keys of its `properties` column as dimensions: `current_url`,
  `session_id` and `geoip_country_code`. They are `json_path` dimensions.

`postgres` also installs:

- `semantics/<connection_id>/ph_persons.yaml`, one row per `(team_id, distinct_id)`, joined
  many-to-one from `ph_events`.
- A row without a property key groups under `NULL`.

`clickhouse` also installs:

- `contracts/guardrails/team-scope.yaml`, a `mandatory_filter` on `team_id`. A PostHog ClickHouse
  database holds the events of every project in the instance, so without it every metric adds up all
  projects.
- A row without a property key groups under an empty string, because ClickHouse returns an empty
  string for a missing key.
- `person_id` as a dimension. Persons are not modeled (see below).

## Required params

| param | required | notes |
| --- | --- | --- |
| `connection_id` | yes | existing `canonic.yaml` connection, bound automatically by the wizard |
| `signup_event` | yes | picked from a live top-50 custom-event query, or typed |
| `activation_event` | yes | same picker as `signup_event` |
| `internal_email_domains` | no | comma-separated, derives `internal_user_filter` |
| `events_table` | no | default `events` |
| `schema` | no | `postgres`: default `posthog_exports`. `clickhouse`: the database, default `default` |
| `persons_table` | no | `postgres` only, default `persons` |
| `team_id` | yes | `clickhouse` only, the numeric project id to analyze |

On `clickhouse` the `signup_event` picker lists the events of the chosen `team_id` only.

## Not in v1

- Further JSON-derived dimensions (`$pathname`, `$browser`, `$referring_domain`, and any custom event
  property) and anything inside `person_properties`. Each is one more `json_path` entry in the
  events model of the variant.
- A persons model for `clickhouse`. PostHog keeps persons in the `person` and `person_distinct_id2`
  tables, which are ReplacingMergeTree tables that need `FINAL` or `argMax` to read correctly, and a
  semantic source can only point at a physical table or view. The events table carries `person_id`
  and `person_properties` as they were when the event was recorded.
- A sessions model. PostHog's sessions batch export has no fixed, documented column list.
- Retention (cohort week-over-week). It is not expressible as a single metric binding and is likely
  a curated report, not a `contracts/metrics/` binding.
- A generic multi-step funnel primitive. `activation_rate` is a concrete two-event instance, and a
  general funnel primitive is a compiler-level question.
- Snowflake and BigQuery variants. They need their own models, picker queries and filter template.
