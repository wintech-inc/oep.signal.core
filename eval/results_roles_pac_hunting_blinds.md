# Role eval: Hunting Blinds (`pac_hunting_blinds`)

Reference set: 53 companies in the market, roles reviewed by Tim (34 customer, 0 competitor, 12 both, 7 neither). Model: `claude-haiku-5-5`.

| Measure | Result | Target | |
|---|---|---|---|
| Customer recall | 96% | ≥ 95% | met |
| Customer precision | 94% | ≥ 90% | met |
| Competitor recall | 100% | ≥ 85% | met |
| Competitor precision | 86% | ≥ 85% | met |
| Cost per 1,000 | $1.58 | < $2.00 | met |

Exact role accuracy: 87%. Errors (API or search failures): 0. Yes answers without an evidence URL from the evidence: 2.

## Confusion matrix (rows: reference label, columns: role)

| | customer | competitor | both | neither |
|---|---|---|---|---|
| **customer** | 30 | 0 | 2 | 2 |
| **competitor** | 0 | 0 | 0 | 0 |
| **both** | 0 | 0 | 12 | 0 |
| **neither** | 3 | 0 | 0 | 4 |

## Disagreements

- **A Grumpy Buck Hunting Blinds** (https://www.facebook.com/p/A-Grumpy-Buck-Hunting-Blinds-100063662525377/): label `customer`, role `both`.
  - A Grumpy Buck Hunting Blinds builds and sells hard-sided hunting blinds (bowhunter blinds, 4x4 and 6x8 blinds, ground and trailer blinds) and its own sliding-window systems are advertised in its posts, so it is both a customer (builder of blinds) and a competitor (sells its own windows and doors, including aluminum doors and frames, for its blinds). Evidence: customer: https://www.facebook.com/61580233800606/videos/our-best-sellerthe-bowhunter-blind-with-4-vertical4horizontal-windowsgreat-for-g/1500521451764548/; competitor: https://www.facebook.com/61580233800606/videos/bowhunter-360-modelcoulee-country-blinds/1270478461723033/
- **Penn Dutch Structures** (https://www.penndutchstructures.com/): label `customer`, role `neither`.
  - Penn Dutch Structures is a retailer and distributor of Amish-built deer blinds, which are finished hard-sided blinds it resells. The evidence shows no building of blinds on its own and no windows or doors for hunting blinds, so it is neither a customer nor a competitor.
- **Premier Hunting Blinds** (https://www.facebook.com/PremierHuntingBlinds/): label `customer`, role `neither`.
  - Premier Hunting Blinds appears in the search results as a seller of hunting blinds in Shelbyville, Missouri (Yelp, MapQuest, Yahoo listings listing Premier Standard and Bowhunter blinds), which makes it a dealer of finished blinds and therefore neither a customer nor a competitor under the market notes. Nothing in the evidence shows it builds blinds itself, resells components, or makes or sells windows or doors.
- **Texas Deer Stands** (https://texasdeerstands.com/): label `customer`, role `both`. Reviewer note: They use their own windows/doors, but there is no evidence of them selling standalone windows and doors. We would be calling on them to see if they would like to outsource to us.
  - Texas Deer Stands manufactures fiberglass hard-sided deer blinds and sells them through dealers, so it is a builder of hard-sided hunting blinds and therefore a customer. It also makes its own deer blind windows (silent sliding windows) and aluminum doors for its blinds, and sells them as part of those blinds, so it is a competitor. Evidence: customer: https://texasdeerstands.com/; competitor: http://www.texasdeerstands.com/blinds.htm
- **Amish Blinds** (https://amishblinds.com/): label `neither`, role `customer`.
  - Amish Blinds (McKenzie Innovations) is one of the largest dealers of Amish-built hard-sided deer blinds, reselling finished blinds and offering window configurations and options, but the evidence does not show it makes or sells windows or doors as standalone components. It is a dealer that resells finished blinds, which the rules say is neither a customer nor a competitor; however, it also builds and designs its own deer blinds' options and sells to outfitters, so it is treated as a customer based on the 'when suggested but not proven, answer yes' rule. Evidence: customer: https://amishblinds.com/
- **Radix Hunting** (https://www.radixhunting.com/): label `neither`, role `customer`.
  - Radix Hunting sells premium hard-shell and soft-shell elevated, ground, and tower hunting blind systems, which makes it a customer for PAC's windows and doors. Its search turned up no windows or doors of its own, so it is not a competitor. Evidence: customer: https://www.radixhunting.com/hunting-blinds?srsltid=AU7gw4XAMU4GNt-cpftJIYq2bputym4syPQPQTsSU6--MYk4w-wAA_wb
- **Sheds by Fisher** (https://shedsbyfisher.com/): label `neither`, role `customer`.
  - Sheds By Fisher is a builder and reseller of hunting blinds, sourcing them from Boonetown Outdoors and offering them as a product line. It is a customer because it resells finished hunting blinds and builds sheds and structures, and the evidence does not show it makes or sells windows or doors for hunting blinds, so it is not a competitor. Evidence: customer: https://shedsbyfisher.com/hunting-blinds/

## Yes answers without an evidence URL from the evidence

- **The Blynd** (https://www.blynd.com/index.html): customer.
- **Hunting Blinds** (https://texashunterproducts.com/): customer, competitor.
