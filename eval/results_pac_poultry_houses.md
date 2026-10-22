# Eval: Poultry Houses (`pac_poultry_houses`)

Reference set: 100 companies reviewed by Tim. Model: `claude-haiku-5-5`.

| Measure | Result | Target | |
|---|---|---|---|
| Recall | 91% | ≥ 95% | **missed** |
| Precision | 100% | ≥ 90% | met |
| Unknown | 6% | ≤ 5% | **missed** |
| Cost per 1,000 | $1.52 | < $2.00 | met |

Errors (API or search failures): 0

## Confusion matrix (rows: reference label, columns: verdict)

| | in | out | unknown | error |
|---|---|---|---|---|
| **in** | 41 | 1 | 3 | 0 |
| **out** | 0 | 52 | 3 | 0 |

## Disagreements

- **Energy Panel Structures** (https://epsbuildings.com/our-company/): label `in`, verdict `unknown`.
  - Energy Panel Structures makes insulated panels, SIPs, post-frame packages and trusses, and its site offers a poultry barn design program through dealers, but it does not show it builds poultry houses itself, distributes poultry house components, or makes poultry doors or windows; it is headquartered in Iowa/Missouri, so geography is satisfied. Evidence: https://epsbuildings.com/livestock/poultry/
- **GPC POULTRY SUPPLY & HARDWARE** (https://gpchardware.com/): label `in`, verdict `out`.
  - GPC Poultry Supply & Hardware is a Carnesville, GA hardware store and lumberyard selling general hardware, feed, fencing, roofing, and poultry farming supplies to farmers and homesteaders, which is a general retailer rather than a supplier specifically for commercial poultry houses; no evidence of building poultry houses or selling poultry house doors or windows. Evidence: https://gpchardware.com/
- **R&L Construction, INC** (https://rlincva.com/): label `in`, verdict `unknown`. Reviewer note: Their agriculture page specifically calls out poultry houses. See https://innovativepoultryproducts.com/dealer-heritage-poultry-supply.html?dealername=heritage%20poultry%20supply
  - R&L Construction, based in Bridgewater, Virginia, advertises agricultural, commercial, and residential construction, but the evidence does not show it builds commercial poultry houses, and the site search for poultry-house and door terms returned nothing. Evidence: https://rlincva.com/
- **Summit Livestock Facilities** (https://www.summitepc.com/): label `in`, verdict `unknown`. Reviewer note: Their project portfolio page shows a huge amount of poultry houses they built
  - Summit is a design-build contractor based in Remington, Indiana, serving agricultural, food and beverage, and light industrial clients, but the evidence never shows it builds commercial poultry houses, and the poultry-specific search returned nothing. Evidence: https://summitepc.com/
- **AR Mobile Food Trucks** (https://armobilefl.com/): label `out`, verdict `unknown`. Reviewer note: I'm considering no evidence to be "out"
  - The only evidence is a Cloudflare 'Just a moment...' placeholder and empty search results, so nothing shows the company builds, distributes, or makes poultry house products, and its location is also unclear from the evidence.
- **Carolina Structures** (https://carolinastructures.org/): label `out`, verdict `unknown`. Reviewer note: I'm considering no evidence to be "out"
  - The only evidence is a private WordPress placeholder page with no description of business activity, and searches of the company's site for poultry house or door terms returned nothing, so it cannot be determined whether the company builds, distributes, or makes products for commercial poultry houses or where it is based.
- **Gulf Coast Home Builders** (https://gulfcoasthomebuilders.net/): label `out`, verdict `unknown`.
  - The evidence shows only a homepage title reading 'Custom Designs' and a site search for poultry-house and poultry-door terms that returned no results, so there is no sign it builds poultry houses or makes or sells poultry doors or windows, and no location is shown. Evidence: https://gulfcoasthomebuilders.net/
