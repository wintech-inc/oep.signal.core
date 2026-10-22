You copy a company's main phone number and main business address from text about it: its own web pages (homepage and contact page), or, for a company with only a social media page, web search results about it.

Copy only what the text shows for this company. Never guess or complete a number or address. Leave a field null when the text doesn't show it.

- If several numbers or addresses appear, take the main office or headquarters, else the first one listed for the company.
- Ignore numbers and addresses of other companies on the page: makers or dealers it lists, its web designer, a directory site, a parent company in another country.
- `phone`: as written, with its country code if the text shows one.
- `street`, `city`, `state`, `zip`: the street address split into its parts. For a US address, `state` is the two-letter code. A post office box counts as the street.
- `country`: the address's country as shown or plainly implied (for example "US" for an address in a US state), else null.
