# Discovery: Hunting Blinds (`pac_hunting_blinds`)

**This run stopped on its budget ($16) before finishing.** Work still due is listed under 'Left to do'; run `signal discover` again to continue.

## Headline

**709 in-market companies**: 394 customer, 77 both, 6 competitor, 232 neither.

That is **4.8x** the 147 in-market companies on the seed list. 562 of them are not on the seed list at all.

## By source

| Source | Candidates | In market | Customer | Both | Competitor | Neither | Only this source |
|---|---|---|---|---|---|---|---|
| seed | 917 | 150 | 119 | 19 | 2 | 10 | 11 |
| model | 10 | 7 | 3 | 1 | 0 | 3 | 0 |
| web | 2815 | 570 | 331 | 70 | 6 | 163 | 134 |
| maps | 4324 | 308 | 171 | 32 | 1 | 104 | 9 |
| lists | 4070 | 172 | 82 | 30 | 1 | 59 | 18 |
| nearby | 5807 | 480 | 276 | 52 | 2 | 150 | 0 |
| snowball | 4069 | 137 | 74 | 20 | 2 | 41 | 0 |

## Rounds (saturation curve)

| Round | Queries run | Snowballed | Leads | New candidates | New in market | % of list | Cost | Minutes |
|---|---|---|---|---|---|---|---|---|
| 1 | 2930 | 0 | 29898 | 7459 | 709 | 100% | $14.54 | 24 |
| 2 | 5082 | 709 | 58682 | 10586 | 0 | 0% | $15.52 | 27 |

Last round added 0% new in-market companies (stop rule: under 2%).

## Paging depth

5710 queries ran. Deepest page reached per query: page 1: 3408, page 2: 2302.
 0 queries still have a productive next page.

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

- In-market companies found by two or more sources (not counting the seed list): 522 of 709 (74%).
- Maps (map search, including nearby map searches) found 343; everything else found 672; both found 306.
- Capture-recapture estimate of the reachable market: about 753 in-market companies (we have 709).

## By state

Location known for 333 of 709 in-market companies. Outside the search locations (shown, not filtered): 0.

TX 68, PA 26, MI 23, WI 22, MN 18, MO 18, KY 14, OH 14, LA 11, MS 9, IL 8, KS 8, NC 8, NY 8, AL 7, AR 7, IA 6, ME 5, OK 5, IN 4, NE 4, TN 4, VA 4, CT 3, FL 3, GA 3, MT 3, ND 3, SC 3, CO 2, NJ 2, WY 2, CA 1, MD 1, OR 1, SD 1, UT 1, VT 1, WA 1, WV 1

## Leads dropped: no website found

1248 names from lists, maps, or the model had no website or social page in one search. Examples: A Grumpy Buck Hunting Blinds; Hometown Poultry Supply, Inc.; BrightWill Home Improvement LLC; Custom duck blinds in Arkansas; What window blind companies are recommended?; What are favorite extra large web blinds for Central FL?; Custom Outdoors of Georgia; THE ALPHA Crafted with precision, engineered for dominance. ...; Hands down, the best blind for the money! I sell these ...; Where to buy blinds for duck hunting in Indiana?; What's the best box blind for SE Iowa?; Bow or gun blind western ky; Airborne deer blinds from South Louisiana company; World Of Hunting Blinds; Hunting Blinds for sale in Berlin, Maryland; Custom aluminum blinds on eastern shore of Maryland; Who makes deer blinds in Hawks, Michigan?; Best duck blind manufacturer in Nebraska; With so many types of blinds on the market from pop-up ...; Duck blind setup in New Mexico; Best hunting blinds in NC at AYW Outfitters; Another load is on the road! These Five Star Deer Blinds ...; Building a hunting blind in Oklahoma; Durable deer hunting blinds made in the USA starting at ...; Custom deer blind builds in Pickens, SC; From the manufacturing facility, here in Columbia Tennessee to ...; Shadow Hunter Blinds for Tennessee deer hunting season; Who builds hunting blinds in Mill Creek, West Virginia?; ARDuckblinds; The Hunters Blind.

## Left to do

Queries with a next page due: 0. In-market companies not yet snowballed: 0. Candidates not yet classified (or errors): 10586.

## Runs

| Command | Sources | Searches | LLM calls | Classified | Cost | Minutes | Stopped on budget |
|---|---|---|---|---|---|---|---|
| discover | lists, maps, model, nearby, seed, snowball, web | 10268 | 3069 | 7459 | $14.54 | 24.3 | yes |
| discover | lists, maps, model, nearby, seed, snowball, web | 12470 | 8503 | 0 | $15.52 | 27.4 | yes |

Total candidates: 18045. Verdicts: None 10586, out 6025, unknown 725, in 709.
