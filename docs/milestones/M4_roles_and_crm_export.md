# M4: Market roles and CRM export

Status: agreed with Tim on 2026-10-22 in the M4 planning thread. Implementation happens in a separate thread.

Background and definitions: [project_overview.md](../project_overview.md). The stages this builds on: [M1_market_classifier.md](M1_market_classifier.md), [M2_role_classifier.md](M2_role_classifier.md), [M3_company_discovery.md](M3_company_discovery.md).

## 1. Goal

M1 to M3 give a basic working system: a market classifier that mostly works and a discovery run that finds several times more in-market companies than the CRM had. Before the core grows further, the output has to reach the sales and marketing team, for their review and feedback and for selling.

M4 does two things:

1. **Replace stage 2's customer / competitor answer with the company's role in the market**, in terms a salesperson acts on: does it make the end product, resell it, make doors or windows for it, or resell doors or windows or other supplies for it?
2. **Export a CSV that imports into the CRM** through the existing SIGNAL import page, with company, homepage, address, phone, role, and a short comment saying why the company is on the list.

The sales team can then filter on role. The lead list is the companies that make the end product and the companies that resell doors, windows, or other supplies to them (section 2).

**Stage 1 (M1) does not change.** Its prompt, including the geography rule added in M3, its code path, and its reference labels stay as they are. Discovery (M3) keeps running both stages as a black box; only stage 2 inside it changes.

**Out of scope for M4:** a database, UI, people and contact names, pushing to the CRM through an API, running discovery to saturation, better evidence gathering for M1, and the graph of links between companies. These are noted in section 10.

## 2. The roles

Stage 2 still runs only on companies stage 1 marks `in`. It now answers which of these activities the company does in the market, from {supplier}'s point of view.

Two words carry the scheme, and each means one thing:

- **Manufacturer** makes something.
- **Reseller** sells products that other companies make. "Dealer", "distributor", "supply store", and "retailer" all fall under it; for sales the difference between them doesn't matter, so the role names don't use those words.

**Component** means the products like ours that the brief names (`our_products`): doors and windows for both PAC markets. The role names stay the same in every market, so the CRM can filter on them across divisions; the brief says what "component" means for each.

| Role (CRM value) | The company... | Example |
|---|---|---|
| **Manufacturer** | makes {end_product.name}s, including contractors that build them on site | Ranch King, Southern Ag Builders |
| **Reseller** | resells finished {end_product.name}s made by others | a shed lot or hardware store selling Sportsman's Condo blinds |
| **Component Manufacturer** | makes {our_products.category} for {end_product.name}s and sells them to others | Deerview Windows, Eagan, Plyco |
| **Component Reseller** | resells other makers' {our_products.category} for {end_product.name}s | a poultry supply store stocking another maker's tunnel doors |
| **Supply Reseller** | resells other parts, equipment, or building materials for {end_product.name}s, but not {our_products.category} | Reliable Poultry Supply, QC Supply |
| **Adjacent** | is in the market but fits none of the above | a fan or feeder maker M1 let in, or thin evidence |

Supply Reseller is Tim's "Other Distributor": poultry supply stores and equipment dealers, the brief's ideal customers, 88 of the 279 in-market poultry companies today. They sell into the market but don't (yet) carry doors or windows. Keeping them apart from Component Resellers keeps that signal in the Role column, and the pitch differs: "switch to our doors" for a Component Reseller, "add our doors to your line" for a Supply Reseller.

**Lead roles:** Manufacturer, Component Reseller, and Supply Reseller. Reseller, Component Manufacturer, and Adjacent are still exported; sales can filter them out.

### One role per company (agreed with Tim)

A company can do several of these things. Hog Slat builds poultry houses, distributes equipment, and sells its own tunnel door. Earlier iterations allowed several roles per company, which added complexity and confusion, so each company gets exactly one: the first that applies in this order.

1. Manufacturer
2. Component Manufacturer
3. Component Reseller
4. Reseller
5. Supply Reseller
6. Adjacent (none of the above)

