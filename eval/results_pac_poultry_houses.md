# Eval: Poultry Houses (`pac_poultry_houses`)

Reference set: 100 companies reviewed by Tim. Model: `claude-haiku-5-5`.

| Measure | Result | Target | |
|---|---|---|---|
| Recall | 91% | ≥ 95% | **missed** |
| Precision | 100% | ≥ 90% | met |
| Unknown | 4% | ≤ 5% | met |
| Cost per 1,000 | $1.51 | < $2.00 | met |

Errors (API or search failures): 0

## Confusion matrix (rows: reference label, columns: verdict)

| | in | out | unknown | error |
|---|---|---|---|---|
| **in** | 42 | 3 | 1 | 0 |
| **out** | 0 | 51 | 3 | 0 |

## Disagreements

- **GPC POULTRY SUPPLY & HARDWARE** (https://gpchardware.com/): label `in`, verdict `out`.
  - GPC Poultry Supply & Hardware is a Georgia hardware store and lumberyard selling general hardware, building materials, feed, fencing, and outdoor equipment; its poultry supplies are farm supplies rather than equipment or building materials specifically for commercial poultry houses, and it shows no poultry house construction or door/window manufacturing, so it does not meet rule A, B, or C. Evidence: https://gpchardware.com/
- **Penner Farm Services** (https://pennerfarmservice.com/poultry/): label `in`, verdict `out`.
  - Penner Farm Services is based in Blumenort, Manitoba, and Lacombe and Lethbridge, Alberta, Canada, which is outside the US geography the market requires, so it is OUT whatever its poultry work. Evidence: https://pennerfarmservice.com/poultry/
- **R&L Construction, INC** (https://rlincva.com/): label `in`, verdict `unknown`. Reviewer note: Their agriculture page specifically calls out poultry houses. See https://innovativepoultryproducts.com/dealer-heritage-poultry-supply.html?dealername=heritage%20poultry%20supply
  - R&L Construction is a Bridgewater, Virginia contractor offering agricultural, commercial, and residential construction, but the evidence does not show it builds commercial poultry houses, and the poultry-specific site search returned nothing. Evidence: https://www.rlincva.com/
- **Summit Livestock Facilities** (https://www.summitepc.com/): label `in`, verdict `out`. Reviewer note: Their project portfolio page shows a huge amount of poultry houses they built
  - Summit is an design-build contractor for agricultural, food, and light industrial facilities based in Remington, Indiana, but the evidence shows no commercial poultry house construction, and its poultry-related search returned nothing, so general agricultural building work does not qualify. Evidence: https://summitepc.com/
- **AR Mobile Food Trucks** (https://armobilefl.com/): label `out`, verdict `unknown`. Reviewer note: I'm considering no evidence to be "out"
  - The only evidence is a Cloudflare 'Just a moment...' placeholder and empty search results; nothing shows what the company does, so its participation in the poultry house door/window market cannot be determined.
- **Carolina Structures** (https://carolinastructures.org/): label `out`, verdict `unknown`. Reviewer note: I'm considering no evidence to be "out"
  - The only evidence is a private WordPress.com placeholder page with no description of business activity, and the site-specific search for poultry house or poultry door terms returned no results, so it cannot be determined whether Carolina Structures builds poultry houses, distributes poultry components, or makes poultry doors or windows.
- **Gulf Coast Home Builders** (https://gulfcoasthomebuilders.net/): label `out`, verdict `unknown`.
  - The only evidence is a homepage title reading 'Custom Designs' with no stated location, and a site-restricted search for poultry house or poultry door terms returned no results, so there is no evidence the company builds poultry houses or makes or sells poultry doors or windows. Evidence: https://gulfcoasthomebuilders.net/
