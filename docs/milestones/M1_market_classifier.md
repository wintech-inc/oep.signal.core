# M1: Market classifier

Status: agreed with Tim on 2026-10-20 in the M1 planning thread. Implementation happens in a separate thread.

Background and definitions: [project_overview.md](../project_overview.md).

## 1. Goal

Given a company (name and URL) and a market brief, answer one question:

> Does this company participate in this market, **as the brief defines it**?

The answer is `in`, `out`, or `unknown`, with a one-sentence reason and the URL of the evidence used.

M1 is a **fast, cheap first screen**. It picks the companies worth considering for the later customer vs. competitor test, so it favors recall: an extra company costs little, a missed one is a lost lead. Later milestones remove the false positives that get through.

It must be generic: adding a market means adding a brief file, never changing code.

**Out of scope for M1:** customer vs. competitor role, geography (M1 doesn't find companies, so location doesn't matter yet), discovering new companies, contact data, UI, and a database.

## 2. What "in the market" means

PAC and WinTech are component suppliers. They make doors and windows that other companies build into an **end product**. A market is one end product seen from the supplier's side: the companies that could buy our component plus the companies that sell components like ours into it.

The screening rule is the same for every market. It lives once, in the classifier's prompt template (a text file, not code). The `{...}` fields are filled from the brief:

> {supplier} makes {our_products.summary}. These are components that other companies build into {end_product.name}s.
>
> A company is **IN** this market if it does at least one of the following:
>
> - **A. Builds the end product.** It manufactures or builds {end_product.name}s, including contractors that build them on site.
> - **B. Distributes components for it.** It sells components, equipment, or building materials specifically for {end_product.name}s to the companies that build, equip, or maintain them.
> - **C. Makes products like ours for it.** It makes {our_products.category} for {end_product.name}s.
>
> Otherwise the company is **OUT**. In particular, these are OUT unless they also do A, B, or C:
>
> - companies that make *other* products used in or around {end_product.name}s;
> - companies that only own, use, or operate {end_product.name}s;
> - dealers and retailers that resell finished {end_product.name}s to end users;
> - companies in the broader industry that are not tied to {end_product.name}s.
>
> If the evidence doesn't show what the company does, answer **UNKNOWN**. When the evidence is suggestive but not conclusive, lean toward IN.

The prompt then adds the brief's `end_product` description and `not_included` list, `our_products.terms`, `notes`, and `examples_in`, followed by the evidence.

## 3. Market briefs

Briefs live in `markets/<market_id>.json`. The first two, agreed in planning, are:

- [`markets/pac_poultry_houses.json`](../../markets/pac_poultry_houses.json)
- [`markets/pac_hunting_blinds.json`](../../markets/pac_hunting_blinds.json)

The original Markdown briefs stay in `docs/` for reference. The JSON versions replace them as the source of truth.

| Field | Used by the M1 classifier | Purpose |
|---|---|---|
| `id`, `name`, `supplier` | yes | Identity; `supplier` fills the rule. |
| `end_product.name`, `.description`, `.terms`, `.not_included` | yes | What the end product is and isn't. `terms` also builds the search query. |
| `our_products.summary`, `.category`, `.terms` | yes | What counts as "products like ours" (rule C). |
| `notes` | yes | Short, market-specific clarifications, one sentence each. |
| `examples_in` | yes | Known participants, tagged with the rule (A, B, C) that makes them IN. |
| `pac_products` | no | Kept for later milestones. |
| `geography` | no | Kept for later milestones. |
| `crm_market` | eval only | Maps the CRM's market name to this brief. |

Writing rules for briefs, because a small model reads them:

- one fact per sentence, with no long "unless" chains;
- name the common false positives explicitly in `notes` or `not_included`;
- add a market-specific note only when the shared rule really doesn't cover the case;
- the implementation adds `markets/schema.json` (JSON Schema) and a matching Pydantic model, and every brief must validate.

## 4. Classifier design

```
classify(company, market):
    evidence = homepage_text(company.url) + site_search(company, market)   # cached on disk
    verdict  = one Claude Haiku 5.5 call(rule + brief + evidence)          # structured JSON out
    return verdict   # {verdict: in|out|unknown, rule: A|B|C|null, reason, evidence_url}
```

