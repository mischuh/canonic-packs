# canonic-packs

Context packs for [canonic](https://github.com/mischuh/canonic) — versioned, git-distributed
bundles of pre-curated `semantics/`/`contracts/`/`knowledge/` content for known systems (PostHog,
Stripe, HubSpot, …), installed via `canonic pack add <name> --repo <this repo's URL>`.

See each pack's own `README.md` for what it installs and its required params.

## Packs

| pack | variants | status |
| --- | --- | --- |
| [`posthog`](packs/posthog/) | `postgres` | v1 |

## Contributing a pack

A pack is packaging, not code: every file under `models/`, `metrics/`, `guardrails/`, `knowledge/`
must be a normal, valid canonic semantic source / contract / knowledge page, with `{{param}}`
placeholders for anything that varies per installation. See `packs/posthog/pack.yaml` for the
manifest shape and the `AMENDMENT-context-packs.md` spec in the `canonic` repo for the full mechanism.
