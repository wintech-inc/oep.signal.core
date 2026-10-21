# Role eval: Hunting Blinds (`pac_hunting_blinds`)

Reference set: 53 companies in the market, roles reviewed by Tim (35 customer, 0 competitor, 11 both, 7 neither). Model: `claude-haiku-5-5`.

| Measure | Result | Target | |
|---|---|---|---|
| Customer recall | 93% | ≥ 95% | **missed** |
| Customer precision | 100% | ≥ 90% | met |
| Competitor recall | 91% | ≥ 85% | met |
| Competitor precision | 83% | ≥ 85% | **missed** |
| Cost per 1,000 | $1.58 | < $2.00 | met |

Exact role accuracy: 89%. Errors (API or search failures): 0. Yes answers without an evidence URL from the evidence: 1.

## Confusion matrix (rows: reference label, columns: role)

| | customer | competitor | both | neither |
|---|---|---|---|---|
| **customer** | 32 | 0 | 2 | 1 |
| **competitor** | 0 | 0 | 0 | 0 |
| **both** | 1 | 2 | 8 | 0 |
| **neither** | 0 | 0 | 0 | 7 |

## Disagreements

- **Buckstop Outdoors, LLC.** (https://buckstophunting.com/): label `both`, role `competitor`. Reviewer note: Yes, but if they're selling doors that other companies make then they're a distributor by definition which would make them "both" -- we would call on them to see if they are interested in offering our products as well
  - Buckstop is primarily a retailer of finished hunting blinds from MB Ranch King, Big Country, and Lamco, which alone would make it neither. Its site navigation also lists hunting blind windows, doors, and window track as product categories, so it sells windows and doors for hard-sided blinds and is a competitor. Evidence: competitor: https://buckstophunting.com/
- **Maverick Blinds** (https://maverickhunting.com/): label `both`, role `customer`.
  - Maverick Hunting designs and sells its own hard-sided hunting blinds (Maverick and Booner lines) made in America, so it builds hard-sided blinds and is a customer. It also sells plexiglass windows and door latches/hinges for its blinds, but the evidence shows only plexiglass windows and window clips/hinges as replacement parts, not aluminum or vinyl windows or doors sold as a window/door product for other blinds, so it is not shown to be a competitor. Evidence: customer: https://maverickhunting.com/
- **Midco Products** (https://www.midcoproducts.com/): label `both`, role `competitor`. Reviewer note: Midco is a known distributor, so this is likely someone else's window. Flagging them as both as a distributor.
  - Midco Products makes and sells aluminum and vinyl windows and doors for sheds, playhouses, and portable buildings, and it sells an aluminum hunting blind window. That makes it a competitor. The evidence does not show it building hard-sided hunting blinds or reselling components for them, so it is not a customer. Evidence: competitor: https://www.midcoproducts.com/windows/deer-blind-window
- **360 Hunting Blinds** (https://360huntingblinds.com/): label `customer`, role `both`.
  - 360 Hunting Blinds designs and manufactures its own hard-sided elevated, box, and shootin' house blinds (made in Hegins, PA, per a customer review) and sells them through dealers, so it is a customer. It also makes its own tinted sliding, weighted windows and locking doors for those blinds and sells replacement parts, which makes it a competitor as well. Evidence: customer: https://360huntingblinds.com/; competitor: https://360huntingblinds.com/pages/360-pro?srsltid=AU7gw4X5ld9G1SbqcDffQGvDt9jMuPbHmzMtAouAvdDioSODCV42EGG3
- **Lazy Man Stands (Lazyman blinds)** (https://lazymanstands.com/): label `customer`, role `both`.
  - Lazy Man Stands sells hard-sided hunting blinds (e.g., the Brickhouse Bow, described as a hard-sided ground blind) and its own aluminum-framed hinged blind windows, which are not for its own blinds only but sold as products. Its Brickhouse Bow listing shows it builds hard-sided blinds, making it a customer. It sells aluminum-framed hinged windows for blinds, making it a competitor. Evidence: customer: https://lazymanstands.com/products/brickhouse-bow; competitor: https://lazymanstands.com/
- **Premier Hunting Blinds** (https://www.facebook.com/PremierHuntingBlinds/): label `customer`, role `neither`.
  - Premier Hunting Blinds appears to be a seller of finished hunting blinds (Premier Standard and Bowhunter blinds listed on Yelp, MapQuest, Yahoo) with no evidence it builds blinds or sells windows or doors for them, so it is neither a customer nor a competitor under the rules for resellers of finished blinds.

## Yes answers without an evidence URL from the evidence

- **The Blynd** (https://www.blynd.com/index.html): customer.
