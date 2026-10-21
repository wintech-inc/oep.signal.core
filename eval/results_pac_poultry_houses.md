# Eval: Poultry Houses (`pac_poultry_houses`)

Reference set: 100 companies reviewed by Tim. Model: `claude-haiku-5-5`.

| Measure | Result | Target | |
|---|---|---|---|
| Recall | 96% | ≥ 95% | met |
| Precision | 100% | ≥ 90% | met |
| Unknown | 3% | ≤ 5% | met |
| Cost per 1,000 | $1.46 | < $2.00 | met |

Errors (API or search failures): 0

## Confusion matrix (rows: reference label, columns: verdict)

| | in | out | unknown | error |
|---|---|---|---|---|
| **in** | 44 | 1 | 1 | 0 |
| **out** | 0 | 52 | 2 | 0 |

## Disagreements

- **R&L Construction, INC** (https://rlincva.com/): label `in`, verdict `unknown`. Reviewer note: Their agriculture page specifically calls out poultry houses. See https://innovativepoultryproducts.com/dealer-heritage-poultry-supply.html?dealername=heritage%20poultry%20supply
  - R&L Construction advertises agricultural, commercial, and residential construction plus concrete pumping, but the evidence never shows it building commercial poultry houses, and a site search for poultry-house terms returned no results. Evidence: https://www.rlincva.com/
- **Summit Livestock Facilities** (https://www.summitepc.com/): label `in`, verdict `out`. Reviewer note: Their project portfolio page shows a huge amount of poultry houses they built
  - Summit is a design-build contractor serving agricultural, food and beverage, and light industrial clients, with agricultural work described only as production, processing, and cold storage facilities; the homepage and the poultry-specific site search show no poultry house construction, poultry equipment distribution, or poultry doors or windows. Evidence: https://summitepc.com/
- **AR Mobile Food Trucks** (https://armobilefl.com/): label `out`, verdict `unknown`. Reviewer note: I'm considering no evidence to be "out"
  - The only evidence is a Cloudflare 'Just a moment...' interstitial on the homepage and a search returning no results, so nothing shows the company makes or sells poultry houses, poultry house components, or doors or windows; its name suggests mobile food trucks, which is unrelated. Evidence: https://armobilefl.com/
- **Carolina Structures** (https://carolinastructures.org/): label `out`, verdict `unknown`. Reviewer note: I'm considering no evidence to be "out"
  - The only evidence is a private WordPress placeholder page with no description of business activity, and site-restricted searches for poultry house or door terms returned no results, so it cannot be determined whether Carolina Structures builds poultry houses, distributes poultry house components, or makes poultry doors or windows. Evidence: https://carolinastructures.wordpress.com/