**Evidence comes from two sources:**

1. **Homepage.** HTTP GET the company URL and extract the title, meta description, and visible text, capped at about 6,000 characters. This answers "what kind of business is this?", which is what catches Amazon, HGTV, retailers, and toy makers.
2. **Site search.** One Serper query per company and market: `site:<domain>` plus the `end_product.terms` and `our_products.terms` OR'ed together. Keep the top 10 titles, snippets, and URLs. Google has indexed the whole site, so this answers "do they do this anywhere?" and catches the shed builder whose deer blinds are on a sub page. For Facebook and Instagram pages, query `"<company name>"` plus the terms instead of `site:`.

**The judge** is one `claude-haiku-5-5` call per company and market, at low effort, using structured output so the JSON always parses.

**`unknown`** means there was no usable evidence (site down, no text, no search hits). It keeps "couldn't see anything" separate from "saw it, and it's not in the market".

**Cache:** every fetch and search result goes to `.cache/` (git-ignored), so re-running after a brief or prompt change costs only the LLM calls.

## 5. Rules against complexity

These exist because earlier iterations collapsed under accumulated special cases.

- **No market knowledge in code.** Everything about a market lives in its brief. No per-company or per-market `if` statements, keyword lists in Python, or hand-tuned score thresholds.
- **CRM labels are not truth.** The CRM export is a list of companies to test against, plus an unreliable hint. Never tune anything to match it.
- **When a verdict looks wrong, fix things in this order:** the reference label (section 7), then the brief's wording, then (only for a general reason) the prompt.
- **No cascades, ensembles, voting, or multi-stage pipelines in M1.** If accuracy falls short, the levers in order are better evidence, then a stronger model (Sonnet 5.5) on only the uncertain cases. Either one is decided with Tim, not added silently.
- **Tests stay small.** Unit tests cover the pure functions (URL normalization, dedupe, brief loading). Accuracy is measured by the eval script against the reference set, not by a growing pytest suite of individual companies.

## 6. Company data

`docs/sample_pac_companies.csv` is a low-quality CRM export (1,083 rows, 71 with no URL, 9 malformed URLs, and 66 domains appearing more than once). A small, re-runnable `sanitize` command turns it into `data/pac_companies.json`, plus `data/pac_companies_sanitize_report.md` listing every row that was dropped or merged and why.

```json
{
  "id": "southernagbuilders.com",
  "name": "Southern Ag Builders & Supply",
  "aliases": ["Southern Ag Builders & Supply LLC"],
  "url": "https://southernagbuilders.com",
  "crm": [{"market": "Poultry", "role": "Customer"}, {"market": "Poultry", "role": "Lead"}]
}
```

Sanitizing rules:

1. Trim whitespace, and add a missing scheme (`www.wickbuildings.com` becomes `https://www.wickbuildings.com`).
2. Drop rows with no URL or a junk URL (`No links found`, `N/A - https://N/A`).
3. Normalize: lowercase the host, strip `www.`, drop the query and fragment. The dedupe key is the domain, except for social hosts (facebook.com, instagram.com), where it's the full page path.
4. Drop URLs whose site doesn't respond (checked once, recorded in the report).
5. Merge duplicates on the key: keep the first name, keep the other names as `aliases`, and keep every (market, role) pair in `crm`.

There is one sanitized output, in JSON. The raw CSV stays unchanged in `docs/`.

## 7. Evaluation

Because the CRM labels can't be trusted, M1 builds a small **reference set** that Tim has reviewed, and measures against that.

1. **Sample.** Using a fixed random seed, draw 100 companies per market from `data/pac_companies.json`: 50 that the CRM tags with that market, and 50 from the rest of the list.
2. **Screen.** Run the classifier on the sample.
3. **Review.** Produce a review sheet (`eval/review_<market>.csv`) with each company's name, URL, verdict, rule, reason, evidence URL, and CRM hint. Tim marks the correct answer for every row. Most rows should be quick confirmations; plan on about an hour for both markets.
4. **Freeze.** Store the reviewed answers in `data/reference_labels.json` (`{company_id, market_id, label, note}`). From then on this is the regression set for every brief or prompt change.

