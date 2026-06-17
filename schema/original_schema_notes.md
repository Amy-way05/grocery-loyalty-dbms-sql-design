# Original Schema Notes

The original SQLite database contained 8 tables:

| Table | Purpose |
|---|---|
| `CUSTOMER` | Customer profile records and loyalty assignment |
| `LOYALTY` | Loyalty account enrollment and points |
| `TIER` | Loyalty tier definitions |
| `REWARD` | Rewards available by tier |
| `STORE` | Store-level attributes |
| `LOCATION` | Store city/state lookup |
| `PROMOTION` | Store promotion campaigns |
| `REVIEW` | Customer reviews by store |

## Portfolio Cleanup

For presentation quality, the portfolio schema in `create_tables.sql` standardizes names and adds relational constraints:

- `CUOSMTER_EMAIL` becomes `customer_email`.
- `Phone Number` becomes `phone_number`.
- `REWARD_STATE_DATE` becomes `reward_start_date`.
- Foreign keys are documented explicitly.
- Indexes are added for join-heavy reporting paths.
- Check constraints are added for non-negative points, costs, and store square footage.
