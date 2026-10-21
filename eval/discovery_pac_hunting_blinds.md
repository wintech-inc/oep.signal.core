# Discovery: Hunting Blinds (`pac_hunting_blinds`)

**This run stopped on its budget ($8) before finishing.** Work still due is listed under 'Left to do'; run `signal discover` again to continue.

## Headline

**709 in-market companies**: 394 customer, 77 both, 6 competitor, 232 neither.

That is **4.8x** the 147 in-market companies on the seed list. 562 of them are not on the seed list at all.

## By source

| Source | Candidates | In market | Customer | Both | Competitor | Neither | Only this source |
|---|---|---|---|---|---|---|---|
| seed | 917 | 150 | 119 | 19 | 2 | 10 | 29 |
| model | 10 | 7 | 3 | 1 | 0 | 3 | 0 |
| web | 1593 | 514 | 292 | 65 | 6 | 151 | 310 |
| maps | 3159 | 278 | 156 | 26 | 1 | 95 | 90 |
| lists | 2470 | 139 | 65 | 20 | 1 | 53 | 47 |

## Rounds (saturation curve)

| Round | Queries run | Snowballed | Leads | New candidates | New in market | % of list | Cost | Minutes |
|---|---|---|---|---|---|---|---|---|
| 1 | 2930 | 0 | 29898 | 7459 | 709 | 100% | $14.54 | 24 |

Last round added 100% new in-market companies (stop rule: under 2%).

## Paging depth

2930 queries ran. Deepest page reached per query: page 1: 2930.
 2302 queries still have a productive next page.


Towns searched with nearby queries: 0.

## Source overlap and market size

- In-market companies found by two or more sources (not counting the seed list): 200 of 709 (28%).
- Maps (map search, including nearby map searches) found 278; everything else found 619; both found 188.
- Capture-recapture estimate of the reachable market: about 915 in-market companies (we have 709).

## By state

Location known for 292 of 709 in-market companies. Outside the search locations (shown, not filtered): 0.

TX 58, PA 20, MI 19, WI 19, MN 17, MO 17, OH 13, KY 12, LA 9, MS 8, NC 8, AL 7, IL 7, KS 7, AR 6, NY 6, IA 5, ME 5, IN 4, NE 4, TN 4, CT 3, GA 3, MT 3, ND 3, OK 3, SC 3, VA 3, CO 2, FL 2, NJ 2, WY 2, CA 1, MD 1, OR 1, SD 1, UT 1, VT 1, WA 1, WV 1

## Leads dropped: no website found

1248 names from lists, maps, or the model had no website or social page in one search. Examples: A Grumpy Buck Hunting Blinds; Hometown Poultry Supply, Inc.; BrightWill Home Improvement LLC; Custom duck blinds in Arkansas; What window blind companies are recommended?; What are favorite extra large web blinds for Central FL?; Custom Outdoors of Georgia; THE ALPHA Crafted with precision, engineered for dominance. ...; Hands down, the best blind for the money! I sell these ...; Where to buy blinds for duck hunting in Indiana?; What's the best box blind for SE Iowa?; Bow or gun blind western ky; Airborne deer blinds from South Louisiana company; World Of Hunting Blinds; Hunting Blinds for sale in Berlin, Maryland; Custom aluminum blinds on eastern shore of Maryland; Who makes deer blinds in Hawks, Michigan?; Best duck blind manufacturer in Nebraska; With so many types of blinds on the market from pop-up ...; Duck blind setup in New Mexico; Best hunting blinds in NC at AYW Outfitters; Another load is on the road! These Five Star Deer Blinds ...; Building a hunting blind in Oklahoma; Durable deer hunting blinds made in the USA starting at ...; Custom deer blind builds in Pickens, SC; From the manufacturing facility, here in Columbia Tennessee to ...; Shadow Hunter Blinds for Tennessee deer hunting season; Who builds hunting blinds in Mill Creek, West Virginia?; ARDuckblinds; The Hunters Blind.

## Left to do

Queries with a next page due: 2302. In-market companies not yet snowballed: 709. Candidates not yet classified (or errors): 0.

## Runs

| Command | Sources | Searches | LLM calls | Classified | Cost | Minutes | Stopped on budget |
|---|---|---|---|---|---|---|---|
| discover | lists, maps, model, nearby, seed, snowball, web | 10268 | 3069 | 7459 | $14.54 | 24.3 | yes |

Total candidates: 7459. Verdicts: out 6025, unknown 725, in 709.
