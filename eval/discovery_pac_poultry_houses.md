# Discovery: Poultry Houses (`pac_poultry_houses`)

## Headline

**279 in-market companies**: 221 customer, 23 both, 9 competitor, 26 neither.

That is **4.7x** the 59 in-market companies on the seed list. 220 of them are not on the seed list at all.

## By source

| Source | Candidates | In market | Customer | Both | Competitor | Neither | Only this source |
|---|---|---|---|---|---|---|---|
| seed | 919 | 64 | 49 | 13 | 2 | 0 | 2 |
| model | 21 | 3 | 2 | 1 | 0 | 0 | 0 |
| web | 5151 | 189 | 148 | 21 | 8 | 12 | 42 |
| maps | 5779 | 104 | 78 | 18 | 3 | 5 | 2 |
| lists | 2723 | 97 | 68 | 18 | 3 | 8 | 18 |
| nearby | 3834 | 177 | 148 | 17 | 1 | 11 | 26 |
| snowball | 1168 | 45 | 24 | 11 | 6 | 4 | 8 |
| probe | 381 | 25 | 19 | 5 | 0 | 1 | 3 |

## Rounds (saturation curve)

| Round | Queries run | Snowballed | Leads | New candidates | New in market | % of list | Cost | Minutes |
|---|---|---|---|---|---|---|---|---|
| 1 | 2736 | 0 | 28607 | 10344 | 197 | 100% | $7.42 | 27 |
| 2 | 445 | 63 | 1200 | 94 | 2 | 1% | $0.09 | 5 |
| 3 | 3036 | 306 | 30651 | 5948 | 77 | 28% | $8.08 | 15 |

Last round added 28% new in-market companies (stop rule: under 2%).

## Paging depth

4366 queries ran. Deepest page reached per query: page 1: 2960, page 2: 1406.
 127 queries still have a productive next page.

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

- In-market companies found by two or more sources (not counting the seed list): 170 of 279 (61%).
- Maps (map search, including nearby map searches) found 128; everything else found 266; both found 115.
- Capture-recapture estimate of the reachable market: about 296 in-market companies (we have 279).

## By state

Location known for 193 of 279 in-market companies. Candidates out without classifying because they are based outside the market's geography: 119.

PA 22, AR 19, GA 15, AL 12, IN 11, IA 10, MO 10, NE 10, MN 9, NC 8, CA 6, DE 6, OH 6, SD 6, TX 6, VA 5, MI 4, WI 4, MS 3, KS 2, KY 2, MD 2, NJ 2, OK 2, SC 2, AZ 1, CO 1, CT 1, FL 1, IL 1, LA 1, ND 1, NY 1, OR 1

## Leads dropped: no website found

4447 names from lists, maps, or the model had no website or social page in one search. Examples: A Grumpy Buck Hunting Blinds; Hometown Poultry Supply, Inc.; BrightWill Home Improvement LLC; 🐔 Poultry Farm Construction: Where Do You Start? ...; Large chicken coop builders in Rio Rico, AZ for high ...; Commercial chicken house builders in central Arkansas?; 1921 Windsweep Farm advertisement in Redding, ...; Custom steel poultry housing solutions; How to Construct a Poultry House Commercial chicken farming ...; Storey Poultry Farm Barn in Meridian, Idaho, and its History; What are recommendations for custom chicken coop ...; Best company for livestock building in NW Iowa?; EGG-CITING NEWS FROM SHED GAL KENTUCKY! Need a ...; Chicken house construction services available; Genesis Poultry House Ltd constructs chicken houses; Turn-key 4 house broiler farm with residence in North ...; Belfast , Maine…old chicken processing barns; Who can finish the construction of a chicken coop in Perry ...; Branch County Welcomes Massive Egg-Laying Barns ...; Hardy Farm in Chester, New Hampshire history; Poultry house construction in Toms River, NJ; Handyman needed for chicken coop project in Clovis, NM; Construction Help Needed for Cattle Buildings in North ...; Northeast Oklahoma builders using reclaimed chicken ...; Who can build a chicken coop in Lorane, Oregon?; Poultry House Construction and Management Techniques ...; We built best poultry, piggery ,farm houses etc . Contuct us ...; Backyard chicken coop builders in Texas?; Is there a carpenter who can build a chicken coop in Kent ...; post frame construction and barn restoration services in ....

## Left to do

Queries with a next page due: 127. In-market companies not yet snowballed: 80. Candidates not yet classified (or errors): 0.

## Runs

| Command | Sources | Searches | LLM calls | Classified | Cost | Minutes | Stopped early |
|---|---|---|---|---|---|---|---|
| discover | lists, maps, model, nearby, seed, snowball, web | 6105 | 3648 | 19868 | $7.52 | 32.1 | no |
| discover | lists, maps, model, nearby, seed, snowball, web | 16568 | 3591 | 10048 | $22.43 | 36.0 | budget |
| probe | lists, maps, model, nearby, seed, snowball, web | 2767 | 31 | 2438 | $3.86 | 10.6 | no |
| discover | lists, maps, model, nearby, seed, snowball, web | 0 | 0 | 441 | $0.41 | 1.7 | no |

Total candidates: 16584. Verdicts: out 14363, unknown 1942, in 279.
