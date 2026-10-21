# M3: Company discovery

Status: draft for discussion with Tim (M3 planning thread, 2026-10-21). Implementation happens in a separate thread.

Background and definitions: [project_overview.md](../project_overview.md). The classifiers it feeds: [M1_market_classifier.md](M1_market_classifier.md) and [M2_role_classifier.md](M2_role_classifier.md).

## 1. Goal

Find companies to feed the classifiers. Given a market brief, `signal discover` builds a list of candidate companies from every source it can reach, runs both classifier stages on each new candidate, and keeps going until new rounds stop turning up new in-market companies.

> Success means finding all the potential customers and competitors in a market that are reachable through websites, and being able to show that the list is close to complete. A company with no website and no social page at all is not worth including.

The sales team needs leads, a lot of them. Earlier iterations spent hours and hundreds of dollars and came back with five companies, four of them in China, while a single Google search found better results in minutes. M3 is not an engineering exercise. Its job is to find companies, at volume, the plain way a person would (web and map searches, directories, "companies like these"), but across every state, every phrasing, and many pages deep.

`docs/sample_pac_companies.csv` is a small, poor list of the low-hanging fruit. Today it yields 63 in-market companies for poultry houses and 151 for hunting blinds (M2 full run). Re-finding every one of them is the minimum, not the goal: matching that list, even 100% of it, is a failure. Success is measured by how many times larger the discovered list is, backed by evidence that searching more no longer turns up new companies (section 7). PAC serves about 15 markets and WinTech about 5, so the whole process must run from a brief alone, with no per-market work from Tim beyond the brief.

**M1 and M2 do not change.** Discovery calls the existing two-stage classifier as a black box. It doesn't touch `prompts/screen_market.md`, `prompts/classify_role.md`, their code paths, or their reference labels.

**Out of scope for M3:** a database, contact data, UI, filtering by geography, and rendering JavaScript-only pages with a headless browser (section 12).

## 2. Principles for discovery

Earlier iterations failed at search in three ways: discovery died after finding a small handful of companies, so a person with ten minutes and a Google search page beat it; the model invented restrictions (one silently switched to maps-only searching because "the web is too noisy"); and the work moved out of the product into thousands of ad hoc scripts. These rules exist to prevent all three.

1. **Volume first.** The output is a long list of real companies. A short list is a failure to investigate, never a finding about the market, unless the saturation evidence in section 7 says otherwise. Discovery keeps going while any source is still producing new in-market companies.
2. **Search like a person, at scale.** Plain queries in many phrasings ("hunting blind builder", "who makes hunting blinds near dallas", "top hunting blind manufacturers"), on both web search and map search, in every state and around every town where we've found the market. Don't overthink the queries; do run a lot of them.
3. **Go deeper while it pays.** A query that keeps turning up new in-market companies gets its next page of results, and the next, well past the first page. A query that stops producing stops.
4. **Web and maps feed each other.** Maps gives local businesses and their towns; web search, directories, and company websites give names. A name found anywhere is looked up; a town where we found an in-market company is searched again on maps and web (section 3).
5. **Discovery is for recall; the classifiers are for precision.** A noisy source is fine. M1 rejects Amazon, HGTV, and toy makers for about $0.0015 each. Never drop, restrict, or filter a source because it is noisy. Removing or narrowing a source is Tim's decision, made on the per-source numbers in the report, never a silent default.
6. **Every source counts.** Web search, map search, directories and member lists, other companies' websites, and the model's own knowledge are all valid. A source is one function that returns leads, so adding one is cheap.
7. **Everything runs through the CLI.** Discovery is a `signal` command, and every lead list in the repo is the output of a `signal` command. No one-off scripts, in the repo or in a session, that search, extract, filter, or edit leads. If a step needs doing, it becomes part of a command or it is raised with Tim. Every test and eval runs against the CLI.
8. **No market knowledge in code.** Search wording comes from the brief and from a per-market query file that Tim can read and edit (section 4). No domain blocklists, keyword lists, or per-market `if` statements in Python.

## 3. Design

```
signal discover --market <id>
  round 1:  leads = seed list + brief examples + model + web + maps + lists
  each round:
      resolve   leads without a website -> one search, pick the company's own site or social page
      dedupe    by company key (domain, or social page path) against everything already found
      classify  new candidates with both stages (M1, then M2 for in-market companies)
      locate    new in-market companies without a known town -> one map lookup by name
      expand    from what this round found -> leads for the next round:
                  next result page of every query whose last page found a new in-market company
                  nearby searches around each new town with an in-market company
                  snowball through each new in-market company's website
                  model: more companies like the ones found so far
  stop when a round adds less than 2% new in-market companies (or none), or after --rounds (default 10)
```

A **lead** is a company name with an optional URL and location, plus where it was found:

