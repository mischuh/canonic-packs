# canonic-packs

Context packs for [canonic](https://github.com/mischuh/canonic) — versioned, git-distributed
bundles of pre-curated `semantics/`/`contracts/`/`knowledge/` content for known systems (PostHog,
Stripe, HubSpot, …), installed via `canonic pack add <name> --repo <this repo's URL>`.

See each pack's own `README.md` for what it installs and its required params.

## Packs

| pack | variants | status |
| --- | --- | --- |
| [`posthog`](packs/posthog/) | `postgres` | v1 |
| [`stripe`](packs/stripe/) | `postgres` | v1 |

## Contributing a pack

A pack is packaging, not code: every file under `models/`, `metrics/`, `guardrails/`, `knowledge/`
must be a normal, valid canonic semantic source / contract / knowledge page, with `{{param}}`
placeholders for anything that varies per installation. See `packs/posthog/pack.yaml` for the
manifest shape and the `AMENDMENT-context-packs.md` spec in the `canonic` repo for the full mechanism.

## CI

Every PR runs:

- **`ci.yml`** — `canonic pack validate .`, which validates every pack under `packs/*/`: manifest
  schema, `{{param}}`/token consistency, and full semantics/contracts/knowledge validation, with no
  live database connection needed. Run it locally with `uvx --from canonic==0.32.0 canonic pack
  validate .` (or `uvx canonic pack validate .` for the latest release).
- **`commitlint.yml`** / **`pr-title-lint.yml`** — commit messages and the PR title (used as the
  squash-merge commit message) must follow [Conventional Commits](https://www.conventionalcommits.org/).
- **`pack-version-guard.yml`** — if a PR changes any file under a pack's directory, that pack's
  `pack.yaml` `version:` must be bumped in the same PR (AMENDMENT-context-packs §2.3: a version
  bump is what makes a reinstall a reviewable diff instead of a silent content change).
