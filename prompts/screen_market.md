You screen companies for a B2B market map. For one company, decide from the evidence whether it participates in the market defined below.

# The market

{supplier} makes {our_products.summary}. These are components that other companies build into {end_product.name}s.

A company is **IN** this market if it does at least one of the following:

- **A. Builds the end product.** It manufactures or builds {end_product.name}s, including contractors that build them on site.
- **B. Distributes components for it.** It sells components, equipment, or building materials specifically for {end_product.name}s to the companies that build, equip, or maintain them.
- **C. Makes products like ours for it.** It makes {our_products.category} for {end_product.name}s.

Otherwise the company is **OUT**. In particular, these are OUT unless they also do A, B, or C:

- companies that make *other* products used in or around {end_product.name}s;
- companies that only own, use, or operate {end_product.name}s;
- dealers and retailers that resell finished {end_product.name}s to end users;
- companies in the broader industry that are not tied to {end_product.name}s.

A company based outside the market's geography is also **OUT**, whatever it does (see Geography below).

If the evidence doesn't show what the company does, answer **UNKNOWN**. When the evidence is suggestive but not conclusive, lean toward IN.

# The end product: {end_product.name}

{end_product.description}

Not included:
{not_included}

# Geography

{geography}

Judge where the company is based from the evidence: its address, phone numbers, domain, language, and where it says it works. A company with its own office, branch, or subsidiary inside the geography counts as based there. If the evidence doesn't show where it is based, don't let geography decide the verdict.

# Products like ours

{our_products.summary}. Related terms: {our_terms}.

# Notes for this market

{notes}

# Known participants

{examples}

# How to answer

- `reason`: one sentence on what the company does and why that puts it IN or OUT.
- `verdict`: `in`, `out`, or `unknown`.
- `rule`: the rule (`A`, `B`, or `C`) that makes it IN, or null when it is not IN.
- `evidence_url`: the URL from the evidence that best supports the verdict, or null.

Judge the company itself, not the other companies that appear in its search results.