```json
{"name": "Cagle Construction", "url": null, "location": "Cullman, AL",
 "found_by": {"source": "lists", "detail": "https://mspoultry.org/allied-members-list-and-links/"}}
```

A **candidate** is a lead with a website, keyed by `company_key(url)` exactly as in M1. A company found by several sources is one candidate with several `found_by` entries.

### Sources

| Source | What it does |
|---|---|
| `seed` | The existing company list (`data/pac_companies.json`) and the brief's `examples_in`. |
| `model` | Sonnet 5.5, once per round: "here is the market and the in-market companies found so far; list more companies like these that are not on the list, with websites and towns." Round 1 starts from the brief's examples (and the seed list's in-market companies on a full run). This is the "give me 100 more like these" request, made repeatable. Hallucinated names fail to resolve or are classified out. |
| `web` | Serper web search for each company query, nationally and as `<query> in <state>` for each search location. Each result's URL is a candidate. |
| `maps` | Serper places search for each company query near each search location. Each place's website is a candidate; places without one become leads to resolve. Places come with an address, which gives the town. |
| `lists` | Serper web search for each list query (directories, association member lists, dealer and distributor lists, trade show exhibitors, "top 10" and "best of" articles). Each result page goes to the list reader. |
| `nearby` | For each new town with an in-market company, each nearby query on maps and web: `<query> near <town, state>`. Companies cluster (Amish builders in one county, poultry builders around a processing plant), so where we've found one we look for its neighbors. Each town is searched once. |
| `snowball` | For each new in-market company: its homepage, plus up to 3 pages from one site search for list pages (dealers, distributors, partners, members, links), go to the list reader. |

**Paging.** Every web and maps query starts with its first page (10 web results, or the first page of places). If a page produces at least one new in-market company, the query's next page is fetched in the next round, up to page 10. Queries that stop producing stop on their own, so depth goes where the companies are.

**The list reader** is one Haiku 5.5 call per page (or per 40,000-character chunk of a long page, up to 5 chunks). It gets the page text with its links and returns every company the page lists, with the website link and location when the page shows them. It extracts all companies, not only ones that look in-market: judging is M1's job. It also returns up to 5 links on the same site to more of the same list (next page, letter sections, categories), which are read once, one level deep.

**The resolver** handles leads without a website, such as the Mississippi Poultry Association's allied members list, which shows names and logos but no links, or a map place with no website. One Serper search for `"<name>" <location>`, then one small Haiku 5.5 call picks the company's own website or social page from the top results, or none. Leads with no website or social page are dropped and counted in the report.

Search results always give a URL. If that URL is a directory or social site rather than a company, M1 classifies it out once and it is never fetched again. Facebook and Instagram page URLs are candidates in their own right, handled by M1's social-page path.

**Budget guard.** `--max-cost` (default $30) stops starting new work when the run's estimated spend reaches it. The report says plainly that the run stopped on budget and what was left, so a capped run is never mistaken for a finished one.

## 4. Search wording: the query file

All search wording lives in `markets/<market_id>.discovery.json`, one per market:

```json
{
  "company_queries": ["hunting blind manufacturer", "hunting blind builder", "who makes hunting blinds", "deer blind company", "box blind for sale", "..."],
  "nearby_queries": ["hunting blind builder", "deer blind manufacturer", "hunting blinds", "..."],
  "list_queries": ["top hunting blind manufacturers", "best deer blind brands", "hunting blind dealers list", "..."],
  "list_terms": ["dealers", "distributors", "where to buy", "partners", "members", "links", "suppliers"]
}
```

- `company_queries` (about 25) find companies directly, phrased the way a person would type them, covering every rule (A, B, C) in the brief and the common ways people name the end product.
- `nearby_queries` (about 5) are the short, broad ones used around each town.
- `list_queries` (about 20) find pages that list companies.
- `list_terms` build the snowball site search: `site:<domain> (<list_terms OR'ed>)`.

`signal queries --market <id>` writes the first version with one Sonnet 5.5 call from the brief (end product, terms, rules, notes, examples). Tim reviews and edits it like a brief, and it is committed. Discovery reads the file and never rewrites it. Changing what we search for means editing this file, not code. Tim doesn't have to review it before a run.

**Search locations.** The brief's `geography` gains an optional `search_locations` list. Both briefs get the 48 contiguous states. Geography is used only to spread the searches; nothing is filtered by location, and M1 still ignores it. There is no map grid: towns come from where companies are actually found (`nearby`).

## 5. Outputs

- **`data/discovery/<market_id>.json`**: every candidate ever found for the market, with its `found_by` entries, round, location when known, whether it was in the seed list, and both stages' results (the same fields as `eval/roles_<market>.csv`). Also the paging and town state, so a later run continues where the last stopped. This is the market list until there is a database. It is committed, and later runs only classify candidates that aren't in it yet (`--reclassify` redoes them, for example after a brief change).
- **`eval/leads_<market_id>.csv`**: the in-market companies only (seed and discovered), with role, reason, evidence links, location, and how each was found. This is the file sales looks at.
- **`eval/discovery_<market_id>.md`**: the run report (section 7).

