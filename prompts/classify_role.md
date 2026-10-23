You classify companies for a B2B market map. One company, already known to participate in a market, is described below. From the evidence, decide which of five activities it does in the {end_product.name} market, and write a short comment about it for a salesperson.

# The activities

{supplier} makes {our_products.summary}. These are components that other companies build into {end_product.name}s. This company is already known to participate in the {end_product.name} market.

Answer each activity yes or no, on its own. A company can do several.

1. `makes_end_product`: it builds or manufactures {end_product.name}s, including contractors that build them on site.
2. `makes_component`: it makes {our_products.category} for {end_product.name}s and sells them to other companies.
3. `resells_component`: it resells {our_products.category} for {end_product.name}s that other companies make. A dealer, distributor, or store that stocks another maker's {our_products.category} for {end_product.name}s does this.
4. `resells_end_product`: it resells finished {end_product.name}s that other companies make.
5. `resells_supplies`: it resells other parts, equipment, or building materials for {end_product.name}s, made by other companies, to the companies that build, equip, or maintain them.

Resell means selling products that other companies make. A company that sells only what it makes itself does not resell. A dealer or store that sells another company's branded {end_product.name}s resells them and does not make them, even when its listing says it "builds and sells" them or it delivers and sets them up.

A builder that makes its own {our_products.category} only for its own {end_product.name}s, including replacement parts for them, does not make them for others: `makes_component` is no. If it also sells them on their own to other companies, `makes_component` is yes.

When the evidence suggests the company builds {end_product.name}s, or resells parts, equipment, or materials for them, but doesn't prove it, answer yes. Answer `makes_component` or `resells_component` yes only when the evidence shows {our_products.category}.

# The end product: {end_product.name}

{end_product.description}

# Products like ours

{our_products.summary}. Related terms: {our_terms}.

# Notes for this market

{role_notes}

# Known companies and their roles

The role is the first of these that applies: Manufacturer (makes the end product), Component Manufacturer (makes {our_products.category} for it), Component Reseller (resells {our_products.category} for it), Reseller (resells the finished end product), Supply Reseller (resells other parts or supplies for it), Adjacent (none of these).

{examples}

# How to answer

- `name`: the company's proper name as its own pages or listings give it, for example "Reliable Poultry Supply", not "Reliable Poultry Supply's post" or "reliablepoultry.com". If the evidence doesn't show which company this is (for example a post or article title that names no company), null.
- `website`: the company's own website (its homepage URL) as the evidence shows it, else null. Not a social media page, directory, marketplace, news site, or another company's site.
- `city`, `state`, `country`: where the company is based (its main office), as the evidence shows it, else null. For a US company, `state` is the two-letter code and `country` is "US".
- For each activity, `yes` (true or false) and `evidence_url`: when yes, the URL from the evidence that best shows it; when no, null. Use only URLs that appear in the evidence.
- `comment`: one or two plain sentences for a salesperson: what the company does in the {end_product.name} market, and its other activities there if it has several (for example "Also makes and sells its own tunnel doors."). Say only what it does, not what it doesn't do: mention {our_products.category} only when it makes, sells, or builds with them. If what it does is uncertain, say so in a word or two ("appears to build"). Write plain words: no rule letters or field names, and never words like "evidence", "listing", "source", or "page".

Judge the company itself, not the other companies that appear in its search results.
