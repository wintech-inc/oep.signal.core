# Eval: Hunting Blinds (`pac_hunting_blinds`)

Reference set: 100 companies reviewed by Tim. Model: `claude-haiku-5-5`.

| Measure | Result | Target | |
|---|---|---|---|
| Recall | 96% | ≥ 95% | met |
| Precision | 96% | ≥ 90% | met |
| Unknown | 4% | ≤ 5% | met |
| Cost per 1,000 | $1.47 | < $2.00 | met |

Errors (API or search failures): 0

## Confusion matrix (rows: reference label, columns: verdict)

| | in | out | unknown | error |
|---|---|---|---|---|
| **in** | 43 | 1 | 1 | 0 |
| **out** | 2 | 50 | 3 | 0 |

## Disagreements

- **Amish Blinds** (https://amishblinds.com/): label `in`, verdict `unknown`. Reviewer note: I almost voted out, but they are a rare "blind distributor". It would be worth contacting them to see if they have any influence in the supply chain or can provide info on who the builders are.
  - McKenzie Innovations (amishblinds.com) sells 100% Amish-made deer blinds it describes as sourced from builders it works with, and says it is one of the largest dealers; it is a dealer/reseller of finished blinds, which is OUT, though it also lists the products as its own designs and manufacturing for ice spearing gear, leaving the blind-building role ambiguous. Evidence: https://amishblinds.com/
- **Foote's Amish Sheds** (https://shedsbarnsgazebosamishbuiltbyfoote.com/): label `in`, verdict `out`. Reviewer note: I like including them so we can contact them to find out who builds the blinds.
  - Foote's Amish Sheds is a retailer that sells Amish-built sheds, barns, and hunting blinds sourced from Pennsylvania Amish builders and trucked to its facility, and it offers delivery and installation; it does not show it manufactures hunting blinds itself, but it sells and installs hard-sided hunting blinds to end users, which is a dealer/reseller role excluded from the market. Evidence: https://shedsbarnsgazebosamishbuiltbyfoote.com/products/hunting-blinds/
- **Cavco - Crouse** (https://r-anell.com/): label `out`, verdict `unknown`.
  - No usable evidence: no homepage text and no search results.
- **Cavco Home Center** (https://cavcohomesburleson.com/): label `out`, verdict `unknown`.
  - No usable evidence: no homepage text and no search results.
- **Freedom Campers** (https://freedomcampers.com/): label `out`, verdict `in`. Reviewer note: The URL you provided redirects to Redneck Blinds. I think Freedom Capers distributes blinds, they don't make them.
  - Freedom Campers is primarily a truck bed and trailer camper maker, and its site has a 'Hunting Blinds for Sale' collection listing Box Blinds and Ground Blinds, which suggests it builds hard-sided blinds, though the evidence does not confirm whether it manufactures them or resells others' products. Evidence: https://freedomcampers.com/collections/hunting-blinds?srsltid=AU7gw4VSBymM5wGh1P8a7CvCN1acBfulejb7Nigh2XjC0Gki18vmCLao
- **Kohler Blinds** (https://www.kohlerblinds.com/): label `out`, verdict `in`. Reviewer note: I think we specifically excluded waterfowl blinds.
  - Kohler Blinds builds permanent steel-constructed waterfowl duck blinds ("Built in the USA", "we build"), which are hard-sided enclosed hunting blinds with windows-like weather-tight panels, so it manufactures the end product under rule A. Evidence: https://www.kohlerblinds.com/
- **The Blind Turtle** (https://blindturtle.net/): label `out`, verdict `unknown`. Reviewer note: They seem to have one product and are no longer accepting orders. See https://blindturtle.net/wp/the-blind-turtle/
  - The only evidence is an essentially empty homepage titled 'Untitled Document' and a site search returning no results, so there is no indication of whether the company builds blinds, sells blind components, or makes windows or doors for blinds.
