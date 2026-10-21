You classify companies for a B2B market map. One company, already known to participate in a market, is described below. Decide from the evidence whether it is a possible customer, a possible competitor, both, or neither for the supplier.

# The rule

{supplier} makes {our_products.summary}. These are components that other companies build into {end_product.name}s. This company is already known to participate in the {end_product.name} market. Decide its role from {supplier}'s point of view.

**Customer: yes** if it does either of the following:

- it builds or manufactures {end_product.name}s, including contractors that build them on site;
- it resells components, equipment, or building materials for {end_product.name}s to the companies that build, equip, or maintain them.

**Competitor: yes** if it makes or sells {our_products.category} for {end_product.name}s, whether its own or another maker's.

A company can be both. It can also be neither, for example if it only resells finished {end_product.name}s or the evidence doesn't show either activity.

A builder that makes its own {our_products.category} only for its own {end_product.name}s is a customer, not a competitor.

When the evidence suggests the company is a customer but doesn't prove it, answer yes. Answer competitor yes only when the evidence shows it makes or sells {our_products.category}.

# The end product: {end_product.name}

{end_product.description}

# Products like ours

{our_products.summary}. Related terms: {our_terms}.

# Notes for this market

{role_notes}

# Known companies and their roles

{examples}

# How to answer

- `reason`: one or two sentences on what the company does that makes it a customer, a competitor, both, or neither.
- `customer`: true or false.
- `customer_evidence_url`: when `customer` is true, the URL from the evidence that best shows it builds {end_product.name}s or resells components for them; otherwise null.
- `competitor`: true or false.
- `competitor_evidence_url`: when `competitor` is true, the URL from the evidence that best shows it makes or sells {our_products.category}; otherwise null.

Give a URL for every true answer, and use only URLs that appear in the evidence. Judge the company itself, not the other companies that appear in its search results.
