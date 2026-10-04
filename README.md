# canonic-packs

Ready-made context for [canonic](https://github.com/mischuh/canonic), for the systems most teams already run.

If you connect an AI agent to a Stripe export or a PostHog database, it sees tables and columns. It does not know that Stripe stores timestamps as Unix seconds, that amounts are in cents, that test mode charges sit in the same table as real ones, or that a refund belongs to the day of the original charge. Every team that connects one of these systems ends up writing the same definitions and learning the same lessons the hard way.

A pack is that work done once and shared. It is a small, versioned folder with the table definitions, metric definitions, guardrails and plain-language notes for one system. You install it into your canonic project with one command, answer a few questions about your instance, and get your first correct number a minute later.

## What canonic is, in short

canonic is an open context layer for data agents. It sits between your warehouse and whatever asks questions of it, such as an agent, a notebook or a dashboard. You describe what your data means in plain files in your git repository, and canonic compiles every question against those definitions. An agent that asks for "revenue" gets the agreed definition, with the filters that belong to it, and an explanation of how the number was produced.

That context has three parts, all stored as files and reviewed like code.

- **Semantics** describe tables, columns, joins and measures, so a query can be generated safely.
- **Contracts** pin down which definition of a metric is the official one, and which filters must always apply.
- **Knowledge** is prose for humans, covering what a metric means and where it differs from what you may expect.

Writing these for your own data is the core job of canonic. For well-known systems, most of it can be written in advance. That is what this repository holds.

The main project, with installation and a full quickstart, lives at [github.com/mischuh/canonic](https://github.com/mischuh/canonic). The documentation is at [docs.getcanonic.app](https://docs.getcanonic.app).

## Try it

You need canonic installed and a project with a connection to the database that holds the data.

A pack ships one or more variants, and each variant targets one connector type. A variant describes where the data physically lives, because the same system looks different in each place. The SQL expressions in a pack are written in the dialect of the connector, so a variant can bring its own model files, its own picker queries and its own list of required tables. Metrics, guardrails and shared knowledge pages stay the same across variants. canonic only offers connections that match the variant. The `posthog` pack has a `postgres` and a `clickhouse` variant. The `stripe` pack has a `postgres` variant only.

```bash
canonic pack list
canonic pack add stripe
```

canonic fetches this repository, checks that the tables the pack needs exist on your connection, and then asks a few questions. For Stripe it asks which currency you report in, and offers the currencies it finds in your live charges. For PostHog it shows the most frequent custom events from the last 30 days and asks which one means signup and which one means activation. Nothing is written until those checks pass.

The same flow is available inside `canonic setup`, which offers packs when you start a new project.

After the install you have ordinary files in your project.

- `semantics/<connection>/` with the source definitions
- `contracts/metrics/` and `contracts/guardrails/`
- `knowledge/global/` with the explanatory pages

canonic then runs one query right away, the pack's first answer, so you see a real number from your own data. For Stripe that is net revenue over the last 30 days. For PostHog it is active users.

From there you work as you would with any canonic project. Run `canonic review`, read the diff, change what does not match your setup, and commit.

## Available packs

| Pack | System | Variant | What you get |
| --- | --- | --- | --- |
| [`stripe`](packs/stripe/) | Payments, customers, subscriptions, refunds | Stripe Data Pipeline real-time sync to Postgres | Gross, refunded and net revenue, refund rate, new and active subscriptions, live mode and single currency guardrails, four knowledge pages |
| [`posthog`](packs/posthog/) | Product analytics | PostHog Postgres batch export, PostHog ClickHouse database (self-hosted) | Active users, new users, activated users and activation rate, an internal traffic guardrail, knowledge pages, a team scope guardrail on ClickHouse |

Each pack folder has its own README with the exact parameters, the version of canonic it needs, and a list of what it leaves out on purpose. Read that list before you rely on a number. The Stripe pack, for example, does not compute MRR, and says why and what to do instead.

## What a pack changes in your project

A pack is a starting point. It is not a dependency that keeps rewriting your files.

When you install one, canonic substitutes your answers into the templates once, writes the result into your project, and marks every file as `human_curated` together with the pack name, version and variant it came from. After that the files are yours. There is no update command that overwrites them. If a newer pack version appears, you install it again and get a diff in git that you can review like any other change.

Packs contain no code. Every file is a normal canonic source, contract or knowledge page, and nothing in the compiler knows about packs at query time.

This also means a pack can be wrong for your instance. Your Stripe account may use a custom billing flow, or your PostHog events may be named differently than the pack assumes. The first review exists to catch that. The guardrails ship with `severity: warn`, so a result shows a warning when a rule applied, and you can tighten it once you trust the filter.

## Using your own pack repository

The same mechanism works for packs your company keeps private. Point canonic at any git URL or local folder with the same layout.

```bash
canonic pack add stripe --repo /path/to/your/checkout
export CANONIC_PACKS_REPO=git@github.com:your-org/your-packs.git
```

This is also the quickest way to test a change to a pack before you open a pull request.

## Contributing a pack

If you know a system well, you can save everyone else the first week with it. The most useful packs come from people who have already been burned by the gotchas.

A pack lives in `packs/<name>/` and looks like this.

```
packs/stripe/
  pack.yaml        manifest with params, variants and the list of files
  mappings/        one mapping per variant, such as postgres.yaml
  models/          semantic sources, one per table or view, in a folder per variant when they differ
  metrics/         metric contracts
  guardrails/      mandatory filters and similar rules
  knowledge/       pages that explain definitions and caveats
  README.md        what it installs, what it needs, what it leaves out
```

Files under `models/`, `metrics/`, `guardrails/` and `knowledge/` are written exactly like files in a canonic project. Anything that differs per installation, such as a schema name or an event name, becomes a `{{param}}` placeholder that is declared in `pack.yaml`. The [Stripe manifest](packs/stripe/pack.yaml) and the [PostHog manifest](packs/posthog/pack.yaml) are good models to copy from. The full mechanism is described in the [`canonic pack` reference](https://docs.getcanonic.app/cli-reference/pack), and the [PostHog guide](https://docs.getcanonic.app/guides/posthog-context-pack) walks through an install against a seeded database.

When the files differ per variant, a variant lists its own in `pack.yaml` and the pack-wide `provides` lists only what every variant installs. A variant can also replace `required_tables` and params, which is how the `posthog` pack gives the ClickHouse variant its own event picker and filter template. Variant-level content needs canonic 0.33.0, so set `min_canonic_version` accordingly. Older releases cannot read such a manifest, and `canonic pack list` then fails for the whole repo, so a pack that uses it should only be merged once that release is in common use.

Some advice from the packs written so far.

- Use only columns that the vendor documents. If the schema is internal and you read it from the vendor's source, as the `posthog` ClickHouse variant does, say so in the pack README. If a table has no fixed schema, leave it out and say so.
- Put the reasoning into the knowledge pages. A metric definition says what is counted. The page next to it says why, and what the vendor's own dashboard will show instead.
- Write down what the pack does not cover. A short, honest list is more useful than a long claim.
- Prefer a guardrail with `severity: warn` over a silent filter, so the person installing it sees the rule at work.

Before you open a pull request, validate the pack. This needs no database and no canonic project.

```bash
uvx canonic pack validate .
```

## Checks on every pull request

- **Pack validation.** `canonic pack validate .` installs every pack into a temporary directory with placeholder values and runs the normal semantics, contracts and knowledge validation on the result.
- **Version bump.** If a pull request changes any file in a pack, the `version` in that pack's `pack.yaml` has to go up in the same pull request. This is what makes a reinstall a reviewable change.
- **Commit messages and PR title.** Both follow [Conventional Commits](https://www.conventionalcommits.org/). The PR title becomes the squash commit message.

## Questions and requests

If a pack gives you a wrong number, or you want a pack for a system that is not listed, open an issue in this repository. For anything about canonic itself, use the [main project](https://github.com/mischuh/canonic).
