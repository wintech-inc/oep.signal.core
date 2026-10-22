# M3 results: company discovery

Results of the first discovery runs for the two PAC markets, measured against the acceptance targets in [M3_company_discovery.md](../docs/milestones/M3_company_discovery.md) (section 7). The full reports are `eval/discovery_<market>.md` (full run), `eval/discovery_<market>.blind.md` (no seed list), and `eval/probe_<market>.md`. The sales list is `eval/leads_<market>.csv`.

## Headline

| | Hunting blinds | Poultry houses |
|---|---|---|
| In-market companies found | **1,144** | **560** |
| Seed list in-market | 147 | 63 |
| Multiple of the seed list | **7.8x** | **8.9x** (7.0x counting only likely-US companies) |
| Not on the seed list | 997 | 497 |
| Customer or both (sales leads) | 712 (62%) | 448 (80%) |
| Competitor only | 10 | 24 |
| Neither (mostly dealers of finished blinds) | 422 | 87 |
| Likely outside the US (marked, not filtered) | 2 | 119 |
| Capture-recapture estimate of the reachable market | about 1,383 | about 629 |

Both lists are many times the seed list, and neither market is saturated yet (see below).

## Against the targets

| Target | Hunting blinds | Poultry houses | |
|---|---|---|---|
| Blind run re-finds the seed list's in-market companies, or each miss is diagnosed | 137 of 147 (93%) | 59 of 63 (94%) | misses diagnosed below |
| Multiple of the seed list | 7.8x | 8.9x | reported |
| Last round adds under 2% new in-market companies | 38% | 33% | **not met** (stopped on budget) |
| Probe finds at least 95% already on the list | 112 of 116 (97%) | 28 of 37 (76%) | blinds met, poultry **missed** (see below) |
| Spot check: at least 90% of sampled `in` verdicts right | 25 of 25 (100%) | 10 of 25 (40%) | blinds met, poultry **missed**: 13 of the 15 wrong are outside the US |
| Cost under $30 for a first full run plus about $3 for the probe | $46.64 | $33.81 | **not met** |
| Re-run with nothing changed under $3 | not measured | not measured | verdict and search caches make it near zero |
| Full run under two hours | 87 min | 79 min | met |

The blind runs ran with a $7 cap each and stopped on budget with a backlog (5,394 and 2,631 candidates not yet classified), so their floor numbers are a lower bound.

## Floor misses

Blinds (10): Country Tyme Sheds, EZ Hunt & Haul, EZ Hunting Blinds, Homestead Barns, Kendall Cabin Company, Pa Pa Jess, Rustic Timbers, Stansell Field Stand Co., WMD Mfg (its brand site trophyblinds.com was found but not yet classified), Woodsmann Inc.

Poultry (4): DCA Construction (found by the nearby source in the full run), Expi-Door (found as frontlinebldg.com, judged out), Heritage Poultry LLC (Facebook only; its name was found but the one-search resolver did not find the page), Tidwell Construction.

Searching for these by hand finds little: they are small firms with thin web presence, and several only show up when searched by exact name. The blind run was also cut short with a large backlog, so some would likely be found by finishing it. No general fix is proposed beyond finishing the runs.

## Why poultry missed the probe target

Of the 9 in-market companies the probe found that the list lacked, most are not poultry house companies a person would call in-market: a California truss maker, a Missouri metal-building company, a roofing contractor, an insulation retailer, and four overseas product pages (Chinese steel-structure and tunnel-door makers). The probe searched narrow trades ("poultry house roofing contractor in Illinois", "poultry house steel truss builder in California") that the main run didn't, and M1 called these generic suppliers `in` because their pages mention poultry houses. This is an M1 precision question on generic building suppliers, not a gap in discovery's coverage of real poultry house builders and dealers. The spot check will show how common it is.

## Cost and saturation

Total M3 spend was about $94.50: blinds $46.64, poultry $33.81, blind runs $14.07. The plan estimated $25 per market; each market produced two to three times the candidates the estimate assumed (18,164 and 16,584), and every candidate costs one M1 call.

Neither market is saturated. Work still due:

- Blinds: 671 queries with a productive next page, 435 in-market companies not yet snowballed.
- Poultry: 27 queries with a next page, 191 in-market companies not yet snowballed.

Continuing is `signal discover --market <id>` with a budget; the run resumes where it stopped. Reaching the 2% stop rule likely costs $60 to $100 per market in total. Each further round finds fewer new companies per dollar, so whether to spend it is a business call.

## Sources

Every source contributed in-market companies no other source found (the "Only this source" column in each report). Web and nearby (`<query> near <town>`) found the most; lists found the most unique poultry companies (95). The model source ("more companies like these") added little (7 and 4 in-market) at low cost.

## Known weak spots (for later milestones)

- **Non-US companies in poultry.** About 119 of 560 are likely outside the US, mostly Canadian provinces and overseas equipment makers. They are marked in the leads sheet's `outside_us` column and counted in the report, not filtered, per the plan.
- **Same company twice.** A company's Facebook page and its website can appear as two rows.
- **Junk lead names.** Lists and maps return many forum titles ("What's the best box blind for SE Iowa?") that the resolver correctly drops (1,266 and 4,447 dropped names). They cost one search and one small model call each.
- **Generic suppliers called in** (see the poultry probe). An M1 note, not a discovery change.

## Spot check

Tim labeled 25 `in` and 25 `out`/`unknown` discovered companies per market ([blinds](results_discovery_pac_hunting_blinds.md), [poultry](results_discovery_pac_poultry_houses.md)). No in-market company turned up in either `out` sample.

- **Blinds:** all 25 `in` verdicts right.
- **Poultry:** 10 of 25 right. 13 of the 15 wrong ones are outside the contiguous US (Germany, France, India, Greece, Türkiye, Colombia, the UK, Canada). Of the other two, one is a heater maker M1 let in under rule B, and the other is Big Dutchman's Facebook page, judged from a post about another company.

**Geography is not enforced anywhere.** The brief says contiguous US only, but M1 judges the market rule alone, so a German poultry equipment maker is `in`. Discovery then expands from it: in-market companies' towns become `nearby` searches (poultry searched around 17 Canadian towns) and their sites get snowballed. Most foreign poultry companies first came from international list pages (UK and Indian trade-show exhibitor lists, the Canadian Poultry buyers' guide, a by-country company directory). Blinds is a domestic market and barely drifts (2 of 1,144). The `outside_us` marker catches only a country domain or a non-US province, so it undercounts: it flagged 119 poultry companies but only 6 of the 14 foreign ones in the sample. The real share of discovered poultry companies outside the US may be close to half.
