# Eval: Hunting Blinds (`pac_hunting_blinds`)

Reference set: 100 companies reviewed by Tim. Model: `claude-haiku-5-5`.

| Measure | Result | Target | |
|---|---|---|---|
| Recall | 98% | ≥ 95% | met |
| Precision | 100% | ≥ 90% | met |
| Unknown | 3% | ≤ 5% | met |
| Cost per 1,000 | $1.47 | < $2.00 | met |

Errors (API or search failures): 0

## Confusion matrix (rows: reference label, columns: verdict)

| | in | out | unknown | error |
|---|---|---|---|---|
| **in** | 45 | 1 | 0 | 0 |
| **out** | 0 | 51 | 3 | 0 |

## Disagreements

- **TX Duck Blinds** (https://txduckblinds.com/): label `in`, verdict `out`.
  - TX Duck Blinds manufactures customized metal duck blinds (waterfowl/layout-style pit, skid, and floating blinds), which the market excludes, and its only deer blind mention is a discounted 6' hay bale deer blind listing with no evidence it builds hard-sided deer blinds or makes windows or doors for them. Evidence: https://txduckblinds.com/
- **Cavco - Crouse** (https://r-anell.com/): label `out`, verdict `unknown`.
  - No usable evidence: no homepage text and no search results.
- **Cavco Home Center** (https://cavcohomesburleson.com/): label `out`, verdict `unknown`.
  - No usable evidence: no homepage text and no search results.
- **The Blind Turtle** (https://blindturtle.net/): label `out`, verdict `unknown`. Reviewer note: They seem to have one product and are no longer accepting orders. See https://blindturtle.net/wp/the-blind-turtle/
  - The only evidence is a homepage with the title 'Untitled Document' and a site search returning no results, so there is nothing showing the company builds hunting blinds, sells blind components, or makes blind windows or doors.
