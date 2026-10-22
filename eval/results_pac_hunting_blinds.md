# Eval: Hunting Blinds (`pac_hunting_blinds`)

Reference set: 100 companies reviewed by Tim. Model: `claude-haiku-5-5`.

| Measure | Result | Target | |
|---|---|---|---|
| Recall | 100% | ≥ 95% | met |
| Precision | 96% | ≥ 90% | met |
| Unknown | 3% | ≤ 5% | met |
| Cost per 1,000 | $1.53 | < $2.00 | met |

Errors (API or search failures): 0

## Confusion matrix (rows: reference label, columns: verdict)

| | in | out | unknown | error |
|---|---|---|---|---|
| **in** | 45 | 0 | 0 | 0 |
| **out** | 2 | 50 | 3 | 0 |

## Disagreements

- **Cavco - Crouse** (https://r-anell.com/): label `out`, verdict `unknown`.
  - No usable evidence: no homepage text and no search results.
- **Cavco Home Center** (https://cavcohomesburleson.com/): label `out`, verdict `unknown`.
  - No usable evidence: no homepage text and no search results.
- **Meyer Distributing** (https://www.meyerdistributing.com/): label `out`, verdict `in`.
  - Meyer Distributing is a Jasper, Indiana automotive parts wholesale distributor, and its return-policy page lists American Hunting Blind Company (AHB) as a manufacturer vendor, which suggests it distributes hunting blind products, though the evidence is thin and doesn't show specific blind components. Evidence: https://www.meyerdistributing.com/Produits/Soutien/Politiquederetour/RMAexigerdunfabricant/tabid/192/pages/lets-go-aero-warranty/language/fr-CA/Default.aspx?www.edelbrock.com=www.wholesalepartsource.com&www.wholesalepartsource.com=www.letsgoaero.com
- **TX Duck Blinds** (https://txduckblinds.com/): label `out`, verdict `in`. Reviewer note: Relabeled OUT on 2026-10-21: duck blinds are excluded, and the deer blind it lists is a hay bale blind with no doors or windows.
  - TX Duck Blinds is based in Gainesville, TX and builds customized metal duck blinds, which are excluded waterfowl blinds, but its discounted-blinds page lists a 6' Hay Bale Deer Blind, suggesting it also builds deer blinds under rule A, though whether that product is hard-sided is not confirmed. Evidence: https://txduckblinds.com/discounted-blinds
- **The Blind Turtle** (https://blindturtle.net/): label `out`, verdict `unknown`. Reviewer note: They seem to have one product and are no longer accepting orders. See https://blindturtle.net/wp/the-blind-turtle/
  - The only evidence is an essentially empty homepage titled 'Untitled Document' and a search returning no results, so nothing shows the company builds hunting blinds, distributes blind components, or makes blind windows or doors, and its location is also unshown.
