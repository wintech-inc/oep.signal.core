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

Fetched pages and search results are cached in `.cache/` (git-ignored), so re-running after a brief or prompt change only costs the LLM calls. Delete `.cache/` to refetch.

A market is defined entirely by its brief in `markets/`; the screening rule and prompt are in `prompts/screen_market.md`. Adding a market means adding a brief, not changing code.