`signal eval --market <id>` reports on the reference set: precision, recall, the `unknown` rate, a confusion matrix, and the disagreements with reasons and evidence links. Running the classifier over the whole company list is also supported, but only for information.

**Acceptance targets** for each market, measured on the reference set (may be revisited after the first results):

- recall of at least 95%;
- precision of at least 90%;
- `unknown` at 5% or less;
- cost under $2 per 1,000 classifications.

## 8. Cost and speed (estimate)

Per company and market: 1 Serper query (about $0.001, depending on plan) plus 1 Haiku 5.5 call of about 3,000 to 4,000 input tokens and 150 output tokens (about $0.0005 at $0.10 / $0.50 per million). The homepage is fetched once per company.

That's about **$1.50 per 1,000 classifications**. Screening the full list (about 1,000 companies) against both markets costs about $3. With 10 to 20 requests in flight, 1,000 classifications take a few minutes.

## 9. Repository layout after M1

```
CLAUDE.md
README.md
pyproject.toml, uv.lock          # uv-managed, Python 3.12
docs/
  project_overview.md
  milestones/M1_market_classifier.md
  sample_*                       # original inputs, unchanged
markets/
  schema.json
  pac_poultry_houses.json
  pac_hunting_blinds.json
prompts/
  screen_market.md               # the screening rule and prompt template
data/
  pac_companies.json
  pac_companies_sanitize_report.md
  reference_labels.json
eval/                            # review sheets and eval outputs
src/signal_core/                 # not "signal": that name clashes with Python's standard library
  markets.py                     # load and validate briefs
  companies.py                   # load companies; sanitize
  evidence.py                    # homepage fetch, Serper search, disk cache
  classify.py                    # prompt and Haiku call
  cli.py                         # signal sanitize | classify | eval
tests/                           # small unit tests only
```

Dependencies: `anthropic`, `httpx`, `pydantic`, `python-dotenv`, `selectolax` (HTML to text), and `pytest` for development. `ANTHROPIC_API_KEY` and `SERPER_API_KEY` come from the local `.env`, which is git-ignored and never committed.

```
uv run signal sanitize docs/sample_pac_companies.csv
uv run signal classify https://ranchkingblinds.com --market pac_hunting_blinds
uv run signal eval --market pac_poultry_houses
```

## 10. Implementation deliverables

1. `uv` project scaffolding, with commands added to `CLAUDE.md` and `README.md`.
2. `markets/schema.json` and validation of both briefs.
3. The `sanitize` command, `data/pac_companies.json`, and the sanitize report.
4. The `prompts/screen_market.md` template and the `classify` command.
5. The `eval` command, the review sheets, the reference set reviewed with Tim, and a results summary against the targets.

## 11. Decisions made in planning

- The brief is the source of truth, not the CRM.
- A market means customers plus competitors for one end product. M1 screens for both together, using rules A, B, and C.
- Poultry growers and integrators are OUT; they are end users.
- "Products like ours" means doors and windows. That includes agricultural doors usable in poultry houses (Plyco) and large equipment makers that also sell poultry house doors (Chore-Time, L.B. White, Double L Group).
- General building-materials distributors are OUT unless they show a poultry or ag program (see section 12).
- Recall is favored over precision, with `unknown` kept separate.
- Geography is ignored in M1.

## 12. Noted for later milestones

- **Local supply stores in the poultry market.** Poultry house construction is ad hoc and decentralized. In rural Arkansas, a farm may hire a local contractor, who buys from whatever local supply store they know. An example is Overman Buildings / Overman's Discount Supply (https://overmanbuildings.com/overmansdiscountsupply/) in Pocahontas, Arkansas. Its website doesn't look like a poultry supplier, but it is exactly the kind of company PAC should approach about carrying its doors and windows. M1 deliberately leaves these OUT (rule B requires a visible poultry or ag program). A later milestone should decide how to find and judge them, probably by location rather than website content.
- The hunting blind market should be easier to map than poultry houses, because blinds are mostly built by established companies rather than ad hoc contractors.
- Customer vs. competitor vs. neither, including the distributor case (a distributor is both).
