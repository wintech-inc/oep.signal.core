# CLAUDE.md

SIGNAL (Sales Intelligence Graph for Networked Accounts and Leads) is a market intelligence tool for OEP's companies, WinTech and Pocahontas Aluminum (PAC). Read [docs/project_overview.md](docs/project_overview.md) first, then the plan for the current milestone in [docs/milestones/](docs/milestones/).

## How work is organized

- Branch `version-13.0` is the integration branch for iteration 13. Each milestone (M1, M2, ...) ends with a PR into it.
- Each milestone has a written plan in `docs/milestones/`. Implement the plan; if it needs to change, raise it with Tim rather than drifting from it.

## Principles (these matter more than anything else here)

Twelve earlier iterations failed by piling on complexity until the system collapsed. Keep it simple.

- **Big picture first.** Prefer the simplest design that solves the real problem. Don't add stages, fallbacks, or heuristics without a clear, general reason.
- **No market knowledge in code.** Everything about a market lives in its brief (`markets/*.json`). Never add per-company or per-market special cases, keyword lists, or tuned thresholds to code.
- **CRM data is not truth.** `docs/sample_pac_companies.csv` and anything derived from it is a list of names to test against, with unreliable labels. Never tune anything to match them.
- **Don't chase test cases.** When a result looks wrong, check the label first, then the brief's wording, and change the prompt only for a general reason. Accuracy is measured by the eval against the reviewed reference set, not by a growing suite of individual cases.
- **Fast and cheap.** Classification runs at scale; keep cost per company low and say what a change does to cost.

## Commands

```
uv sync                                   # install
uv run pytest                             # small unit tests
uv run signal sanitize docs/sample_pac_companies.csv
uv run signal classify <url> --market <market_id>
uv run signal review --market <market_id>   # sample + screen -> eval/review_<market_id>.csv
uv run signal freeze --market <market_id>   # reviewed sheet -> data/reference_labels.json
uv run signal eval --market <market_id>     # accuracy against the reference set
uv run signal schema                        # after editing the Market model in src/signal_core/markets.py
uv run signal role <url> --market <market_id>         # both stages: market, then customer/competitor role
uv run signal review --roles --market <market_id>     # role reference set -> eval/review_roles_<market_id>.csv
uv run signal freeze --roles --market <market_id>     # -> data/reference_roles.json
uv run signal eval --roles --market <market_id>       # stage-2 accuracy against the role reference set
uv run signal queries --market <market_id>            # first version of markets/<market_id>.discovery.json (search wording)
uv run signal discover --market <market_id>           # discovery (M3) -> data/discovery/, eval/leads_*, eval/discovery_*.md
uv run signal discover --market <market_id> --no-seeds   # blind run: must re-find the seed list's in-market companies
uv run signal probe --market <market_id>              # fresh-eyes completeness check -> eval/probe_<market_id>.md
uv run signal report --market <market_id>             # rewrite discovery report + leads sheet from stored state, no new searches
uv run signal review|freeze|eval --discovered --market <market_id>   # spot check of M1 on discovered companies
```

Discovery (`discover.py`, `prompts/discovery_queries.md`, `more_companies.md`, `read_list.md`, `resolve_lead.md`) calls both classifier stages unchanged. Every lead list comes from a `signal` command: no ad hoc scripts that search, extract, filter, or edit leads. Never restrict or drop a discovery source without Tim.

Stage 1 (M1, `prompts/screen_market.md`) must not change when working on stage 2 (`prompts/classify_role.md`, `role.py`).

Company websites, Serper, and the Anthropic API must be reachable, and keys must be in `.env`. Cloud sessions without that network access can run the unit tests only; run the commands on Tim's machine.

## Secrets

`ANTHROPIC_API_KEY` and `SERPER_API_KEY` live in a local `.env`, which is git-ignored. Never commit `.env` or any key.
