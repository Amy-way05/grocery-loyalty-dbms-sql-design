# Data Dictionary

## `customer`

| Column | Description |
|---|---|
| `customer_id` | Unique customer identifier |
| `customer_first_name` | Customer first name |
| `customer_last_name` | Customer last name |
| `phone_number` | Customer phone number |
| `customer_email` | Customer email address |
| `customer_zipcode` | Customer zip code |
| `loyalty_id` | Linked loyalty account |

## `loyalty`

| Column | Description |
|---|---|
| `loyalty_id` | Unique loyalty account identifier |
| `tier_id` | Linked loyalty tier |
| `loyalty_enroll_date` | Enrollment date |
| `loyalty_points` | Current loyalty point balance |

## `tier`

| Column | Description |
|---|---|
| `tier_id` | Unique tier identifier |
| `tier_level` | Loyalty tier name or level |
| `tier_cost` | Cost associated with the tier |

## `reward`

| Column | Description |
|---|---|
| `reward_id` | Unique reward identifier |
| `tier_id` | Tier eligible for the reward |
| `reward_name` | Reward name |
| `reward_cost` | Reward cost |
| `reward_start_date` | Reward availability start date |
| `reward_end_date` | Reward availability end date |

## `store`

| Column | Description |
|---|---|
| `store_id` | Unique store identifier |
| `store_name` | Store name |
| `location_id` | Linked location |
| `store_sqft` | Store square footage |

## `location`

| Column | Description |
|---|---|
| `location_id` | Unique location identifier |
| `location_city` | City |
| `location_state` | State |

## `promotion`

| Column | Description |
|---|---|
| `promo_id` | Unique promotion identifier |
| `store_id` | Store running the promotion |
| `promo_description` | Promotion description |
| `promo_start_date` | Promotion start date |
| `promo_end_date` | Promotion end date |

## `review`

| Column | Description |
|---|---|
| `review_id` | Unique review identifier |
| `customer_id` | Reviewing customer |
| `store_id` | Reviewed store |
| `review_date` | Review date |
| `review_description` | Review text |
