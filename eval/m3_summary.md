# M3 results: company discovery

Results of the first discovery runs for the two PAC markets, measured against the acceptance targets in [M3_company_discovery.md](../docs/milestones/M3_company_discovery.md) (section 7). The full reports are `eval/discovery_<market>.md` (full run), `eval/discovery_<market>.blind.md` (no seed list), and `eval/probe_<market>.md`. The sales list is `eval/leads_<market>.csv`.

The numbers below are after the geography fix (2026-10-22, see "Geography" at the end). The spot check showed that most wrong poultry verdicts were companies based abroad, so the brief's geography is now a hard boundary, and the in-market companies of both full runs were classified again under it.

## Headline

| | Hunting blinds | Poultry houses |
|---|---|---|
| In-market companies found | **1,060** (1,144 before the fix) | **279** (560 before the fix) |
| Seed list in-market | 145 | 59 |
| Multiple of the seed list | **7.3x** | **4.7x** |
| Not on the seed list | 915 | 220 |
| Customer or both (sales leads) | 677 (64%) | 244 (87%) |
| Competitor only | 12 | 9 |
| Neither (mostly dealers of finished blinds) | 371 | 26 |
| Capture-recapture estimate of the reachable market | about 1,258 | about 296 |

Both lists are several times the seed list. Poultry's US market is small: the estimate of the reachable market (about 296) is close to what was found. Blinds is not saturated (see below).

## Against the targets

| Target | Hunting blinds | Poultry houses | |
|---|---|---|---|
| Blind run re-finds the seed list's in-market companies, or each miss is diagnosed | 137 of 147 (93%) | 59 of 63 (94%) | misses diagnosed below |
| Multiple of the seed list | 7.3x | 4.7x | reported |
| Last round adds under 2% new in-market companies | 38% | 33% | **not met** (stopped on budget) |
| Probe finds at least 95% already on the list | 112 of 116 (97%) | 28 of 37 (76%) | blinds met, poultry **missed** (see below) |
| Spot check: at least 90% of sampled `in` verdicts right | 24 of 24 (100%) | 9 of 9 (100%) | met after the geography fix (poultry was 9 of 25 before it) |
| Cost under $30 for a first full run plus about $3 for the probe | $46.64 | $33.81 | **not met** |
| Re-run with nothing changed under $3 | not measured | not measured | verdict and search caches make it near zero |
| Full run under two hours | 87 min | 79 min | met |
| M1 eval after the geography change (targets: recall ≥ 95%, precision ≥ 90%) | R100 / P96 | R91 / P100 (93% after relabeling Penner, see below) | blinds met, poultry recall **missed** |

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

- **Same company twice.** A company's Facebook page and its website can appear as two rows.
- **Junk lead names.** Lists and maps return many forum titles ("What's the best box blind for SE Iowa?") that the resolver correctly drops (1,266 and 4,447 dropped names). They cost one search and one small model call each.
- **Generic suppliers called in** (see the poultry probe). An M1 note, not a discovery change.

## Spot check and geography

Tim labeled 25 `in` and 25 `out`/`unknown` discovered companies per market ([blinds](results_discovery_pac_hunting_blinds.md), [poultry](results_discovery_pac_poultry_houses.md)). No in-market company turned up in either `out` sample.

- **Blinds:** all 25 `in` verdicts right.
- **Poultry:** 10 of 25 right. 13 of the 15 wrong ones are outside the contiguous US (Germany, France, India, Greece, Türkiye, Colombia, the UK, Canada). Of the other two, one is a heater maker M1 let in under rule B, and the other is Big Dutchman's Facebook page, judged from a post about another company.

**What the spot check found: geography was not enforced anywhere.** The brief says contiguous US only, but M1 judges the market rule alone, so a German poultry equipment maker is `in`. Discovery then expands from it: in-market companies' towns become `nearby` searches (poultry searched around 17 Canadian towns) and their sites get snowballed. Most foreign poultry companies first came from international list pages (UK and Indian trade-show exhibitor lists, the Canadian Poultry buyers' guide, a by-country company directory). Blinds is a domestic market and barely drifts (2 of 1,144). The `outside_us` marker catches only a country domain or a non-US province, so it undercounts: it flagged 119 poultry companies but only 6 of the 14 foreign ones in the sample. The real share of discovered poultry companies outside the US may be close to half.

**The fix (Tim's rule, 2026-10-22).** The brief's `countries` and `search_locations` (the 48 contiguous states) are a hard boundary; `priority_states` are soft and only steer searching. A candidate known to be based outside the boundary (a state or province code outside it, a country the list reader or model reports, or another country's domain) is out without being classified. M1's market rule now also says a company based outside the geography is OUT, for companies whose location only the evidence shows. Nearby searches and snowballing start only from in-market companies, so they stay inside the boundary.

**Re-check of the full runs** (`signal discover --recheck --rounds 0`, $1.65):

- Poultry: 560 to 279 in-market. The gate removed 119 without a call, and M1 removed 162: about 126 on geography, and about 36 on run-to-run variance in borderline cases (16 of them now `unknown`).
- Blinds: 1,144 to 1,060. The gate removed 2, and M1 removed 82: about 19 on geography, and about 63 on variance in thin-evidence cases (Facebook posts, prefab cabin builders), mostly now `unknown`.
- Spot check rescored on the same labels: poultry 9 of 9 `in` right, and none of the 41 out or unknown is in-market. Blinds 24 of 24 right, and 1 of 26 out or unknown is in-market (East Texas Trailers, which flipped to `out`).

**M1 eval after the change.** Blinds R100 / P96: two companies labeled out came out `in` on thin evidence (Meyer Distributing, TX Duck Blinds), which is run-to-run variance. Poultry R91 / P100. Penner Farm Services (Manitoba and Alberta) is now out on geography, as the rule intends, so its reference label was changed to out; that gives 42 of 45 (93%). The other misses are GPC Poultry Supply & Hardware (a hardware store and lumberyard, borderline, and judged differently between runs before) and Summit Livestock (missed before the change too).

The blind runs were not re-checked, so their reports still include companies based abroad.
