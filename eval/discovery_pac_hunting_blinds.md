# Discovery: Hunting Blinds (`pac_hunting_blinds`)

## Headline

**1057 in-market companies**: 509 Manufacturer, 15 Component Manufacturer, 38 Component Reseller, 458 Reseller, 17 Supply Reseller, 20 Adjacent.

That is **7.3x** the 145 in-market companies on the seed list. 912 of them are not on the seed list at all.

## By source

| Source | Candidates | In market | Manufacturer | Component Manufacturer | Component Reseller | Reseller | Supply Reseller | Adjacent | Only this source |
|---|---|---|---|---|---|---|---|---|---|
| seed | 917 | 148 | 120 | 3 | 3 | 17 | 0 | 5 | 10 |
| model | 10 | 7 | 4 | 0 | 0 | 3 | 0 | 0 | 0 |
| web | 2815 | 656 | 327 | 14 | 28 | 266 | 8 | 13 | 190 |
| maps | 4324 | 330 | 155 | 4 | 13 | 144 | 6 | 8 | 28 |
| lists | 4070 | 179 | 88 | 3 | 8 | 71 | 3 | 6 | 23 |
| nearby | 5807 | 692 | 344 | 6 | 21 | 301 | 5 | 15 | 192 |
| snowball | 4069 | 178 | 84 | 4 | 4 | 75 | 5 | 6 | 33 |
| probe | 361 | 114 | 75 | 2 | 3 | 32 | 0 | 2 | 4 |

## Rounds (saturation curve)

| Round | Queries run | Snowballed | Leads | New candidates | New in market | % of list | Cost | Minutes |
|---|---|---|---|---|---|---|---|---|
| 1 | 2930 | 0 | 29898 | 7459 | 668 | 100% | $14.54 | 24 |
| 2 | 5082 | 709 | 58682 | 10586 | 385 | 37% | $15.52 | 27 |

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

- In-market companies found by two or more sources (not counting the seed list): 565 of 1057 (53%).
- Maps (map search, including nearby map searches) found 416; everything else found 959; both found 318.
- Capture-recapture estimate of the reachable market: about 1255 in-market companies (we have 1057).

## By state

Location known for 777 of 1057 in-market companies. Candidates out without classifying because they are based outside the market's geography: 5.

TX 133, PA 70, WI 50, MI 45, OH 37, MN 35, MO 34, KY 29, LA 28, AL 25, NC 22, AR 20, MS 19, TN 19, GA 18, IL 18, IA 16, IN 16, NY 16, FL 15, KS 14, OK 11, VA 11, NE 10, ND 9, SC 7, CA 6, WV 6, MD 5, ME 5, NJ 5, CT 4, MT 4, NH 3, CO 2, DE 2, SD 2, WA 2, MA 1, OR 1, VT 1, WY 1

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
| export | lists, maps, model, nearby, seed, snowball, web | 984 | 0 | 0 | $1.64 | 4.0 | no |
| export | lists, maps, model, nearby, seed, snowball, web | 0 | 1 | 0 | $0.00 | 0.1 | no |

Total candidates: 18164. Verdicts: out 14974, unknown 2133, in 1057.
