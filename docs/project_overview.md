# SIGNAL project overview

SIGNAL (Sales Intelligence Graph for Networked Accounts and Leads) is a market intelligence tool for the sales teams of Ozark ESOP Partners (OEP). This document records the project's background and goals as Tim (OEP Chief Strategy Officer, WinTech CIO) described them at the start of iteration 13.

## Who it's for

OEP is a newly formed ESOP holding company with two operating companies today:

- **WinTech ("WT")**, https://www.wintechinc.com
- **Pocahontas Aluminum ("PAC")**, https://www.pocahontasaluminum.com

Both are **component suppliers**: they make windows and doors that other companies build into an end product. That end product might be a commercial HVAC unit (WinTech doors), a poultry house (a PAC bi-fold door), or a manufactured home (a PAC vinyl window).

## The problem

Since acquiring PAC, the sales team has struggled to find new leads on its own. Paid lead sources and lead generation tools (for example Seamless.ai) raised spend without producing results.

Lead generation is hard because the markets are niche. For example, PAC wants to sell aluminum doors (such as bi-fold doors) into the poultry house market. Its customers are the companies that build commercial poultry houses or distribute components for them. The poultry industry is large, but identifying which companies are customers or competitors has proven very difficult.

## What SIGNAL is

A market intelligence platform holding markets, products, channels, customers, and competitors. Over time the data store should hold a near-complete list of the participants in each target market. That data can then be used to:

- build lead lists;
- research competitors;
- spot product gaps (a competitor offers product X and we don't);
- find new, untapped markets.

The core loop, simple in theory and hard in practice:

1. Search for companies in a target market.
2. Classify each as a potential customer or a potential competitor.
3. Use what we learn about those companies to find more companies (a customized semantic crawler).
4. Build a map of customers and competitors that covers the market.
5. Add product and contact information.
6. Provide a searchable, interactive database for finding customers and spotting product gaps.

## Key definitions

- **End product:** the thing our component goes into (a poultry house, a hunting blind).
- **Customer:** a company that manufactures the end product (and chooses its component vendors), or a distributor that resells components to those manufacturers.
- **Competitor:** a company that does what we do: sells similar products to the same buyers in that market.
- **Distributor:** both a potential customer and a potential competitor. Sales often has to decide whether to work through a distributor or go around it to the distributor's customers.
- **Market:** the collection of customers and competitors for one end product, from our point of view.

## Prototype goal

Lead generation: find potential customers, get their contact information, and get it to someone in sales. The list should be comprehensive enough that it represents the bulk of the market. We should be unlikely to find a meaningful number of potential customers that are *not* in the database.

## Lessons from iterations 1 to 12

- Early stages worked; things failed at scale. Results were either a large list of very poor quality (Amazon.com, HGTV, and a maker of toy chickens all showed up in one run), or so strict that almost everything was rejected (for example, "only 5 companies in Texas" could be customers).
- The two most critical components, **classification** (judging a company correctly) and **search** (finding companies to classify), were also the two that failed.
- Implementations lost sight of the big picture. Whether the design was heavily specified or not, the work turned into passing ever more labyrinthine test cases. Each problem added complexity until the whole effort collapsed.
- Doing customer vs. competitor classification immediately caused problems. In iteration 13, deciding whether a company is in the market comes first and the role comes later.
- The CRM export is reference data only. Earlier iterations treated its labels as ground truth; they are unreliable at best and adversarial at worst.

## How iteration 13 is run

- Repository `wintech-inc/oep.signal.core`, branch `version-13.0`.
- Work is split into milestones M1 to Mn. Each ends with a PR merged into `version-13.0`.
- For each milestone, a planning thread agrees the plan with Tim and writes it to `docs/milestones/`. A separate implementation thread then builds it. Trivial milestones may be done in one thread.
- Keep designs simple and focused on the big picture.

## Milestones

| Milestone | Goal | Plan |
|---|---|---|
| M1 | Market classifier: does a company participate in a market as we define it? | [M1_market_classifier.md](milestones/M1_market_classifier.md) |
