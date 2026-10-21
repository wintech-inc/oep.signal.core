# Discovery: Poultry Houses (`pac_poultry_houses`)

**This run stopped on its budget ($22) before finishing.** Work still due is listed under 'Left to do'; run `signal discover` again to continue.

## Headline

**387 in-market companies**: 280 customer, 34 both, 19 competitor, 53 neither, 1 role errors.

That is **6.1x** the 63 in-market companies on the seed list. 324 of them are not on the seed list at all.

## By source

| Source | Candidates | In market | Customer | Both | Competitor | Neither | Only this source |
|---|---|---|---|---|---|---|---|
| seed | 919 | 68 | 49 | 11 | 4 | 3 | 3 |
| model | 21 | 4 | 2 | 1 | 0 | 1 | 0 |
| web | 5151 | 233 | 168 | 24 | 17 | 24 | 48 |
| maps | 5779 | 122 | 87 | 16 | 5 | 14 | 3 |
| lists | 2723 | 215 | 149 | 29 | 7 | 30 | 73 |
| nearby | 3834 | 186 | 147 | 19 | 3 | 17 | 0 |
| snowball | 1168 | 95 | 57 | 16 | 10 | 12 | 2 |

## Rounds (saturation curve)

| Round | Queries run | Snowballed | Leads | New candidates | New in market | % of list | Cost | Minutes |
|---|---|---|---|---|---|---|---|---|
| 1 | 2736 | 0 | 28607 | 10344 | 364 | 100% | $7.42 | 27 |
| 2 | 445 | 63 | 1200 | 94 | 5 | 1% | $0.09 | 5 |
| 3 | 3036 | 306 | 30651 | 5948 | 18 | 5% | $8.08 | 15 |

**5424 candidates are not classified yet**, so the last round's count is incomplete and says nothing about saturation.

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

- In-market companies found by two or more sources (not counting the seed list): 249 of 387 (64%).
- Maps (map search, including nearby map searches) found 148; everything else found 379; both found 140.
- Capture-recapture estimate of the reachable market: about 401 in-market companies (we have 387).

## By state

Location known for 200 of 387 in-market companies. Outside the search locations (shown, not filtered): 20.

PA 18, AR 15, GA 13, IA 10, ON 10, IN 9, NC 9, AL 8, MN 8, NE 8, DE 7, MO 7, MI 6, OH 6, SD 6, TX 6, CA 5, FL 5, MB 5, WI 5, VA 4, KY 3, MS 3, NJ 3, OK 3, BC 2, CO 2, AB 1, AZ 1, CT 1, IL 1, KS 1, LA 1, MD 1, ME 1, ND 1, NY 1, OR 1, QC 1, SC 1, SK 1

## Leads dropped: no website found

4406 names from lists, maps, or the model had no website or social page in one search. Examples: A Grumpy Buck Hunting Blinds; Hometown Poultry Supply, Inc.; BrightWill Home Improvement LLC; 🐔 Poultry Farm Construction: Where Do You Start? ...; Large chicken coop builders in Rio Rico, AZ for high ...; Commercial chicken house builders in central Arkansas?; 1921 Windsweep Farm advertisement in Redding, ...; Custom steel poultry housing solutions; How to Construct a Poultry House Commercial chicken farming ...; Storey Poultry Farm Barn in Meridian, Idaho, and its History; What are recommendations for custom chicken coop ...; Best company for livestock building in NW Iowa?; EGG-CITING NEWS FROM SHED GAL KENTUCKY! Need a ...; Chicken house construction services available; Genesis Poultry House Ltd constructs chicken houses; Turn-key 4 house broiler farm with residence in North ...; Belfast , Maine…old chicken processing barns; Who can finish the construction of a chicken coop in Perry ...; Branch County Welcomes Massive Egg-Laying Barns ...; Hardy Farm in Chester, New Hampshire history; Poultry house construction in Toms River, NJ; Handyman needed for chicken coop project in Clovis, NM; Construction Help Needed for Cattle Buildings in North ...; Northeast Oklahoma builders using reclaimed chicken ...; Who can build a chicken coop in Lorane, Oregon?; Poultry House Construction and Management Techniques ...; We built best poultry, piggery ,farm houses etc . Contuct us ...; Backyard chicken coop builders in Texas?; Is there a carpenter who can build a chicken coop in Kent ...; post frame construction and barn restoration services in ....

## Left to do

Queries with a next page due: 27. In-market companies not yet snowballed: 18. Candidates not yet classified (or errors): 5424.

## Runs

| Command | Sources | Searches | LLM calls | Classified | Cost | Minutes | Stopped early |
|---|---|---|---|---|---|---|---|
| discover | lists, maps, model, nearby, seed, snowball, web | 6105 | 3648 | 19868 | $7.52 | 32.1 | no |
| discover | lists, maps, model, nearby, seed, snowball, web | 16568 | 3591 | 10048 | $22.43 | 36.0 | budget |

Total candidates: 16386. Verdicts: out 9484, None 5424, unknown 1091, in 387.
