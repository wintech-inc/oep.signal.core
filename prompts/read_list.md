You read one web page and extract every company it names or lists: directory entries, association members, dealers, distributors, suppliers, exhibitors, partners, companies in a "top 10" article, and so on. The page text shows each link inline after its text, like `Acme Co [https://acme.com]`.

Extract every company on the page, not only ones that seem relevant: another step judges them. Leave out the company whose website this is, people who are not businesses, and pure navigation (Home, About, Contact).

For each company:

- `name`: the company name as the page shows it.
- `url`: the company's own website or social media page, if the page links to it or shows it (a link next to the name, or an email address such as info@acme.com, which gives https://acme.com). Use null when the page only links to its own profile page for the company, or shows no link.
- `location`: the company's town as "Town, ST" (two-letter state or province code) if the page shows it, otherwise null.

Also return `more_pages`: up to 5 links on this same website to more of the same list (the next page, other letters, other categories, other regions), if there are any. Otherwise an empty list.

If the page lists no companies, return empty lists.
