-- Customer review and engagement analysis.

-- 1. Customers who submitted reviews.
SELECT
  c.customer_id,
  c.customer_zipcode,
  COUNT(r.review_id) AS review_count
FROM customer c
JOIN review r
  ON c.customer_id = r.customer_id
GROUP BY c.customer_id, c.customer_zipcode
ORDER BY review_count DESC;

-- 2. Loyalty customers with review activity.
SELECT
  t.tier_level,
  COUNT(DISTINCT c.customer_id) AS reviewing_customers
FROM customer c
JOIN loyalty l
  ON c.loyalty_id = l.loyalty_id
JOIN tier t
  ON l.tier_id = t.tier_id
JOIN review r
  ON c.customer_id = r.customer_id
GROUP BY t.tier_level
ORDER BY reviewing_customers DESC;

-- 3. Review coverage rate across the customer base.
SELECT
  COUNT(DISTINCT r.customer_id) AS customers_with_reviews,
  COUNT(DISTINCT c.customer_id) AS total_customers,
  ROUND(
    100.0 * COUNT(DISTINCT r.customer_id) / COUNT(DISTINCT c.customer_id),
    2
  ) AS review_participation_pct
FROM customer c
LEFT JOIN review r
  ON c.customer_id = r.customer_id;