The M1 and M2 outputs (`eval/screen_*`, `eval/roles_*`, reference sets) are unchanged.

## 6. Commands

```
uv run signal queries --market pac_hunting_blinds             # first version of markets/pac_hunting_blinds.discovery.json
uv run signal discover --market pac_hunting_blinds            # full run -> data/discovery/, eval/leads_*, eval/discovery_*.md
uv run signal discover --market pac_hunting_blinds --no-seeds # blind run (section 7)
uv run signal discover --market pac_hunting_blinds --sources maps,nearby   # a subset of sources (default: all)
uv run signal probe --market pac_hunting_blinds               # fresh-eyes completeness check (section 7)
uv run signal review --discovered --market pac_hunting_blinds # spot-check sheet -> eval/review_discovery_*.csv
uv run signal freeze --discovered --market pac_hunting_blinds # -> data/reference_discovery.json
uv run signal eval --discovered --market pac_hunting_blinds   # spot-check precision
```

As with M1 and M2, real runs need company websites, Serper, and the Anthropic API, so they happen on Tim's Mac; the cloud container runs the unit tests only.

## 7. Measuring success

Nobody knows how big these markets are, so there is no target count. The evidence that the list is close to complete has to come from the searching itself, automatically, with no per-market work from Tim.

**Headline: how far beyond the seed list.** Every report leads with the number of in-market companies found, by role, as a multiple of the seed list's in-market companies (63 poultry, 151 blinds). This is the number the business cares about.

**Floor: re-find every seed company.** `signal discover --no-seeds` runs every source except the seed list (the brief's examples still count, since they are part of the market definition). It must re-find every company on the seed list that M1 calls `in`. Each miss is listed with a diagnosis (which source should have found it and why it didn't) and fixed at its general cause. Re-finding all of them is the minimum; it says nothing about success.

**Saturation: searching more stops finding new companies.** Three automatic signals, all in the report:

1. **Rounds level off.** New in-market companies per round fall to under 2% of the list.
2. **Fresh-eyes probe.** After a run, `signal probe` asks Sonnet 5.5 for a new set of searches that discovery has never run: different phrasings from the query file, in randomly chosen states, on web and maps, a few pages deep. It runs them, classifies what they find, and reports what share of the in-market companies they turn up were already on the list. This is the "a person tries a different search" check, done by SIGNAL instead of by Tim. Companies the probe finds are then added to the list, so its work is never wasted, and each miss is reported with the search that found it.
3. **Sources agree.** Of the in-market companies, the share found by two or more independent sources (for example maps and a directory, or web and the model). The report also gives the capture-recapture estimate of market size from two independent halves (maps versus everything else): *N ≈ (found by A × found by B) / found by both*. When independent sources keep finding the same companies, we have most of them.

**Run report** (`eval/discovery_<market>.md`), for every run:

- the headline: in-market companies by role, and the multiple of the seed list;
- candidates, in-market companies, and roles found per source, and the in-market companies only that source found (its unique contribution);
- new in-market companies per round (the saturation curve), and how deep the productive queries went;
- source overlap and the market-size estimate;
- in-market companies per state, and how many are outside the contiguous US (shown, not filtered);
- leads dropped because no website was found;
- searches, LLM calls, cost, run time, and whether the run stopped on budget.

**Spot check (once, in M3).** Discovered companies are a different population from the CRM list, so M1's accuracy is checked on them once, for these two markets only. `signal review --discovered` samples, with a fixed seed, 25 discovered companies M1 called `in` and 25 it called `out` or `unknown`. Tim labels them on the review page used for M1 and M2. This validates M1 on the new population; it is not a step future markets need.

**Acceptance targets** per market (may be revisited after the first results):

- the blind run re-finds every in-market company on the seed list, or each miss has a diagnosis and a general fix;
- the discovered in-market list is reported as a multiple of the seed list's (no fixed number, since the market size is unknown, but a small multiple needs the saturation evidence below to back it);
- the last round adds less than 2% new in-market companies;
- the fresh-eyes probe finds at least 95% of its in-market companies already on the list;
- spot check: at least 90% of sampled `in` verdicts are right (missed companies in the `out` sample are reported);
- cost under $30 for a first full run per market plus about $3 for the probe, and under $3 for a re-run with nothing changed;
- a full run takes under two hours on Tim's Mac.

## 8. Rules against complexity

M1's and M2's rules apply unchanged. In addition:

