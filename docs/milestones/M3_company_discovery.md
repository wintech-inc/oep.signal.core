# M3: Company discovery

Status: draft for discussion with Tim (M3 planning thread, 2026-10-21). Implementation happens in a separate thread.

Background and definitions: [project_overview.md](../project_overview.md). The classifiers it feeds: [M1_market_classifier.md](M1_market_classifier.md) and [M2_role_classifier.md](M2_role_classifier.md).

## 1. Goal

Find companies to feed the classifiers. Given a market brief, `signal discover` builds a list of candidate companies from every source it can reach, runs both classifier stages on each new candidate, and keeps going until new rounds stop turning up new in-market companies.

> Success means the in-market list is big enough that we are reasonably confident it covers the bulk of the market that is reachable through websites. A company with no website and no social page at all is not worth including.

`docs/sample_pac_companies.csv` is one source among several, not the boundary of the market. Today it yields 63 in-market companies for poultry houses and 151 for hunting blinds (M2 full run). M3 should grow those numbers substantially, and measure how much of the market they cover (section 7).

**M1 and M2 do not change.** Discovery calls the existing two-stage classifier as a black box. It doesn't touch `prompts/screen_market.md`, `prompts/classify_role.md`, their code paths, or their reference labels.

**Out of scope for M3:** a database, contact data, UI, filtering by geography, and rendering JavaScript-only pages with a headless browser (section 10).

## 2. Principles for discovery

Earlier iterations failed at search in two ways: the model invented restrictions (one silently switched to maps-only searching because "the web is too noisy"), and the work moved out of the product into thousands of ad hoc scripts. These rules exist to prevent both.

1. **Discovery is for recall; the classifiers are for precision.** A noisy source is fine. M1 rejects Amazon, HGTV, and toy makers for about $0.0015 each. Never drop, restrict, or filter a source because it is noisy. Removing or narrowing a source is Tim's decision, made on the per-source numbers in the report (section 7), never a silent default.
2. **Every source counts.** Web search, map search, directories and member lists, other companies' websites, and the model's own knowledge are all valid. The design makes adding a source cheap: a source is one function that returns leads.
3. **Everything runs through the CLI.** Discovery is a `signal` command, and every lead list in the repo is the output of a `signal` command. No one-off scripts, in the repo or in a session, that search, extract, filter, or edit leads. If a step needs doing, it becomes part of a command or it is raised with Tim. Every test and eval runs against the CLI.
4. **No market knowledge in code.** Search wording comes from the brief and from a per-market query file that Tim can read and edit (section 4). No domain blocklists, keyword lists, or per-market `if` statements in Python.
5. **Simple loop, measured.** One loop (section 3), five sources, three small prompts. If coverage falls short, the report says which source to improve; levers are decided with Tim (section 8).

## 3. Design

```
signal discover --market <id>
  round 1:  leads = seed list + brief examples + model + web + maps + lists
  each round:
      resolve   leads without a website -> one search, pick the company's own site or social page
      dedupe    by company key (domain, or social page path) against everything already found
      classify  new candidates with both stages (M1, then M2 for in-market companies)
      snowball  read the websites of the new in-market companies for other companies -> leads for the next round
  stop when a round finds no new in-market companies, or after --rounds (default 3)
```

A **lead** is a company name with an optional URL and location, plus where it was found:

```json
{"name": "Cagle Construction", "url": null, "location": "Cullman, AL",
 "found_by": {"source": "lists", "detail": "https://mspoultry.org/allied-members-list-and-links/"}}
```

A **candidate** is a lead with a website, keyed by `company_key(url)` exactly as in M1. A company found by several sources is one candidate with several `found_by` entries.

### Sources

| Source | What it does | Per market, about |
|---|---|---|
| `seed` | The existing company list (`data/pac_companies.json`) and the brief's `examples_in`. | 930 candidates |
| `model` | One Sonnet 5.5 call: "list the companies you know that are in this market, with websites." Hallucinated names fail to resolve or are classified out. | 1 call |
| `web` | Serper web search for each company query, nationally and in each search location. Each result's URL is a candidate. | 1,200 searches |
| `maps` | Serper places search for each company query in each search location. Each place's website is a candidate; places without one become leads to resolve. | 1,200 searches |
| `lists` | Serper web search for each list query (directories, association member lists, dealer and distributor lists, trade show exhibitors, "top 10" articles). Each result page goes to the list reader. | 20 searches, 200 pages |
| `snowball` | For each new in-market company: its homepage, plus up to 3 pages from one site search for list pages (dealers, distributors, partners, members, links), go to the list reader. | 1 search, 4 pages per company |

The **list reader** is one Haiku 5.5 call per page (or per 40,000-character chunk of a long page, up to 5 chunks). It gets the page text with its links and returns every company the page lists, with the website link and location when the page shows them. It extracts all companies, not only ones that look in-market: judging is M1's job. It also returns up to 5 links on the same site to more of the same list (next page, letter sections, categories), which are read once, one level deep.

