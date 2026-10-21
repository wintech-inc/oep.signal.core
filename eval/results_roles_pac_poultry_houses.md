# Role eval: Poultry Houses (`pac_poultry_houses`)

Reference set: 47 companies in the market, roles reviewed by Tim (37 customer, 0 competitor, 7 both, 3 neither). Model: `claude-haiku-5-5`.

| Measure | Result | Target | |
|---|---|---|---|
| Customer recall | 98% | ≥ 95% | met |
| Customer precision | 98% | ≥ 90% | met |
| Competitor recall | 86% | ≥ 85% | met |
| Competitor precision | 100% | ≥ 85% | met |
| Cost per 1,000 | $1.47 | < $2.00 | met |

Exact role accuracy: 94%. Errors (API or search failures): 0. Yes answers without an evidence URL from the evidence: 0.

## Confusion matrix (rows: reference label, columns: role)

| | customer | competitor | both | neither |
|---|---|---|---|---|
| **customer** | 36 | 0 | 0 | 1 |
| **competitor** | 0 | 0 | 0 | 0 |
| **both** | 1 | 0 | 6 | 0 |
| **neither** | 1 | 0 | 0 | 2 |

## Disagreements

- **A1 Ag Services LLC** (https://a1ag.com/): label `both`, role `customer`. Reviewer note: Their products page (https://a1ag.com/poultry/) lists several known competitors like L.B. White, Plyco, and Double L. I'm classifying as both since they do remodel work and could be reselling in addition to building.
  - A1 Ag Services lists Poultry products and K Buildings and describes construction crews doing estimating, concrete, and construction, so it likely builds or resells components for poultry houses, which makes it a customer. The evidence shows no doors or windows for poultry houses, and the product searches returned nothing, so it is not a competitor. Evidence: customer: https://a1ag.com/
- **Potters** (https://www.potterspoultryusa.com/): label `customer`, role `neither`.
  - Potters Poultry makes poultry equipment such as automatic nests, aviaries, slats, feeders, and drinkers, and sells them through dealers. It does not build commercial poultry houses, does not make or sell doors or windows, and its search results show only nests and mobile hoop-house equipment. Neither role is supported by the evidence.
- **Borders Poultry Supply Inc.** (https://www.borderstx.com/): label `neither`, role `customer`. Reviewer note: I'd like to make them a customer but don't see any website evidence so have to go "neither"
  - Borders Poultry Supply is a retail farm and poultry supply store that sells equipment and building materials for poultry houses ("We'll meet all your poultry house needs"), so it resells components to the companies that build and equip them, making it a customer. The evidence does not show it makes or sells doors or windows for poultry houses, so it is not a competitor. Evidence: customer: https://www.borderstx.com/

## Yes answers without an evidence URL from the evidence

None.
