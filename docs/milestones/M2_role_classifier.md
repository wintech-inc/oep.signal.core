# M2: Role classifier (customer vs. competitor)

Status: draft, under discussion with Tim in the M2 planning thread (2026-10-21). Implementation happens in a separate thread.

Background and definitions: [project_overview.md](../project_overview.md). The first stage: [M1_market_classifier.md](M1_market_classifier.md).

## 1. Goal

For a company that the M1 market classifier marks `in`, answer a second question:

> From {supplier}'s point of view, is this company a **possible customer**, a **possible competitor**, **both**, or **neither**?

The answer comes with a one-sentence reason and the URL of the evidence used.

SIGNAL is now a two-stage engine:

```
stage 1 (M1, unchanged):  is the company in the market?       in | out | unknown
stage 2 (M2, new):        if in, what is its role to us?        customer | competitor | both | neither
```

Stage 2 runs only on companies stage 1 marks `in`. Like M1, it must be generic (a new market means a new brief, not new code), fast, and cheap.

**M1 does not change.** Its prompt, code path, outputs, and eval results stay as they are. M2 adds a new prompt and a new module next to it. The only shared file M2 touches is the brief, and only by adding optional fields that M1 does not read (section 4).

**Out of scope for M2:** a database, discovering new companies, geography, contact data, UI, and changes to the stage-1 rule.

## 2. What the roles mean

PAC and WinTech make doors and windows that other companies build into an end product. The roles are judged against that.

