# Methodology

## 1. Business Framing

The project models a grocery store loyalty program, where customers can enroll in loyalty tiers, earn points, redeem rewards, interact with store promotions, and leave reviews.

## 2. Entity Design

The schema separates business concepts into 8 core entities:

- Customer
- Loyalty
- Tier
- Reward
- Store
- Location
- Promotion
- Review

This avoids one large flat table and supports scalable reporting through joins.

## 3. Relationship Design

Key relationships include:

- A customer may have one loyalty account.
- A loyalty account belongs to one tier.
- A tier can offer many rewards.
- A store belongs to one location.
- A store can run many promotions.
- A customer can leave reviews for stores.

## 4. Query Design

SQL files are grouped by analytical use case:

- `loyalty_analysis.sql` for membership and tier participation.
- `store_performance_analysis.sql` for store, location, promotion, and review reporting.
- `reward_strategy_analysis.sql` for reward availability and cost structure.
- `customer_review_analysis.sql` for engagement and review participation.

## 5. Public Sharing Approach

Because the original database includes customer-style details such as names, phone numbers, emails, and zip codes, this repository is structured to showcase schema, SQL, ERD, and aggregate insights. Raw customer-level data should be excluded from public publishing unless it is synthetic or approved for release.