(Tim, 2026-10-22, after the first export: Reseller now comes before Supply Reseller. In hunting blinds, about 270 gun shops, feed stores, and shed lots that resell finished blinds plus stands and accessories were landing in the lead role Supply Reseller; they are dealers, and his M2 call was that dealers aren't leads. Poultry is unaffected.)

Making the end product comes first because it makes the company a customer however else it is involved. The Comments column names the other activities ("also makes and sells its own tunnel doors"), and the internal sheet keeps every activity flag (section 3), so nothing is lost.

### How the M2 decisions carry over

| M2 decision or result | M4 role |
|---|---|
| Hunting blind dealers that resell finished blinds: `neither` | Reseller |
| Distributor is `both` only with evidence it carries doors or windows like ours | Component Reseller with that evidence, Supply Reseller without it |
| Reseller of another maker's doors or windows: `both` (prompt rule added in M2) | Component Reseller |
| Builder that makes its own doors or windows only for its own product: `customer` | Manufacturer (making its own windows doesn't count as selling them) |
| Builder that also sells its own windows standalone: `both` (Lazy Man Stands) | Manufacturer; Comments says it also sells windows |
| Door and window makers (Eagan, Plyco, Deerview, Kudu): `competitor` | Component Manufacturer |
| Large equipment makers that offer doors (Chore-Time, L.B. White): `competitor` | Component Manufacturer |
| Hog Slat: `both` | Manufacturer; Comments says it also makes tunnel doors |
| In the market on thin or suggestive evidence: `neither` | Adjacent |

Customer and competitor stay derivable from the flags (customer: makes the end product or resells components or supplies; competitor: makes or resells components) if anything later needs them.

## 3. Classifier design

Same shape as M2: one Claude Haiku 5.5 call per in-market company and market, at low effort with structured output, over the cached M1 evidence plus M2's product search (both already cached for every company classified so far). Each activity is a concrete yes/no question about what the company does, which a small model answers more reliably than a six-way pick, and the role follows mechanically.

```python
class Activity(BaseModel):
    yes: bool
    evidence_url: str | None      # the page that shows it, required when yes

class RoleAnswer(BaseModel):
    name: str                       # the company's proper name as its own pages give it
    makes_end_product: Activity     # makes the end product                          -> Manufacturer
    makes_component: Activity       # makes doors/windows for it, sold to others      -> Component Manufacturer
    resells_component: Activity     # resells other makers' doors/windows for it      -> Component Reseller
    resells_supplies: Activity      # resells other parts, equipment, materials for it -> Supply Reseller
    resells_end_product: Activity   # resells finished end products made by others    -> Reseller
    comment: str                    # one or two plain sentences for a salesperson
```

`role` is derived in code from the flags using the order in section 2. As in M2, a yes whose URL isn't in the evidence is kept and flagged as weak in the eval.

**The prompt** (`prompts/classify_role.md`, rewritten) states the five activities with the brief's placeholders, keeps M2's two clarifications (a builder's own doors or windows, including replacement parts, don't make it a Component Manufacturer; a dealer or store that stocks another maker's doors or windows is a Component Reseller), and asks for the comment in plain words: what the company does in the {end_product.name} market and why it has its role, naming its other activities, with no rule letters or internal terms. This is the review summary text Tim liked, written for sales.

**`name`** fixes company names that discovery took from page titles and social posts ("Reliable Poultry Supply's post", "newtoncrouch.com"). It costs a few output tokens.

**Brief changes.** `examples_in[].role` takes the new role values (proposed: poultry Southern Poultry Solutions, Reliable Poultry Supply, QC Supply → Supply Reseller; Hostetler, Southern Ag Builders, Hog Slat → Manufacturer; L.B. White, Eagan, Chore-Time, Double L Group, Plyco → Component Manufacturer; blinds Ranch King, Antler Shed, Boss Game Systems, Atascosa → Manufacturer; the four window makers → Component Manufacturer). The blinds `role_notes` line about dealers is removed, since Reseller is now a role. One new field, `crm_target` ("PAC"), for the Target column; the existing `crm_market` ("Poultry", "Hunting Blinds") becomes the Division column. `signal schema` regenerates the schema.

**Caching.** Discovery's verdict cache key today hashes the stage-1 and stage-2 prompts together, so changing the stage-2 prompt would re-run stage 1 on every candidate (about 35,000, roughly $50). The key is split so a stage-2 change re-runs stage 2 only, on in-market companies.

## 4. Address and phone

**Source: one Google Maps lookup per exported company, through Serper's places search,** which discovery already uses. Maps listings are where a business's primary address and main phone are kept current, and Serper returns both as fields. No new API key, account, or vendor.

- Query: `<name> <town, state>` when the town is known, else the name.
- Match: the same rule discovery's `locate` step already uses (the listing's website has the company's key, or the names contain one another).
- Take the listing's address, split into Street address, City, State, and ZIP, and its phone number. Service-area businesses often list only a town; then Street address and ZIP stay blank.
- No match means blank fields, not a guess. The report counts how many rows have each field.
- Cached per company, so re-exports cost nothing.

A state outside the market's geography (for example a Canadian province) puts the company out through M3's existing geography gate, so it is not exported.

**Fallback, noted but not built:** reading the address and phone from the homepage text stage 1 already fetched (footers often have both). Decide after seeing the fill rate.

## 5. The export

```
signal export --market <id>
    in-market companies from the discovery run (data/discovery/<id>.json)
    stage 2 (new roles) for any whose role is from an older prompt        # cached
    maps lookup for any without one                                       # cached
    geography gate on the found address
    merge duplicates
    -> exports/crm_<id>.csv      (the CRM file)
    -> eval/leads_<id>.csv       (the internal sheet: every flag, evidence URL, source)
```

**Columns, in this order:**

| Column | Value |
|---|---|
| Company | `name` from stage 2 |
| Homepage | own domain: `https://` plus the host, no path. Social-only company: its Facebook (or Instagram) page. A social-only company whose maps listing gives its own website gets that website |
| Target | `crm_target` from the brief ("PAC") |
| Division | `crm_market` from the brief ("Poultry", "Hunting Blinds") |
| Role | section 2 |
| Street address, City, State, ZIP, Phone | section 4 |
| Comments | stage 2's `comment`, then "Source: <evidence URL of the role>" |
| Lead Source | "SIGNAL" |

**Duplicates.** Discovery sometimes holds a company twice, typically its Facebook page and its website ("Strand Ag Supply" and strandagsupply.com). Two rows whose maps listing is the same place (same phone number, or the listing's website is the other row's domain) are one company: keep the own-domain row. This needs no extra calls, since the maps lookup is done anyway.

Every in-market company is exported, including those already in the CRM (the seed list); the import page decides how to match existing records.

## 6. Rules against complexity

M1's and M2's rules apply unchanged. In addition:

- **Stage 1 is not touched.** No change to `prompts/screen_market.md` or its code path. M1 verdicts that look wrong are noted for later.
- **One call per company for the role, one maps lookup for the address.** No cascades, voting, or extra stages. If role accuracy falls short, the levers in order are: the reference label, the brief's `role_notes`, the prompt wording for a general reason, better evidence, then Sonnet 5.5. Each lever beyond the brief is decided with Tim.
- **No market knowledge in code**, including no keyword lists for roles. Role names and the precedence order are the only fixed lists, and they are the same for every market.
- **Blank beats wrong.** Missing address or phone stays blank.

## 7. Evaluation

**Changed by Tim on 2026-10-22, after the first real export:** Tim does not relabel the role reference set or check the contact spot sample. The judges are the sales and marketing team, who call these companies and can say whether a role or a phone number is right. Feedback from sales replaces the targets below for M4. The tooling stays (`signal review|freeze|eval --roles`, `signal eval --contacts`, and the sheets in `eval/review_roles_*` and `eval/review_contacts_*`) for when feedback arrives. Until then `data/reference_roles.json` still holds M2's customer/competitor labels, so `signal eval --roles` doesn't mean anything yet.

The first export (both markets, $2.07): poultry 252 companies, 229 in lead roles, phone filled for 81% and street address for 61%; hunting blinds 947, 805 in lead roles, phone 73% and street address 34%. See `eval/export_<market>.md`.

A review of that export before the real upload (`/mnt/project-files/m4/export_review.md` in the project files) found: blind dealers in a lead role (fixed by the role order above); dealers of a brand called makers; about 140 homepages that weren't the company's own site (directory pages, or a wrongly matched map listing's site); contacts from same-named businesses in other states; foreign companies with no US address to gate on; phones missing where the website shows one; social pages duplicating a website row. The fixes, all general: stage 2 also returns the company's own website (kept only if it appears in the evidence) and where it is based, and a sentence that selling another company's brand is reselling; the export looks the company up in stage 2's town, rejects a listing in another state or with another company's website, gates on stage 2's country and on non-US phone codes and addresses, reads a missing phone or address from the company's own homepage and contact page (one web search for social-only companies), drops pages stage 2 can't tie to a named company, and merges a social page whose handle is a row's domain.

The plan as agreed before that change:

**Role reference set.** The M2 reference set (100 companies, Tim-labeled) is relabeled with the new roles, plus up to 10 companies per market for each role the set lacks (likely Reseller, Supply Reseller, and Component Reseller), sampled from the discovery list where the new stage 2 gives that role, to test precision. `signal review --roles` writes the sheet with the model's role and comment; Tim confirms or corrects on the review page as in M2. About 120 to 140 rows per market, mostly quick confirmations. `signal freeze --roles` replaces `data/reference_roles.json`.

**Measures** (`signal eval --roles`):

- lead recall and precision (lead roles: Manufacturer, Component Reseller, Supply Reseller);
- exact-role accuracy and the 6×6 confusion matrix, with the disagreements, reasons, and evidence links;
- yes answers without an evidence URL;
- cost per 1,000.

**Contact data.** Fill rate per column, and a spot check of 25 exported rows per market (with a link to the maps listing): is each filled field right?

**Targets** per market (may be revisited after first results, as in M2):

- lead recall at least 95% (a missed lead is lost);
- lead precision at least 90%;
- exact-role accuracy at least 85%;
- stage-2 cost under $2 per 1,000;
- at least 90% of filled address and phone fields right in the spot check;
- `exports/crm_<id>.csv` imports through the CRM import page without edits (Tim tries a small file first).

## 8. Cost and speed (estimate)

- Stage 2 on the current in-market companies (1,060 blinds, 279 poultry): about $1.60 per 1,000, so about $2.20. The output grows by roughly 100 tokens for the comment and name.
- Maps lookups: about 1,340 Serper places queries, around $1 to $4 depending on Serper's credit price for places.
- Eval runs: under $1.

M4 should cost under $10 in API and search spend, and a full export of both markets takes minutes.

## 9. Repository changes

```
prompts/classify_role.md         # rewritten: five activities, comment, name
markets/*.json, schema.json      # new role values in examples_in, crm_target, blinds role_notes trimmed
src/signal_core/markets.py       # Example.role values, Market.crm_target
src/signal_core/role.py          # RoleAnswer with activities; role derived by precedence
src/signal_core/evidence.py      # places() keeps phone and full address
src/signal_core/discover.py      # verdict cache split by stage; leads sheet and report use the new roles
src/signal_core/export.py        # new: maps lookup, address split, duplicate merge, CRM CSV
src/signal_core/eval.py          # role review, freeze, metrics for the new roles; contact spot check sheet
src/signal_core/cli.py           # `signal export`
data/reference_roles.json        # relabeled
exports/crm_<market>.csv         # the files for sales
README.md, CLAUDE.md             # commands updated (`signal role` description, `signal export`)
tests/                           # a few small unit tests: role precedence, address split, homepage form, merge
```

Real runs happen on Tim's Mac via Remote Control, as before; the cloud container runs the unit tests only.

## 10. Noted for later milestones

- Running both markets to saturation (M3 left blinds and poultry unsaturated).
- Better evidence gathering for M1 (site search misses pages; several poultry misses).
- Reading address and phone from the company's own pages when maps has no listing.
- Dealers of finished blinds that are a route to builders (Amish networks).
- Whether large equipment makers that make doors could also be OEM customers.
- Sales feedback on roles and comments, fed back into the brief's `role_notes` and examples.
