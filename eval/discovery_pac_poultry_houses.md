# Discovery: Poultry Houses (`pac_poultry_houses`)

## Headline

**560 in-market companies**: 402 customer, 46 both, 24 competitor, 87 neither, 1 role errors.

That is **8.9x** the 63 in-market companies on the seed list. 497 of them are not on the seed list at all.

## By source

| Source | Candidates | In market | Customer | Both | Competitor | Neither | Only this source |
|---|---|---|---|---|---|---|---|
| seed | 919 | 68 | 49 | 11 | 4 | 3 | 3 |
| model | 21 | 4 | 2 | 1 | 0 | 1 | 0 |
| web | 5151 | 271 | 194 | 29 | 20 | 28 | 73 |
| maps | 5779 | 128 | 87 | 16 | 5 | 20 | 4 |
| lists | 2723 | 241 | 165 | 32 | 7 | 37 | 95 |
| nearby | 3834 | 257 | 204 | 22 | 3 | 28 | 55 |
| snowball | 1168 | 140 | 87 | 20 | 12 | 21 | 43 |
| probe | 381 | 37 | 29 | 5 | 1 | 2 | 7 |

## Rounds (saturation curve)

| Round | Queries run | Snowballed | Leads | New candidates | New in market | % of list | Cost | Minutes |
|---|---|---|---|---|---|---|---|---|
| 1 | 2736 | 0 | 28607 | 10344 | 364 | 100% | $7.42 | 27 |
| 2 | 445 | 63 | 1200 | 94 | 5 | 1% | $0.09 | 5 |
| 3 | 3036 | 306 | 30651 | 5948 | 184 | 33% | $8.08 | 15 |

Last round added 33% new in-market companies (stop rule: under 2%).

## Paging depth

4366 queries ran. Deepest page reached per query: page 1: 2960, page 2: 1406.
 27 queries still have a productive next page.

- `web: poultry house construction company`: 2 pages
- `web: poultry house construction company in Alabama`: 2 pages
- `web: poultry house construction company in Arizona`: 2 pages
- `web: poultry house construction company in Arkansas`: 2 pages
- `web: poultry house construction company in California`: 2 pages
- `web: poultry house construction company in Colorado`: 2 pages
- `web: poultry house construction company in Connecticut`: 2 pages
- `web: poultry house construction company in Delaware`: 2 pages
- `web: poultry house construction company in Florida`: 2 pages
- `web: poultry house construction company in Georgia`: 2 pages

Towns searched with nearby queries: 163.

## Source overlap and market size

- In-market companies found by two or more sources (not counting the seed list): 271 of 560 (48%).
- Maps (map search, including nearby map searches) found 177; everything else found 533; both found 150.
- Capture-recapture estimate of the reachable market: about 629 in-market companies (we have 560).

## By state

Location known for 272 of 560 in-market companies. Outside the search locations (shown, not filtered): 42. Likely outside the US by location or country domain (marked in the leads sheet, not filtered): 119.

PA 24, AR 21, GA 19, ON 16, IA 13, AL 12, IN 12, MB 12, MO 11, MN 10, NE 10, TX 10, NC 9, CA 8, BC 7, DE 7, MI 7, OH 7, SD 6, FL 5, VA 5, WI 5, MS 4, KY 3, NJ 3, OK 3, AB 2, CO 2, KS 2, MD 2, SC 2, SK 2, AZ 1, CT 1, IL 1, LA 1, ME 1, ND 1, NS 1, NY 1, OR 1, QC 1, QT 1

## Leads dropped: no website found

4447 names from lists, maps, or the model had no website or social page in one search. Examples: A Grumpy Buck Hunting Blinds; Hometown Poultry Supply, Inc.; BrightWill Home Improvement LLC; 🐔 Poultry Farm Construction: Where Do You Start? ...; Large chicken coop builders in Rio Rico, AZ for high ...; Commercial chicken house builders in central Arkansas?; 1921 Windsweep Farm advertisement in Redding, ...; Custom steel poultry housing solutions; How to Construct a Poultry House Commercial chicken farming ...; Storey Poultry Farm Barn in Meridian, Idaho, and its History; What are recommendations for custom chicken coop ...; Best company for livestock building in NW Iowa?; EGG-CITING NEWS FROM SHED GAL KENTUCKY! Need a ...; Chicken house construction services available; Genesis Poultry House Ltd constructs chicken houses; Turn-key 4 house broiler farm with residence in North ...; Belfast , Maine…old chicken processing barns; Who can finish the construction of a chicken coop in Perry ...; Branch County Welcomes Massive Egg-Laying Barns ...; Hardy Farm in Chester, New Hampshire history; Poultry house construction in Toms River, NJ; Handyman needed for chicken coop project in Clovis, NM; Construction Help Needed for Cattle Buildings in North ...; Northeast Oklahoma builders using reclaimed chicken ...; Who can build a chicken coop in Lorane, Oregon?; Poultry House Construction and Management Techniques ...; We built best poultry, piggery ,farm houses etc . Contuct us ...; Backyard chicken coop builders in Texas?; Is there a carpenter who can build a chicken coop in Kent ...; post frame construction and barn restoration services in ....

## Left to do

Queries with a next page due: 27. In-market companies not yet snowballed: 191. Candidates not yet classified (or errors): 0.

## Runs

| Command | Sources | Searches | LLM calls | Classified | Cost | Minutes | Stopped early |
|---|---|---|---|---|---|---|---|
| discover | lists, maps, model, nearby, seed, snowball, web | 6105 | 3648 | 19868 | $7.52 | 32.1 | no |
| discover | lists, maps, model, nearby, seed, snowball, web | 16568 | 3591 | 10048 | $22.43 | 36.0 | budget |
| probe | lists, maps, model, nearby, seed, snowball, web | 2767 | 31 | 2438 | $3.86 | 10.6 | no |

Total candidates: 16584. Verdicts: out 14098, unknown 1926, in 560.
