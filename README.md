# oep.signal.core

SIGNAL (Sales Intelligence Graph for Networked Accounts and Leads) is a market intelligence platform for Ozark ESOP Partners (OEP) and its companies, WinTech and Pocahontas Aluminum. It finds the companies in a target market, classifies each one's role there (makes the end product, makes or resells doors and windows for it, resells other supplies for it, ...), and exports them for the CRM to drive lead generation.

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

## Usage (stage 2: role in the market, M4)

For companies the market screen marks `in`, a second stage answers five yes/no questions with an evidence URL for each yes (makes the end product, makes components like ours for it, resells others' components, resells other supplies, resells the finished end product). The company's role is the first that applies, in this order: Manufacturer, Component Manufacturer, Component Reseller, Supply Reseller, Reseller, else Adjacent. Lead roles are Manufacturer, Component Reseller, and Supply Reseller. Stage 2 also gives the company's proper name and a short comment for sales. `signal classify` stays stage 1 only.

```
uv run signal role https://www.hogslat.com --market pac_poultry_houses   # both stages, one company
uv run signal role --all --market pac_poultry_houses                     # both stages, whole list -> eval/roles_<market>.csv
uv run signal review --roles --market pac_poultry_houses pac_hunting_blinds   # reference set + discovered companies for rare roles -> eval/review_roles_<market>.csv (run signal export first)
uv run signal freeze --roles --market pac_poultry_houses                 # reviewed sheet -> data/reference_roles.json
uv run signal eval --roles --market pac_poultry_houses                   # lead recall and precision, exact role accuracy -> eval/results_roles_<market>.md
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
uv run signal report --market pac_hunting_blinds              # rewrite the discovery report and leads sheet from stored state (no searching)
uv run signal discover --market pac_hunting_blinds --recheck --rounds 0   # after a stage-1 prompt change: classify the in-market companies again (roles from an older stage-2 prompt are redone by every run)
uv run signal review --discovered --market pac_hunting_blinds # spot-check sheet -> eval/review_discovery_<market>.csv
uv run signal freeze --discovered --market pac_hunting_blinds # -> data/reference_discovery.json
uv run signal eval --discovered --market pac_hunting_blinds   # spot-check precision -> eval/results_discovery_<market>.md
```

`eval/leads_<market>.csv` lists every in-market company with its role, activities, evidence, location, and how it was found; the file for sales is the CRM export below. A run stops starting new work at `--max-cost` (default $30) and says so in its report; running it again continues where it stopped. Classified companies are stored, so a re-run only classifies new ones.

## Usage (M4: CRM export)

`signal export` turns a market's discovery run into the CRM import file. It gives every in-market company a role from the current stage-2 prompt, looks up its primary address and main phone with one Google Maps search (Serper places), drops companies whose listing is outside the market's geography, and merges duplicates (the same phone number or homepage, typically a Facebook page and a website).

```
uv run signal export --market pac_poultry_houses pac_hunting_blinds   # -> exports/crm_<market>.csv, eval/leads_<market>.csv, eval/export_<market>.md
uv run signal eval --contacts --market pac_poultry_houses             # after filling eval/review_contacts_<market>.csv -> eval/results_contacts_<market>.md
```

The CRM file's columns are Company, Homepage, Target, Division, Role, Street address, City, State, ZIP, Phone, Comments, and Lead Source. Target and Division come from the brief (`crm_target`, `crm_market`). A field with no matching map listing stays blank. `eval/leads_<market>.csv` is the internal sheet with every activity, evidence URL, and source. Roles and map lookups are cached, so exporting again costs nothing unless the stage-2 prompt or brief changed.

Fetched pages and search results are cached in `.cache/` (git-ignored), so re-running after a brief or prompt change only costs the LLM calls. Delete `.cache/` to refetch.

A market is defined entirely by its brief in `markets/`; the screening rule and prompt are in `prompts/screen_market.md`. Adding a market means adding a brief, not changing code.
