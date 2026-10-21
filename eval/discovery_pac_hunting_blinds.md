# Discovery: Hunting Blinds (`pac_hunting_blinds`)

**This run stopped on its budget ($16) before finishing.** Work still due is listed under 'Left to do'; run `signal discover` again to continue.

## Headline

**1140 in-market companies**: 605 customer, 104 both, 10 competitor, 421 neither.

That is **7.8x** the 147 in-market companies on the seed list. 993 of them are not on the seed list at all.

## By source

| Source | Candidates | In market | Customer | Both | Competitor | Neither | Only this source |
|---|---|---|---|---|---|---|---|
| seed | 917 | 150 | 119 | 19 | 2 | 10 | 11 |
| model | 10 | 7 | 3 | 1 | 0 | 3 | 0 |
| web | 2815 | 696 | 391 | 80 | 8 | 217 | 220 |
| maps | 4324 | 348 | 187 | 35 | 2 | 124 | 34 |
| lists | 4070 | 194 | 96 | 30 | 1 | 67 | 30 |
| nearby | 5807 | 731 | 409 | 69 | 3 | 250 | 209 |
| snowball | 4069 | 193 | 93 | 20 | 3 | 77 | 41 |

## Rounds (saturation curve)

| Round | Queries run | Snowballed | Leads | New candidates | New in market | % of list | Cost | Minutes |
|---|---|---|---|---|---|---|---|---|
| 1 | 2930 | 0 | 29898 | 7459 | 709 | 100% | $14.54 | 24 |
| 2 | 5082 | 709 | 58682 | 10586 | 431 | 38% | $15.52 | 27 |

**1 candidates are not classified yet**, so the last round's count is incomplete and says nothing about saturation.

## Paging depth

5710 queries ran. Deepest page reached per query: page 1: 3408, page 2: 2302.
 671 queries still have a productive next page.

- `web: hunting blind manufacturer`: 2 pages
- `web: hunting blind manufacturer in Alabama`: 2 pages
- `web: hunting blind manufacturer in Arizona`: 2 pages
- `web: hunting blind manufacturer in Arkansas`: 2 pages
- `web: hunting blind manufacturer in California`: 2 pages
- `web: hunting blind manufacturer in Colorado`: 2 pages
- `web: hunting blind manufacturer in Connecticut`: 2 pages
- `web: hunting blind manufacturer in Delaware`: 2 pages
- `web: hunting blind manufacturer in Florida`: 2 pages
- `web: hunting blind manufacturer in Georgia`: 2 pages

Towns searched with nearby queries: 278.

## Source overlap and market size

- In-market companies found by two or more sources (not counting the seed list): 580 of 1140 (51%).
- Maps (map search, including nearby map searches) found 439; everything else found 1029; both found 328.
- Capture-recapture estimate of the reachable market: about 1377 in-market companies (we have 1140).

## By state

Location known for 573 of 1140 in-market companies. Outside the search locations (shown, not filtered): 2.

TX 101, PA 50, WI 34, MI 33, OH 32, MO 26, MN 25, LA 21, KY 20, AL 17, NY 15, AR 14, NC 14, IA 13, MS 13, IL 12, KS 11, GA 10, IN 10, TN 10, FL 9, ND 9, VA 9, NE 7, OK 7, SC 7, ME 5, WV 5, CT 4, NJ 4, MD 3, MT 3, NH 3, CA 2, CO 2, SD 2, VT 2, WA 2, WY 2, MA 1, ON 1, OR 1, QC 1, UT 1

## Leads dropped: no website found

1248 names from lists, maps, or the model had no website or social page in one search. Examples: A Grumpy Buck Hunting Blinds; Hometown Poultry Supply, Inc.; BrightWill Home Improvement LLC; Custom duck blinds in Arkansas; What window blind companies are recommended?; What are favorite extra large web blinds for Central FL?; Custom Outdoors of Georgia; THE ALPHA Crafted with precision, engineered for dominance. ...; Hands down, the best blind for the money! I sell these ...; Where to buy blinds for duck hunting in Indiana?; What's the best box blind for SE Iowa?; Bow or gun blind western ky; Airborne deer blinds from South Louisiana company; World Of Hunting Blinds; Hunting Blinds for sale in Berlin, Maryland; Custom aluminum blinds on eastern shore of Maryland; Who makes deer blinds in Hawks, Michigan?; Best duck blind manufacturer in Nebraska; With so many types of blinds on the market from pop-up ...; Duck blind setup in New Mexico; Best hunting blinds in NC at AYW Outfitters; Another load is on the road! These Five Star Deer Blinds ...; Building a hunting blind in Oklahoma; Durable deer hunting blinds made in the USA starting at ...; Custom deer blind builds in Pickens, SC; From the manufacturing facility, here in Columbia Tennessee to ...; Shadow Hunter Blinds for Tennessee deer hunting season; Who builds hunting blinds in Mill Creek, West Virginia?; ARDuckblinds; The Hunters Blind.

## Left to do

Queries with a next page due: 671. In-market companies not yet snowballed: 431. Candidates not yet classified (or errors): 1.

## Runs

| Command | Sources | Searches | LLM calls | Classified | Cost | Minutes | Stopped early |
|---|---|---|---|---|---|---|---|
| discover | lists, maps, model, nearby, seed, snowball, web | 10268 | 3069 | 7459 | $14.54 | 24.3 | budget |
| discover | lists, maps, model, nearby, seed, snowball, web | 12470 | 8503 | 0 | $15.52 | 27.4 | budget |
| discover | lists, maps, model, nearby, seed, snowball, web | 11394 | 0 | 10586 | $16.03 | 33.5 | budget |

Total candidates: 18045. Verdicts: out 14838, unknown 2066, in 1140, error 1.