- **One loop, the sources above, four prompts** (`prompts/discovery_queries.md`, `prompts/more_companies.md`, `prompts/read_list.md`, `prompts/resolve_lead.md`). No scoring of leads, ranking of sources, pre-filters before M1, or extra classification stages.
- **No source is restricted or dropped without Tim.** That includes "only maps", "only the first page of results", "skip social pages", and "skip directory sites". No map grids or coordinate sweeps either; locations are states and the towns where companies are found.
- **When coverage falls short**, read the report, the blind-run misses, and the probe misses first. The levers, in order: the query file (more or different phrasings), paging depth and search locations, the list reader prompt, and a new source. Each lever beyond the query file is decided with Tim.
- **When a discovered company is misjudged**, it is an M1 or M2 issue: note it for that stage. Discovery doesn't override verdicts.
- **Tests stay small**: lead parsing, dedupe and merge of `found_by`, query building, the paging rule, and the round stop rule. The real tests are `signal discover`, `signal probe`, and their reports.

## 9. Cost and speed (estimate)

Per market, first full run, with about 25 company queries, 5 nearby queries, 20 list queries, and 48 states:

| Item | Count | Cost |
|---|---|---|
| Web and map searches, first pages | about 2,500 | $2.50 |
| Further pages for productive queries | about 1,500 | $1.50 |
| Nearby searches (about 300 towns) | about 3,000 | $3 |
| List reader calls (list pages and snowball pages) | about 2,000 | $3 |
| Resolving and locating leads | about 1,500 | $2 |
| Snowball site searches | about 500 | $0.50 |
| M1 on new candidates | about 8,000 | $12 |
| M2 on new in-market companies | about 600 | $1 |
| Query file and model source (Sonnet 5.5, once per round) | about 10 calls | $0.50 |
| **Total** | | **about $25** |

The probe adds about $3 per market: about 50 new searches a few pages deep, plus M1 on what they find.

Searches assume about $1 per 1,000 Serper queries, and Haiku 5.5 the M1 plan's $0.10 / $0.50 per million tokens. The candidate count is the big unknown; the report will show the real number, and the budget guard holds the run to $30. Every fetch, search, and LLM answer of the new prompts is cached, and classified candidates are stored, so a re-run with nothing changed costs almost nothing. Time is dominated by M1 on new candidates: about 40 minutes for 8,000 at M1's current pace.

## 10. Repository changes

```
markets/
  pac_poultry_houses.discovery.json   # new: query file (written by `signal queries`; Tim may edit)
  pac_hunting_blinds.discovery.json
  pac_*.json                          # geography.search_locations (48 contiguous states)
  schema.json                         # regenerated
prompts/
  discovery_queries.md                # new: writes the query file from the brief, and the probe's searches
  more_companies.md                   # new: the model source ("more companies like these")
  read_list.md                        # new: list reader
  resolve_lead.md                     # new: pick a lead's website from search results
src/signal_core/
  markets.py                          # Geography.search_locations (optional)
  evidence.py                         # add page text with links, paged web search, Serper places search; M1/M2 functions unchanged
  discover.py                         # new: sources, list reader, resolver, the loop, the probe, the report
  eval.py                             # discovery spot-check sample, sheet, freeze, metrics
  cli.py                              # new `queries`, `discover`, and `probe`; --discovered on review, freeze, eval
data/
  discovery/<market_id>.json          # new: all candidates, verdicts, paging and town state
  reference_discovery.json            # new: spot-check labels
eval/
  leads_<market>.csv, discovery_<market>.md, probe_<market>.md, review_discovery_<market>.csv
tests/                                # a few small unit tests
```

M1's rendered prompt (`system_prompt()` in `classify.py`) and M2's must stay byte-identical after the brief change, as in M2.

## 11. Implementation deliverables

1. `geography.search_locations`, model, schema; both briefs validate; M1 and M2 prompts byte-identical.
2. `signal queries` and both query files. Tim may read and edit them, but the run doesn't wait on him: the generated file is good enough to start.
3. The sources, paging, list reader, resolver, loop, budget guard, and `signal discover` with its outputs and report.
4. `signal probe`.
5. A blind run, a full run, and a probe for both markets on Tim's Mac, with the reports committed.
6. The spot check reviewed with Tim, and a results summary against the targets.
7. README and CLAUDE.md commands updated.

## 12. Noted for later milestones

- **JavaScript dealer locators.** Many equipment makers (feeders, fans, curtains) list their dealers in map widgets that a plain fetch can't read. Those dealers are exactly the poultry supply stores of rule B. If the report shows list pages coming back empty for this reason, a headless browser for the list reader is the next lever, decided with Tim.
- **Local supply stores** (the Overman's Discount Supply case in the M1 plan). Maps search will find many local building-supply stores, and M1 will call most of them out by design. Deciding which of them are worth a call is a later milestone.
- Filtering or ranking leads by geography (`priority_states`).
- A database to hold the market list in place of `data/discovery/`.
