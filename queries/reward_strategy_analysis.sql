-- Reward strategy analysis by loyalty tier.

-- 1. Reward count and cost profile by tier.
SELECT
  t.tier_level,
  COUNT(r.reward_id) AS reward_count,
  ROUND(AVG(r.reward_cost), 2) AS avg_reward_cost,
  MIN(r.reward_cost) AS min_reward_cost,
  MAX(r.reward_cost) AS max_reward_cost
FROM tier t
LEFT JOIN reward r
  ON t.tier_id = r.tier_id
GROUP BY t.tier_level
ORDER BY reward_count DESC, avg_reward_cost DESC;

-- 2. Reward calendar coverage.
SELECT
  reward_id,
  reward_name,
  reward_start_date,
  reward_end_date,
  tier_id
FROM reward
ORDER BY reward_start_date, reward_end_date;

-- 3. Tiers with strongest reward depth.
SELECT
  t.tier_level,
  COUNT(r.reward_id) AS reward_options
FROM tier t
LEFT JOIN reward r
  ON t.tier_id = r.tier_id
GROUP BY t.tier_level
HAVING COUNT(r.reward_id) > 0
ORDER BY reward_options DESC;