The **resolver** handles leads without a website, such as the Mississippi Poultry Association's allied members list, which shows names and logos but no links. One Serper search for `"<name>" <location>`, then one small Haiku 5.5 call picks the company's own website or social page from the top results, or none. Leads with no website or social page are dropped and counted in the report.

Search results always give a URL. If that URL is a directory or social site rather than a company, M1 classifies it out once and it is never fetched again. Facebook and Instagram page URLs are candidates in their own right, handled by M1's social-page path.

## 4. Search wording: the query file

All search wording lives in `markets/<market_id>.discovery.json`, one per market:

```json
{
  "company_queries": ["poultry house builder", "poultry house construction", "poultry equipment supply", "poultry house doors", "..."],
  "list_queries": ["poultry association allied members", "poultry equipment dealer locator", "Georgia poultry federation members", "..."],
  "list_terms": ["dealers", "distributors", "where to buy", "partners", "members", "links", "suppliers"]
}
```

- `company_queries` (about 25) find companies directly: builders, manufacturers, suppliers, and dealers, from every rule (A, B, C) in the brief.
- `list_queries` (about 20) find pages that list companies.
- `list_terms` build the snowball site search: `site:<domain> (<list_terms OR'ed>)`.

`signal queries --market <id>` writes the first version with one Sonnet 5.5 call from the brief (end product, terms, rules, notes, examples). Tim reviews and edits it like a brief, and it is committed. Discovery reads the file and never rewrites it. Changing what we search for means editing this file, not code.

**Search locations.** The brief's `geography` gains an optional `search_locations` list. Both briefs get the 48 contiguous states. Web and map company queries run once nationally and once per location (`"<query>" <state>` for web, `location` for places). Geography is used only to spread the searches; nothing is filtered by location, and M1 still ignores it.

## 5. Outputs

- **`data/discovery/<market_id>.json`**: every candidate ever found for the market, with its `found_by` entries, round, whether it was in the seed list, and both stages' results (the same fields as `eval/roles_<market>.csv`). This is the market list until there is a database. It is committed, and later runs only classify candidates that aren't in it yet (`--reclassify` redoes them, for example after a brief change).
- **`eval/leads_<market_id>.csv`**: the in-market companies only (seed and discovered), with role, reason, evidence links, location when known, and how each was found. This is the file sales looks at.
- **`eval/discovery_<market_id>.md`**: the run report (section 7).

The M1 and M2 outputs (`eval/screen_*`, `eval/roles_*`, reference sets) are unchanged.

## 6. Commands

```
uv run signal queries --market pac_poultry_houses             # first version of markets/pac_poultry_houses.discovery.json
uv run signal discover --market pac_poultry_houses            # full run -> data/discovery/, eval/leads_*, eval/discovery_*.md
uv run signal discover --market pac_poultry_houses --no-seeds # blind run for the coverage test (section 7)
uv run signal discover --market pac_poultry_houses --sources lists,snowball   # a subset of sources (default: all)
uv run signal review --discovered --market pac_poultry_houses # spot-check sheet -> eval/review_discovery_*.csv
uv run signal freeze --discovered --market pac_poultry_houses # -> data/reference_discovery.json
uv run signal eval --discovered --market pac_poultry_houses   # spot-check precision
```

As with M1 and M2, real runs need company websites, Serper, and the Anthropic API, so they happen on Tim's Mac; the cloud container runs the unit tests only.

## 7. Measuring coverage

We can't list the whole market to compare against, but we have something almost as good: a list of in-market companies found independently of discovery, namely the seed list.

