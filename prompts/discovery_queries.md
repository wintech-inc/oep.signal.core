You write the web and map searches that find every company in a B2B market. A person will not run these by hand: software runs each one on Google web search and Google Maps, nationally and in every US state, and pages deep into the results. Every company found is checked against the market definition afterwards, so the searches should cast a wide net. A search that also returns unrelated companies is fine; a phrasing that misses a group of real companies is not.

# The market

{supplier} makes {our_products.summary}. These are components that other companies build into {end_product.name}s. A company is in this market if it does at least one of the following:

- **A.** It manufactures or builds {end_product.name}s, including contractors that build them on site.
- **B.** It sells components, equipment, or building materials specifically for {end_product.name}s to the companies that build, equip, or maintain them.
- **C.** It makes {our_products.category} for {end_product.name}s.

## The end product: {end_product.name}

{end_product.description}

Terms: {end_terms}

Not included:
{not_included}

## Products like ours

{our_products.summary}. Terms: {our_terms}

## Notes

{notes}

## Known participants

{examples}

# What to write

- `company_queries` (about 25): searches that return companies directly, phrased the way people actually type them ("hunting blind manufacturer", "who makes deer blinds", "box blind builder", "poultry house construction company", "poultry equipment supply store"). Cover rules A, B, and C, every common name for the end product, the kinds of companies that build it (manufacturers, builders, contractors, shed and building companies that also build it), the dealers, stores, and suppliers that sell to them, and the makers of products like ours. Don't put a place in them; the software adds "in <state>" or "near <town>".
- `nearby_queries` (about 5): short, broad searches used on maps and web around each town where a company in the market was found ("hunting blinds", "poultry house builder").
- `list_queries` (about 20): searches that find pages listing many companies: directories, association and member lists, dealer and distributor lists, trade show exhibitor lists, buyer's guides, and "top 10" or "best of" articles.
- `list_terms` (about 7): words that name the pages on a company's own website that list other companies ("dealers", "distributors", "where to buy", "partners", "members", "links", "suppliers").

Plain words only: no quotes, no `site:`, no OR.

{existing}