- **Possible customer:** a company that could buy our products. It builds the end product (and so chooses its door and window vendors), or it resells components for the end product to the companies that build, equip, or maintain it.
- **Possible competitor:** a company that sells products like ours into this market. It makes or sells {our_products.category} for {end_product.name}s.
- **Both:** both of the above. The common case is a distributor that carries other makers' doors or windows: sales must decide whether to sell through it or go around it.
- **Neither:** in the market, but it neither buys nor sells products like ours. For example a company that M1 let through on suggestive evidence, or (pending Tim's decision) a dealer that resells finished end products.

These definitions follow the project overview and the original briefs. Checked against the competitors Tim named there:

| Company | Customer? | Competitor? | Role |
|---|---|---|---|
| Eagan, Plyco, Double L Group, L.B. White, Chore-Time (poultry) | no: they don't build houses or resell others' components | yes: they make poultry house doors | competitor |
| Hog Slat (poultry) | yes: builds houses, distributes equipment | yes: sells its own tunnel door | both |
| Southern Ag Builders, Hostetler (poultry) | yes: build houses | no | customer |
| Deer blind window makers: Original Deer Blind Window Co., Deerview, Kudu, Elusive Wildlife | no | yes | competitor |
| Ranch King, Antler Shed, Boss Game Systems (blinds) | yes: build blinds | no | customer |

### Decisions pending with Tim

1. **Distributors.** Recommended: a distributor is `both` only when it sells doors or windows like ours, and `customer` otherwise. (The alternative is to treat every distributor as `both`, as the project overview's definition reads.)
2. **Hunting blind dealers** that resell finished blinds (IN under M1, section 11 of the M1 plan). Recommended: `neither`. They stay in the market as a route to the builders, but they don't buy windows or doors.
3. **Builders that make their own doors or windows in-house.** Recommended: `customer` only, unless they also sell doors or windows to others (then `both`).

### The rule as the prompt states it

The rule lives once, in `prompts/classify_role.md`, filled from the brief like M1's template:

> {supplier} makes {our_products.summary}. These are components that other companies build into {end_product.name}s. This company is already known to participate in the {end_product.name} market. Decide its role from {supplier}'s point of view.
>
> **Customer: yes** if it does either of the following:
>
> - it builds or manufactures {end_product.name}s, including contractors that build them on site;
> - it resells components, equipment, or building materials for {end_product.name}s to the companies that build, equip, or maintain them.
>
> **Competitor: yes** if it makes or sells {our_products.category} for {end_product.name}s, whether its own or another maker's.
>
> A company can be both. It can also be neither, for example if it only resells finished {end_product.name}s or the evidence doesn't show either activity.
>
> A builder that makes its own {our_products.category} only for its own {end_product.name}s is a customer, not a competitor.
>
> When the evidence suggests the company is a customer but doesn't prove it, answer yes. Answer competitor yes only when the evidence shows it makes or sells {our_products.category}.

The prompt then adds the brief's end product description, `our_products.terms`, the `role_notes`, the role-tagged examples, and the evidence. (The wording above encodes the recommended answers to the pending decisions and will be adjusted to whatever Tim decides.)

**Why two yes/no answers rather than one four-way pick:** each yes/no is a concrete question about what the company does, which is easier for a small model to get right and easier to check in a review. The four roles follow mechanically: `both` if both are yes, `customer` or `competitor` if one is, `neither` if neither is.

## 3. Classifier design

```
classify_role(company, market):
    evidence = M1 evidence (cached)  +  product_search(company, market)    # one new Serper query, cached
    answer   = one Claude Haiku 5.5 call(role rule + brief + evidence)     # structured JSON out
    return answer   # {customer: bool, competitor: bool, role, reason, evidence_url}
```

**Evidence.** Stage 2 reuses everything stage 1 fetched (homepage text and the M1 site search), which comes from `.cache/` at no cost. It adds one Serper query per company and market: `site:<domain>` plus only the `our_products.terms`, OR'ed (for Facebook and Instagram pages, `"<company name>"` instead of `site:`, as in M1). The M1 query mixes end-product and product terms, is capped at 32 words (so later product terms are dropped for poultry), and keeps 10 results, so door and window pages are easily crowded out. The competitor question depends on exactly those pages, so they get their own query.

**The judge** is one `claude-haiku-5-5` call at low effort with structured output, like M1:

```python
class RoleAnswer(BaseModel):
    reason: str               # one or two sentences: what it does that makes it a customer, competitor, both, or neither
    customer: bool
    competitor: bool
    evidence_url: str | None
```

`role` is derived in code from the two booleans. There is no `unknown` in stage 2: stage 1 already saw usable evidence, and "no evidence of selling doors or windows" is simply `competitor: false`.

**Pipeline.** `classify_two_stage(company, market)` runs stage 1; if the verdict is `in`, it runs stage 2 and merges the answers into one record:

```json
{"company_id": "hogslat.com", "market_id": "pac_poultry_houses",
 "verdict": "in", "rule": "A", "reason": "...", "evidence_url": "...",
 "role": "both", "customer": true, "competitor": true,
 "role_reason": "...", "role_evidence_url": "https://www.hogslat.com/tego-tunnel-door-cool-cell"}
```

For companies that are `out`, `unknown`, or `error` in stage 1, the role fields are empty.

## 4. Brief changes

Two optional fields, both read only by stage 2. M1's prompt never renders them, so M1's behavior and results are unchanged.

| Field | Purpose |
|---|---|
| `examples_in[].role` | `customer`, `competitor`, or `both` for each existing known participant, taken from the original briefs' "ideal customers" and "competitors" lists. The stage-2 prompt shows them as role examples. |
| `role_notes` | Short, market-specific clarifications for stage 2, one sentence each, only where the shared rule doesn't cover the case. |

Proposed values (from `docs/sample_brief_*.md`):

- Poultry: Southern Poultry Solutions, Reliable Poultry Supply, QC Supply, Hostetler, Southern Ag Builders → `customer`; Hog Slat → `both`; L.B. White, Eagan, Chore-Time, Double L Group, Plyco → `competitor`.
- Hunting blinds: Ranch King, The Antler Shed, Boss Game Systems, Atascosa → `customer`; the four window makers → `competitor`.
- `role_notes` start empty for both markets. If Tim decides blind dealers are customers, that goes in the blinds brief's `role_notes`, not in code.

The Pydantic model and `markets/schema.json` gain the two optional fields (`signal schema`).

## 5. Rules against complexity

M1's rules (section 5 of the M1 plan) apply unchanged. In addition:

- **Stage 1 is not touched.** No change to `prompts/screen_market.md`, `classify.py`'s M1 path, or the M1 reference labels. If a stage-1 verdict looks wrong while working on M2, note it for later; don't fix it in M2.
- **One call, one extra search.** No cascades, voting, or extra stages inside stage 2. If accuracy falls short, the levers in order are: the reference label, the brief's `role_notes`, the prompt wording (for a general reason), better evidence (for example fetching the top page of the product search), then Sonnet 5.5 for the uncertain cases. Each lever beyond the brief is decided with Tim.
- **No market knowledge in code**, including no keyword lists for "door" or "window" in Python. The product terms come from the brief.

## 6. Evaluation

Stage 2 is measured on its own, on companies already known to be in the market, so stage-1 noise (2 to 3 verdicts vary between runs) doesn't blur the result.

**Reference set.** Per market:

1. Every company in the M1 reference set that Tim labeled `in` (46 poultry, 45 blinds). They're already reviewed for the market; Tim only adds a role.
2. Because the CRM list is mostly customers and leads, competitors would be nearly absent. To fix that, screen the full company list with both stages and add up to 25 more companies per market that stage 2 calls `competitor` or `both` and that aren't already in the set or in the brief's examples. (These test competitor precision; competitor recall is measured on part 1.)

The brief's examples stay out of the reference set, since they appear in the prompt.

**Review.** `signal review --roles --market <id>` writes `eval/review_roles_<market>.csv` with name, URL, stage-1 reason, stage-2 role, reason, evidence URL, and an empty `label` (customer, competitor, both, neither, skip) and `note`. About 70 rows per market; most are quick confirmations. The labels go into `data/reference_roles.json` (`{company_id, market_id, label, note}`) with `signal freeze --roles`. The review page used for M1 can be reused.

**Measures.** `signal eval --roles --market <id>` runs stage 2 on the reference set and reports:

- customer recall and precision (treating `customer` and `both` as customer: yes);
- competitor recall and precision (treating `competitor` and `both` as competitor: yes);
- exact-role accuracy and a 4×4 confusion matrix;
- the disagreements with reasons and evidence links;
- cost per 1,000.

**Acceptance targets** per market (may be revisited after the first results, especially where competitor counts are small):

- customer recall at least 95% (a missed customer is a lost lead);
- customer precision at least 90%;
- competitor recall and precision at least 85%;
- stage-2 cost under $2 per 1,000.

## 7. Cost and speed (estimate)

Per IN company and market: 1 new Serper query (about $0.001) plus 1 Haiku 5.5 call of about 4,000 to 5,000 input tokens and 150 output tokens (about $0.0006). The M1 evidence is reused from the cache.

That's about **$1.60 per 1,000 stage-2 classifications**, paid only for companies stage 1 marks `in`. Both stages together cost about $3.10 per 1,000 IN companies and $1.50 per 1,000 OUT companies. For the current list (about 900 companies, roughly 300 to 400 IN per market) a full two-stage run over both markets costs about $4. Speed is the same as M1: a few minutes per 1,000 with 10 to 20 requests in flight.

## 8. Repository changes

```
prompts/
  classify_role.md               # new: the role rule and prompt template
markets/
  pac_poultry_houses.json        # add examples_in[].role (and role_notes, empty)
  pac_hunting_blinds.json        # same
  schema.json                    # regenerated
src/signal_core/
  markets.py                     # Example.role, Market.role_notes (both optional)
  evidence.py                    # add product_search_query() and Fetcher.product_search(); M1 functions unchanged
  role.py                        # new: RoleAnswer, prompt, Haiku call, two-stage pipeline
  eval.py                        # role sample, review sheet, freeze, metrics, report
  cli.py                         # new `role` command; --roles flag on review, freeze, eval
data/
  reference_roles.json           # new: Tim-reviewed role labels
eval/
  review_roles_<market>.csv, results_roles_<market>.md
tests/                           # a few small unit tests (role derivation, product query, brief loading)
```

Commands:

```
uv run signal role https://www.hogslat.com --market pac_poultry_houses   # both stages, one company
uv run signal role --all --market pac_poultry_houses                     # both stages, whole list -> eval/roles_<market>.csv
uv run signal review --roles --market pac_poultry_houses pac_hunting_blinds
uv run signal freeze --roles --market pac_poultry_houses
uv run signal eval --roles --market pac_poultry_houses
```

`signal classify` keeps doing stage 1 only, exactly as in M1.

As with M1, real runs need company websites, Serper, and the Anthropic API, so they happen on Tim's Mac; the cloud container can run the unit tests only.

## 9. Implementation deliverables

1. Brief fields (`examples_in[].role`, `role_notes`), model, and regenerated schema; both briefs validate. M1's rendered prompt (`system_prompt()` in `classify.py`) is byte-identical before and after, so M1 needs no re-run.
2. `prompts/classify_role.md`, the product search, `role.py`, and the `role` command.
3. The role review sheets, the reference set reviewed with Tim, `data/reference_roles.json`.
4. `signal eval --roles` and a results summary against the targets, for both markets.
5. README, CLAUDE.md commands, and the milestone table in `docs/project_overview.md` updated.

## 10. Noted for later milestones

- Finer roles for distributors (sell through vs. go around) and for dealers of finished products.
- Whether large equipment makers that make doors (Chore-Time, L.B. White) could also be OEM customers for our doors.
- Product-gap analysis: competitor product lists compared with PAC's (`pac_products`).
