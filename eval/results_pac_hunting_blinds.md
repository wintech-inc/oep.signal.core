# Eval: Hunting Blinds (`pac_hunting_blinds`)

Reference set: 100 companies reviewed by Tim. Rescored after relabeling TX Duck Blinds OUT (same verdicts as commit 0a6c6a6). Model: `claude-haiku-5-5`.

| Measure | Result | Target | |
|---|---|---|---|
| Recall | 100% | ≥ 95% | met |
| Precision | 100% | ≥ 90% | met |
| Unknown | 3% | ≤ 5% | met |
| Cost per 1,000 | $1.47 | < $2.00 | met |

Errors (API or search failures): 0

## Confusion matrix (rows: reference label, columns: verdict)

| | in | out | unknown | error |
|---|---|---|---|---|
| **in** | 45 | 0 | 0 | 0 |
| **out** | 0 | 52 | 3 | 0 |

## Disagreements

- **Cavco - Crouse** (https://r-anell.com/): label `out`, verdict `unknown`.
  - No usable evidence: no homepage text and no search results.
- **Cavco Home Center** (https://cavcohomesburleson.com/): label `out`, verdict `unknown`.
  - No usable evidence: no homepage text and no search results.
- **The Blind Turtle** (https://blindturtle.net/): label `out`, verdict `unknown`. Reviewer note: They seem to have one product and are no longer accepting orders. See https://blindturtle.net/wp/the-blind-turtle/
  - The only evidence is a homepage with the title 'Untitled Document' and a site search returning no results, so there is nothing showing the company builds hunting blinds, sells blind components, or makes blind windows or doors.
