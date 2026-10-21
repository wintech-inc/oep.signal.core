# Role eval: Poultry Houses (`pac_poultry_houses`)

Reference set: 47 companies in the market, roles reviewed by Tim (37 customer, 0 competitor, 7 both, 3 neither). Model: `claude-haiku-5-5`.

| Measure | Result | Target | |
|---|---|---|---|
| Customer recall | 100% | ≥ 95% | met |
| Customer precision | 100% | ≥ 90% | met |
| Competitor recall | 57% | ≥ 85% | **missed** |
| Competitor precision | 100% | ≥ 85% | met |
| Cost per 1,000 | $1.46 | < $2.00 | met |

Exact role accuracy: 94%. Errors (API or search failures): 0. Yes answers without an evidence URL from the evidence: 0.

## Confusion matrix (rows: reference label, columns: role)

| | customer | competitor | both | neither |
|---|---|---|---|---|
| **customer** | 37 | 0 | 0 | 0 |
| **competitor** | 0 | 0 | 0 | 0 |
| **both** | 3 | 0 | 4 | 0 |
| **neither** | 0 | 0 | 0 | 3 |

## Disagreements

- **A1 Ag Services LLC** (https://a1ag.com/): label `both`, role `customer`. Reviewer note: Their products page (https://a1ag.com/poultry/) lists several known competitors like L.B. White, Plyco, and Double L. I'm classifying as both since they do remodel work and could be reselling in addition to building.
  - A1 Ag Services is an ag services provider that sells and installs agricultural buildings, including poultry products and remodels, and its poultry offering appears to involve building work with concrete and construction crews, which suggests it builds or equips poultry houses. The evidence does not show it makes or sells doors or windows for poultry houses. Evidence: customer: https://a1ag.com/
- **Smith Poultry & Supply** (https://www.smithpoultryalabama.com/): label `both`, role `customer`.
  - Smith Poultry Supply is a dealer and service company that resells poultry house equipment, parts, and building components (including Eagan Manufacturing doors and windows) to growers and builders, which makes it a customer. It is not shown to make or sell its own doors or windows; it lists Eagan's door and window line as a brand it carries, which is a distributor relationship rather than competing manufacturing, so it is not a competitor. Evidence: customer: https://www.smithpoultryalabama.com/poultry-equipment.php
- **Superior Poultry Supply** (https://spspoultry.com/): label `both`, role `customer`.
  - Superior Poultry Supply builds new commercial poultry houses from the pad up and retrofits existing ones, so it is a customer. It lists Tunnel Doors among twelve equipment lines it resells as an authorized Chore-Time dealer, but the evidence does not show it manufactures doors or windows, so it is not a competitor. Evidence: customer: https://spspoultry.com/construction/

## Yes answers without an evidence URL from the evidence

None.
