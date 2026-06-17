-- Store performance analysis across locations, promotions, and reviews.

-- 1. Store footprint by location.
SELECT
  loc.location_state,
  loc.location_city,
  COUNT(s.store_id) AS store_count,
  SUM(s.store_sqft) AS total_store_sqft,
  ROUND(AVG(s.store_sqft), 1) AS avg_store_sqft
FROM store s
JOIN location loc
  ON s.location_id = loc.location_id
GROUP BY loc.location_state, loc.location_city
ORDER BY store_count DESC, total_store_sqft DESC;

-- 2. Promotion volume by store.
SELECT
  s.store_id,
  s.store_name,
  COUNT(p.promo_id) AS promotion_count
FROM store s
LEFT JOIN promotion p
  ON s.store_id = p.store_id
GROUP BY s.store_id, s.store_name
ORDER BY promotion_count DESC;

-- 3. Review activity by store.
SELECT
  s.store_id,
  s.store_name,
  COUNT(r.review_id) AS review_count
FROM store s
LEFT JOIN review r
  ON s.store_id = r.store_id
GROUP BY s.store_id, s.store_name
ORDER BY review_count DESC;

-- 4. Combined activity score for stores.
SELECT
  s.store_id,
  s.store_name,
  COUNT(DISTINCT p.promo_id) AS promotion_count,
  COUNT(DISTINCT r.review_id) AS review_count,
  COUNT(DISTINCT p.promo_id) + COUNT(DISTINCT r.review_id) AS activity_score
FROM store s
LEFT JOIN promotion p
  ON s.store_id = p.store_id
LEFT JOIN review r
  ON s.store_id = r.store_id
GROUP BY s.store_id, s.store_name
ORDER BY activity_score DESC;
