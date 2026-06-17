-- Loyalty participation and engagement analysis.

-- 1. Overall loyalty penetration.
SELECT
  COUNT(*) AS total_customers,
  SUM(CASE WHEN loyalty_id IS NOT NULL THEN 1 ELSE 0 END) AS loyalty_customers,
  ROUND(
    100.0 * SUM(CASE WHEN loyalty_id IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*),
    2
  ) AS loyalty_penetration_pct
FROM customer;

-- 2. Loyalty distribution by tier.
SELECT
  t.tier_level,
  COUNT(l.loyalty_id) AS loyalty_accounts,
  ROUND(AVG(l.loyalty_points), 1) AS avg_loyalty_points,
  MIN(l.loyalty_points) AS min_points,
  MAX(l.loyalty_points) AS max_points
FROM loyalty l
JOIN tier t
  ON l.tier_id = t.tier_id
GROUP BY t.tier_level
ORDER BY loyalty_accounts DESC;

-- 3. High-value loyalty customers.
SELECT
  c.customer_id,
  t.tier_level,
  l.loyalty_points
FROM customer c
JOIN loyalty l
  ON c.loyalty_id = l.loyalty_id
JOIN tier t
  ON l.tier_id = t.tier_id
ORDER BY l.loyalty_points DESC
LIMIT 10;
