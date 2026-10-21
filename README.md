# oep.signal.core

SIGNAL (Sales Intelligence Graph for Networked Accounts and Leads) is a market intelligence platform for Ozark ESOP Partners (OEP) and its companies, WinTech and Pocahontas Aluminum. It finds and classifies the companies in a target market (customers and competitors) to drive lead generation.

- Project background and goals: [docs/project_overview.md](docs/project_overview.md)
- Milestone plans: [docs/milestones/](docs/milestones/)
- Market definitions: [markets/](markets/)

## Setup

Requires [uv](https://docs.astral.sh/uv/) (Python 3.12 is installed by uv). Put the API keys in a local `.env`, which is git-ignored:

```
ANTHROPIC_API_KEY=...
SERPER_API_KEY=...
```

Then `uv sync`.

## Usage (M1: market screening)

```
uv run signal sanitize docs/sample_pac_companies.csv       # CRM export -> data/pac_companies.json + report
uv run signal classify https://ranchkingblinds.com --market pac_hunting_blinds
uv run signal classify --all --market pac_hunting_blinds   # whole list, for information -> eval/screen_<market>.csv
uv run signal review --market pac_poultry_houses pac_hunting_blinds   # sample + screen -> eval/review_<market>.csv
uv run signal freeze --market pac_poultry_houses           # reviewed sheet -> data/reference_labels.json
uv run signal eval --market pac_poultry_houses             # precision, recall, unknown rate, cost -> eval/results_<market>.md
uv run signal schema                                       # regenerate markets/schema.json, validate briefs
uv run pytest
```

## Usage (M2: customer or competitor)

For companies the market screen marks `in`, a second stage decides whether each is a possible customer, a possible competitor, both, or neither, with an evidence URL for each yes. `signal classify` stays stage 1 only.

```
uv run signal role https://www.hogslat.com --market pac_poultry_houses   # both stages, one company
uv run signal role --all --market pac_poultry_houses                     # both stages, whole list -> eval/roles_<market>.csv
uv run signal review --roles --market pac_poultry_houses pac_hunting_blinds   # -> eval/review_roles_<market>.csv
uv run signal freeze --roles --market pac_poultry_houses                 # reviewed sheet -> data/reference_roles.json
uv run signal eval --roles --market pac_poultry_houses                   # customer/competitor recall and precision -> eval/results_roles_<market>.md
```

The role rule and prompt are in `prompts/classify_role.md`; the brief's `examples_in[].role` and `role_notes` feed it.

## Usage (M3: company discovery)

`signal discover` builds the market list from every source it can reach (the seed list, the model's own knowledge, web search, map search, directories and member lists, nearby searches around towns where the market was found, and in-market companies' own dealer and partner pages), runs both classifier stages on each new company, and keeps going until a round adds less than 2% new in-market companies. Search wording lives in `markets/<market>.discovery.json`, which `signal queries` writes from the brief and Tim may edit.

```
uv run signal queries --market pac_hunting_blinds             # first version of markets/pac_hunting_blinds.discovery.json
uv run signal discover --market pac_hunting_blinds            # full run -> data/discovery/<market>.json, eval/leads_<market>.csv, eval/discovery_<market>.md
uv run signal discover --market pac_hunting_blinds --no-seeds # blind run without the seed list -> data/discovery/<market>.blind.json, eval/discovery_<market>.blind.md
uv run signal discover --market pac_hunting_blinds --sources maps,nearby   # a subset of sources (default: all)
uv run signal probe --market pac_hunting_blinds               # fresh-eyes completeness check -> eval/probe_<market>.md
uv run signal review --discovered --market pac_hunting_blinds # spot-check sheet -> eval/review_discovery_<market>.csv
uv run signal freeze --discovered --market pac_hunting_blinds # -> data/reference_discovery.json
uv run signal eval --discovered --market pac_hunting_blinds   # spot-check precision -> eval/results_discovery_<market>.md
```

`eval/leads_<market>.csv` is the list for sales: every in-market company with its role, reason, evidence, location, and how it was found. A run stops starting new work at `--max-cost` (default $30) and says so in its report; running it again continues where it stopped. Classified companies are stored, so a re-run only classifies new ones.

Fetched pages and search results are cached in `.cache/` (git-ignored), so re-running after a brief or prompt change only costs the LLM calls. Delete `.cache/` to refetch.

A market is defined entirely by its brief in `markets/`; the screening rule and prompt are in `prompts/screen_market.md`. Adding a market means adding a brief, not changing code.
