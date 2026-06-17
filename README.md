# Grocery Loyalty DBMS & SQL Analytics

<p>
  <img src="assets/badges/sql.svg" alt="SQL Design">
  <img src="assets/badges/sqlite.svg" alt="SQLite DBMS">
  <img src="assets/badges/erd.svg" alt="ERD Modeling">
  <img src="assets/badges/portfolio-ready.svg" alt="Portfolio Ready">
</p>

An advanced DBMS portfolio project designing and analyzing a grocery-store loyalty ecosystem across customers, stores, locations, promotions, rewards, loyalty tiers, and customer reviews.

## Live Dashboard

View the executive database case-study dashboard:

[https://amy-way05.github.io/grocery-loyalty-dbms-sql-design/](https://amy-way05.github.io/grocery-loyalty-dbms-sql-design/)

## Executive Snapshot

This project models a retail loyalty program as a relational database and demonstrates how SQL can support customer engagement, store performance, promotion planning, and reward strategy. The database contains **8 relational tables** and supports analysis across customer enrollment, loyalty tiers, promotions, rewards, store locations, and review activity.

## Database Scale

| Entity | Rows |
|---|---:|
| Customers | 1,000 |
| Loyalty Accounts | 212 |
| Promotions | 36 |
| Rewards | 28 |
| Reviews | 20 |
| Stores | 5 |
| Locations | 3 |
| Loyalty Tiers | 3 |

## Business Questions

- Which loyalty tiers have the strongest participation?
- How are stores distributed across locations?
- Which stores have the highest review and promotion activity?
- What reward structures exist across loyalty tiers?
- How can customer, loyalty, review, promotion, and store data be joined for business reporting?
- Where are the strongest opportunities for customer engagement and retention?

## Data Model

The database is organized around a retail loyalty program:

```text
CUSTOMER  -> LOYALTY -> TIER -> REWARD
CUSTOMER  -> REVIEW  -> STORE -> LOCATION
STORE     -> PROMOTION
```

Core design concepts demonstrated:

- Entity relationship modeling
- Relational schema design
- Primary and foreign key planning
- Join-based reporting
- Aggregation and segmentation
- Retail loyalty analytics

## Featured SQL Insights

### Loyalty Tier Participation

The project includes SQL to calculate loyalty account distribution and average point balances by tier. This supports retention analysis and helps identify which membership levels drive the most engagement.

### Store Activity View

Store-level queries combine promotions and customer reviews to understand which stores have stronger customer-facing activity.

### Reward Strategy

Reward queries compare reward availability and cost by tier, showing how benefits scale across loyalty levels.

### Customer Engagement

Customer, loyalty, and review joins create a foundation for engagement scoring and targeted promotion planning.

## Repository Structure

```text
.
├── assets/                 # ERD image and editable diagram files
├── database/               # Local SQLite database, if included
├── docs/                   # Data dictionary and methodology
├── outputs/                # Query output examples and insight tables
├── queries/                # SQL analysis files
├── reports/                # Original project PDFs, if included
├── schema/                 # Database schema and design notes
├── scripts/                # Local validation helpers
└── README.md               # Project overview
```

## How To Use

Open the SQLite database in DB Browser for SQLite, SQLiteStudio, or the command line:

```bash
sqlite3 database/ITC6000_GRP_PRJT.db
```

Run schema and analysis files:

```bash
.read schema/create_tables.sql
.read queries/loyalty_analysis.sql
.read queries/store_performance_analysis.sql
.read queries/reward_strategy_analysis.sql
```

## Portfolio Value

This project shows more than basic SQL. It demonstrates how to move from business context to relational design, then from relational design to analysis-ready queries and stakeholder-facing insights.

## Data Privacy

The original database appears to contain customer-style records such as names, phone numbers, emails, and zip codes. Before publishing this repository publicly, include only synthetic or approved sample data. The schema, queries, ERD, and aggregate outputs can be shared safely.

## License

Released under the MIT License. See [LICENSE](LICENSE).