**Blind test.** `signal discover --no-seeds` runs every source except the seed list (the brief's examples still count, since they are part of the market definition). The report then shows how many of the seed list's in-market companies discovery found on its own:

- of the companies Tim labeled `in` in the M1 reference set (46 poultry, 45 blinds), excluding brief examples;
- of every seed company M1 calls `in` (63 poultry, 151 blinds).

If blind discovery re-finds 85% of the companies we already knew, it is likely finding a similar share of the ones we didn't. The report also gives the standard capture-recapture estimate of market size, *N ≈ (discovered in-market × seed in-market) / overlap*. The seed list leans toward companies PAC already knows, which tend to be the more visible ones, so the estimate is optimistic. It is a guide, not a target.

**Run report** (`eval/discovery_<market>.md`), for every run:

- candidates, in-market companies, and roles found per source, and the in-market companies only that source found (its unique contribution);
- new in-market companies per round (the saturation curve);
- blind-test recall and the market-size estimate (blind runs);
- leads dropped because no website was found;
- searches, LLM calls, cost, and run time.

**Spot check.** Discovered companies are a different population from the CRM list, so M1's accuracy is checked on them once. `signal review --discovered` samples, with a fixed seed, 25 discovered companies M1 called `in` and 25 it called `out` or `unknown`, from candidates not in the seed list. Tim labels them on the review page used for M1 and M2. This is a sanity check on M1 for the new population, not a new regression set.

**Acceptance targets** per market (may be revisited after the first results):

- blind test: discovery re-finds at least 85% of the reference companies Tim labeled `in`;
- the in-market list grows well beyond the seed list's, and the last round adds less than 5% new in-market companies;
- spot check: at least 90% of sampled `in` verdicts are right (missed companies in the `out` sample are reported);
- cost under $30 for a first full run per market, and under $3 for a re-run with nothing changed;
- a full run takes under an hour on Tim's Mac.

## 8. Rules against complexity

M1's and M2's rules apply unchanged. In addition:

- **One loop, the sources above, three prompts** (`prompts/discovery_queries.md`, `prompts/read_list.md`, `prompts/resolve_lead.md`). No scoring of leads, ranking of sources, pre-filters before M1, or extra classification stages.
- **No source is restricted or dropped without Tim.** That includes "only maps", "only the first page of results", "skip social pages", and "skip directory sites".
- **When coverage falls short**, read the report first. The levers, in order: the query file (more or different queries), more results per query or more search locations, a better list reader prompt, and a new source. Each lever beyond the query file is decided with Tim.
- **When a discovered company is misjudged**, it is an M1 or M2 issue: note it for that stage. Discovery doesn't override verdicts.
- **Tests stay small**: lead parsing, dedupe and merge of `found_by`, query building, and the round stop rule. The real test is `signal discover` and its report.

## 9. Cost and speed (estimate)

Per market, first full run, with about 25 company queries, 20 list queries, and 48 locations:

| Item | Count | Cost |
|---|---|---|
| Web and map searches | about 2,500 | $2.50 |
| List reader calls (list pages and snowball pages) | about 2,000 | $3 |
| Resolving leads without a website | about 1,000 | $1.30 |
| Snowball site searches | about 500 | $0.50 |
| M1 on new candidates | about 6,000 | $9 |
| M2 on new in-market companies | about 500 | $0.80 |
| Queries and model source (Sonnet 5.5) | 2 calls | $0.10 |
| **Total** | | **about $17** |

Searches assume about $1 per 1,000 Serper queries, and Haiku 5.5 the M1 plan's $0.10 / $0.50 per million tokens. The candidate count is the big unknown; the report will show the real number. Every fetch, search, and LLM answer of the new prompts is cached, and classified candidates are stored, so a re-run with nothing changed costs almost nothing. Time is dominated by M1 on new candidates: about 30 minutes for 6,000 at M1's current pace.

## 10. Repository changes

```
markets/
  pac_poultry_houses.discovery.json   # new: query file (written by `signal queries`, reviewed by Tim)
  pac_hunting_blinds.discovery.json
  pac_*.json                          # geography.search_locations (48 contiguous states)
  schema.json                         # regenerated
prompts/
  discovery_queries.md                # new: writes the query file from the brief
  read_list.md                        # new: list reader
  resolve_lead.md                     # new: pick a lead's website from search results
src/signal_core/
  markets.py                          # Geography.search_locations (optional)
  evidence.py                         # add page text with links, and Serper places search; M1/M2 functions unchanged
  discover.py                         # new: sources, list reader, resolver, the loop, the report
  eval.py                             # discovery spot-check sample, sheet, freeze, metrics
  cli.py                              # new `queries` and `discover`; --discovered on review, freeze, eval
data/
  discovery/<market_id>.json          # new: all candidates and verdicts
  reference_discovery.json            # new: spot-check labels
eval/
  leads_<market>.csv, discovery_<market>.md, review_discovery_<market>.csv
tests/                                # a few small unit tests
```

M1's rendered prompt (`system_prompt()` in `classify.py`) and M2's must stay byte-identical after the brief change, as in M2.

## 11. Implementation deliverables

1. `geography.search_locations`, model, schema; both briefs validate; M1 and M2 prompts byte-identical.
2. `signal queries` and both query files, reviewed with Tim before the first full run.
3. The sources, list reader, resolver, loop, and `signal discover` with its outputs and report.
4. A blind run and a full run for both markets on Tim's Mac, with the reports committed.
5. The spot check reviewed with Tim, and a results summary against the targets.
6. README and CLAUDE.md commands updated.

## 12. Noted for later milestones

- **JavaScript dealer locators.** Many equipment makers (feeders, fans, curtains) list their dealers in map widgets that a plain fetch can't read. Those dealers are exactly the poultry supply stores of rule B. If the report shows list pages coming back empty for this reason, a headless browser for the list reader is the next lever, decided with Tim.
- **Local supply stores** (the Overman's Discount Supply case in the M1 plan). Maps search will find many local building-supply stores, and M1 will call most of them out by design. Deciding which of them are worth a call is a later milestone.
- Filtering or ranking leads by geography (`priority_states`).
- A database to hold the market list in place of `data/discovery/`.
