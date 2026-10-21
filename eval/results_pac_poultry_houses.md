# Eval: Poultry Houses (`pac_poultry_houses`)

Reference set: 100 companies reviewed by Tim. Model: `claude-haiku-5-5`.

| Measure | Result | Target | |
|---|---|---|---|
| Recall | 96% | ≥ 95% | met |
| Precision | 100% | ≥ 90% | met |
| Unknown | 4% | ≤ 5% | met |
| Cost per 1,000 | $1.47 | < $2.00 | met |

Errors (API or search failures): 0

## Confusion matrix (rows: reference label, columns: verdict)

| | in | out | unknown | error |
|---|---|---|---|---|
| **in** | 44 | 1 | 1 | 0 |
| **out** | 0 | 51 | 3 | 0 |

## Disagreements

- **R&L Construction, INC** (https://rlincva.com/): label `in`, verdict `unknown`. Reviewer note: Their agriculture page specifically calls out poultry houses. See https://innovativepoultryproducts.com/dealer-heritage-poultry-supply.html?dealername=heritage%20poultry%20supply
  - R&L Construction advertises agricultural, commercial, and residential construction and concrete pumping in Virginia, but the homepage and the poultry-specific site search show no poultry houses, poultry doors, or windows, so its agricultural work is not shown to be poultry-related. Evidence: https://www.rlincva.com/
- **Summit Livestock Facilities** (https://www.summitepc.com/): label `in`, verdict `out`. Reviewer note: Their project portfolio page shows a huge amount of poultry houses they built
  - Summit is a design-build contractor for agricultural, food and beverage, and light industrial facilities, but its homepage and a site search for poultry house and poultry door terms show no poultry house work, so it does not show rule A, B, or C. Evidence: https://summitepc.com/
- **AR Mobile Food Trucks** (https://armobilefl.com/): label `out`, verdict `unknown`. Reviewer note: I'm considering no evidence to be "out"
  - The only evidence is a Cloudflare 'Just a moment...' interstitial on the homepage and an empty search for poultry-house and door terms; the company's business is not shown, and the name suggests a mobile food truck business unrelated to poultry houses.
- **Carolina Structures** (https://carolinastructures.org/): label `out`, verdict `unknown`. Reviewer note: I'm considering no evidence to be "out"
  - The only evidence is a private WordPress.com placeholder page with no description of business activity, and site-restricted searches for poultry house or door terms returned nothing, so it cannot be determined whether Carolina Structures builds poultry houses, distributes poultry components, or makes poultry doors or windows.
- **Gulf Coast Home Builders** (https://gulfcoasthomebuilders.net/): label `out`, verdict `unknown`.
  - The only evidence is a homepage header reading 'Custom Designs' and a site search for poultry house and poultry door terms that returned no results, so there is no indication the company builds poultry houses or makes or sells poultry doors or windows. Evidence: https://gulfcoasthomebuilders.net/
