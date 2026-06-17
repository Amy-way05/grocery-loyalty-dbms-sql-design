-- Grocery Loyalty DBMS
-- Clean portfolio schema based on the original retail loyalty database design.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS tier (
  tier_id INTEGER PRIMARY KEY,
  tier_level TEXT NOT NULL UNIQUE,
  tier_cost NUMERIC NOT NULL CHECK (tier_cost >= 0)
);

CREATE TABLE IF NOT EXISTS location (
  location_id INTEGER PRIMARY KEY,
  location_city TEXT NOT NULL,
  location_state TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS store (
  store_id TEXT PRIMARY KEY,
  store_name TEXT NOT NULL,
  location_id INTEGER NOT NULL,
  store_sqft INTEGER CHECK (store_sqft > 0),
  FOREIGN KEY (location_id) REFERENCES location(location_id)
);

CREATE TABLE IF NOT EXISTS loyalty (
  loyalty_id INTEGER PRIMARY KEY,
  tier_id INTEGER NOT NULL,
  loyalty_enroll_date TEXT NOT NULL,
  loyalty_points INTEGER NOT NULL DEFAULT 0 CHECK (loyalty_points >= 0),
  FOREIGN KEY (tier_id) REFERENCES tier(tier_id)
);

CREATE TABLE IF NOT EXISTS customer (
  customer_id INTEGER PRIMARY KEY,
  customer_first_name TEXT NOT NULL,
  customer_last_name TEXT NOT NULL,
  phone_number TEXT,
  customer_email TEXT,
  customer_zipcode TEXT,
  loyalty_id INTEGER,
  FOREIGN KEY (loyalty_id) REFERENCES loyalty(loyalty_id)
);

CREATE TABLE IF NOT EXISTS promotion (
  promo_id TEXT PRIMARY KEY,
  store_id TEXT NOT NULL,
  promo_description TEXT NOT NULL,
  promo_start_date TEXT NOT NULL,
  promo_end_date TEXT NOT NULL,
  FOREIGN KEY (store_id) REFERENCES store(store_id)
);

CREATE TABLE IF NOT EXISTS reward (
  reward_id TEXT PRIMARY KEY,
  tier_id INTEGER NOT NULL,
  reward_name TEXT NOT NULL,
  reward_cost INTEGER NOT NULL CHECK (reward_cost >= 0),
  reward_start_date TEXT NOT NULL,
  reward_end_date TEXT NOT NULL,
  FOREIGN KEY (tier_id) REFERENCES tier(tier_id)
);

CREATE TABLE IF NOT EXISTS review (
  review_id INTEGER PRIMARY KEY,
  customer_id INTEGER NOT NULL,
  store_id TEXT NOT NULL,
  review_date TEXT NOT NULL,
  review_description TEXT,
  FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
  FOREIGN KEY (store_id) REFERENCES store(store_id)
);

CREATE INDEX IF NOT EXISTS idx_customer_loyalty_id ON customer(loyalty_id);
CREATE INDEX IF NOT EXISTS idx_store_location_id ON store(location_id);
CREATE INDEX IF NOT EXISTS idx_promotion_store_id ON promotion(store_id);
CREATE INDEX IF NOT EXISTS idx_reward_tier_id ON reward(tier_id);
CREATE INDEX IF NOT EXISTS idx_review_customer_id ON review(customer_id);
CREATE INDEX IF NOT EXISTS idx_review_store_id ON review(store_id);
