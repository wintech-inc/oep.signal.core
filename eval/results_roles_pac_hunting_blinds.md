# Role eval: Hunting Blinds (`pac_hunting_blinds`)

Reference set: 53 companies in the market, roles reviewed by Tim (35 customer, 0 competitor, 11 both, 7 neither). Model: `claude-haiku-5-5`.

| Measure | Result | Target | |
|---|---|---|---|
| Customer recall | 98% | ≥ 95% | met |
| Customer precision | 96% | ≥ 90% | met |
| Competitor recall | 100% | ≥ 85% | met |
| Competitor precision | 85% | ≥ 85% | **missed** |
| Cost per 1,000 | $1.59 | < $2.00 | met |

Exact role accuracy: 91%. Errors (API or search failures): 0. Yes answers without an evidence URL from the evidence: 1.

## Confusion matrix (rows: reference label, columns: role)

| | customer | competitor | both | neither |
|---|---|---|---|---|
| **customer** | 32 | 0 | 2 | 1 |
| **competitor** | 0 | 0 | 0 | 0 |
| **both** | 0 | 0 | 11 | 0 |
| **neither** | 2 | 0 | 0 | 5 |

## Disagreements

- **Lazy Man Stands (Lazyman blinds)** (https://lazymanstands.com/): label `customer`, role `both`.
  - Lazy Man Stands sells the Brickhouse Bow, described as a hard-sided ground blind, so it builds hard-sided hunting blinds and is a customer. It also sells its own FG Bow Aluminium Framed Hinged Window, so it makes and sells windows for hunting blinds and is a competitor. Evidence: customer: https://lazymanstands.com/products/brickhouse-bow; competitor: https://lazymanstands.com/
- **Premier Hunting Blinds** (https://www.facebook.com/PremierHuntingBlinds/): label `customer`, role `neither`.
  - Premier Hunting Blinds appears in the search results as a seller of hunting blinds in Shelbyville, Missouri (Yelp, MapQuest, Yahoo Local listings show Premier Bowhunter and Standard blinds), but the evidence does not show it builds its own blinds or sells windows or doors. Its listings mention window treatments only generically, and the Facebook page itself was not fetched, so neither role is established.
- **Texas Deer Stands** (https://texasdeerstands.com/): label `customer`, role `both`. Reviewer note: They use their own windows/doors, but there is no evidence of them selling standalone windows and doors. We would be calling on them to see if they would like to outsource to us.
  - Texas Deer Stands manufactures fiberglass hard-sided deer blinds and sells them through dealers, so it is a builder of hunting blinds and therefore a customer. It also makes and sells its own aluminum-framed blind windows and all-aluminum doors, which are products like ours, so it is a competitor too. Evidence: customer: https://texasdeerstands.com/; competitor: http://www.texasdeerstands.com/blinds.htm
- **Amish Blinds** (https://amishblinds.com/): label `neither`, role `customer`.
  - McKenzie Innovations (Amish Blinds) is one of the largest dealers of Amish-built hard-sided deer blinds and offers multiple window configurations, and it volume-sells to outfitters and retailers, so it resells blinds and components for them; it sells finished blinds rather than windows or doors separately, and the evidence does not show it makes or sells windows or doors as standalone products, so it is a customer but not a competitor. Evidence: customer: https://amishblinds.com/
- **Radix Hunting** (https://www.radixhunting.com/): label `neither`, role `customer`.
  - Radix Hunting sells hard-shell and soft-shell elevated, ground, and tower hunting blind systems, which makes it a customer in that it resells finished blinds (builder/seller of blind systems) and components; it shows no windows or doors for hunting blinds, so it is not a competitor on the evidence. Evidence: customer: https://www.radixhunting.com/hunting-blinds?srsltid=AU7gw4XAMU4GNt-cpftJIYq2bputym4syPQPQTsSU6--MYk4w-wAA_wb

## Yes answers without an evidence URL from the evidence

- **The Blynd** (https://www.blynd.com/index.html): customer.
