# Discovery: Hunting Blinds (`pac_hunting_blinds`)

## Headline

**1060 in-market companies**: 577 customer, 100 both, 12 competitor, 371 neither.

That is **7.3x** the 145 in-market companies on the seed list. 915 of them are not on the seed list at all.

## By source

| Source | Candidates | In market | Customer | Both | Competitor | Neither | Only this source |
|---|---|---|---|---|---|---|---|
| seed | 917 | 148 | 113 | 22 | 2 | 11 | 10 |
| model | 10 | 7 | 3 | 1 | 0 | 3 | 0 |
| web | 2815 | 659 | 369 | 77 | 10 | 203 | 193 |
| maps | 4324 | 330 | 185 | 35 | 3 | 107 | 28 |
| lists | 4070 | 179 | 92 | 28 | 1 | 58 | 23 |
| nearby | 5807 | 692 | 388 | 68 | 4 | 232 | 192 |
| snowball | 4069 | 178 | 87 | 20 | 3 | 68 | 33 |
| probe | 361 | 114 | 75 | 12 | 1 | 26 | 4 |

## Rounds (saturation curve)

| Round | Queries run | Snowballed | Leads | New candidates | New in market | % of list | Cost | Minutes |
|---|---|---|---|---|---|---|---|---|
| 1 | 2930 | 0 | 29898 | 7459 | 671 | 100% | $14.54 | 24 |
| 2 | 5082 | 709 | 58682 | 10586 | 385 | 36% | $15.52 | 27 |

Last round added 36% new in-market companies (stop rule: under 2%).

## Paging depth

5710 queries ran. Deepest page reached per query: page 1: 3408, page 2: 2302.
 672 queries still have a productive next page.

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

- In-market companies found by two or more sources (not counting the seed list): 565 of 1060 (53%).
- Maps (map search, including nearby map searches) found 416; everything else found 962; both found 318.
- Capture-recapture estimate of the reachable market: about 1258 in-market companies (we have 1060).

## By state

Location known for 651 of 1060 in-market companies. Candidates out without classifying because they are based outside the market's geography: 2.

TX 114, PA 57, WI 42, MI 37, OH 33, MN 31, MO 29, LA 26, KY 25, AL 20, AR 17, MS 16, NC 16, IA 15, TN 15, GA 14, IL 14, NY 14, IN 13, KS 13, FL 12, VA 9, ND 8, NE 8, OK 7, SC 7, WV 5, CA 4, CT 4, MD 4, ME 4, NJ 4, NH 3, MT 2, SD 2, WA 2, CO 1, MA 1, OR 1, VT 1, WY 1

## Leads dropped: no website found

1266 names from lists, maps, or the model had no website or social page in one search. Examples: A Grumpy Buck Hunting Blinds; Hometown Poultry Supply, Inc.; BrightWill Home Improvement LLC; Custom duck blinds in Arkansas; What window blind companies are recommended?; What are favorite extra large web blinds for Central FL?; Custom Outdoors of Georgia; THE ALPHA Crafted with precision, engineered for dominance. ...; Hands down, the best blind for the money! I sell these ...; Where to buy blinds for duck hunting in Indiana?; What's the best box blind for SE Iowa?; Bow or gun blind western ky; Airborne deer blinds from South Louisiana company; World Of Hunting Blinds; Hunting Blinds for sale in Berlin, Maryland; Custom aluminum blinds on eastern shore of Maryland; Who makes deer blinds in Hawks, Michigan?; Best duck blind manufacturer in Nebraska; With so many types of blinds on the market from pop-up ...; Duck blind setup in New Mexico; Best hunting blinds in NC at AYW Outfitters; Another load is on the road! These Five Star Deer Blinds ...; Building a hunting blind in Oklahoma; Durable deer hunting blinds made in the USA starting at ...; Custom deer blind builds in Pickens, SC; From the manufacturing facility, here in Columbia Tennessee to ...; Shadow Hunter Blinds for Tennessee deer hunting season; Who builds hunting blinds in Mill Creek, West Virginia?; ARDuckblinds; The Hunters Blind.

## Left to do

Queries with a next page due: 672. In-market companies not yet snowballed: 389. Candidates not yet classified (or errors): 0.

## Runs

| Command | Sources | Searches | LLM calls | Classified | Cost | Minutes | Stopped early |
|---|---|---|---|---|---|---|---|
| discover | lists, maps, model, nearby, seed, snowball, web | 10268 | 3069 | 7459 | $14.54 | 24.3 | budget |
| discover | lists, maps, model, nearby, seed, snowball, web | 12470 | 8503 | 0 | $15.52 | 27.4 | budget |
| discover | lists, maps, model, nearby, seed, snowball, web | 11394 | 0 | 10586 | $16.03 | 33.5 | budget |
| probe | lists, maps, model, nearby, seed, snowball, web | 481 | 18 | 119 | $0.55 | 2.3 | no |
| discover | lists, maps, model, nearby, seed, snowball, web | 0 | 0 | 1142 | $1.24 | 5.3 | no |

Total candidates: 18164. Verdicts: out 14971, unknown 2133, in 1060.
