"""
Grocery Loyalty - Campaign 18 Causal Impact Analysis
=====================================================
Real data: Dunnhumby "The Complete Journey" (84.51 degrees)
1,469,307 transactions - 2,500 US households - real campaign/coupon data

Business question: Does coupon redemption from Campaign 18 (Type A, the
largest campaign, 1,133 households exposed) cause incremental spend, or
are redeemers just already-high-spending customers who would have bought
anyway (selection bias)?

Method: Propensity Score Matching + Difference-in-Differences
"""

import numpy as np
import pandas as pd
from completejourney_py import get_data
import pingouin as pg
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors
import warnings, os
warnings.filterwarnings('ignore')

print("Loading Dunnhumby Complete Journey data...")
data = get_data()
transactions = data['transactions']
campaigns = data['campaigns']
redemptions = data['coupon_redemptions']
demographics = data['demographics']
campaign_desc = data['campaign_descriptions']

CAMPAIGN_ID = 18
camp_info = campaign_desc[campaign_desc.campaign_id == CAMPAIGN_ID].iloc[0]
CAMP_START = camp_info.start_date
CAMP_END = camp_info.end_date
PRE_START = CAMP_START - pd.Timedelta(days=(CAMP_END - CAMP_START).days)

print(f"\nCampaign {CAMPAIGN_ID} ({camp_info.campaign_type}): {CAMP_START.date()} to {CAMP_END.date()}")
print(f"Pre-period for comparison: {PRE_START.date()} to {CAMP_START.date()}")

# 1. DEFINE TREATMENT
exposed_hh = set(campaigns[campaigns.campaign_id == CAMPAIGN_ID].household_id)
redeemed_hh = set(redemptions[redemptions.campaign_id == CAMPAIGN_ID].household_id)
redeemed_hh = redeemed_hh & exposed_hh
non_redeemed_hh = exposed_hh - redeemed_hh

print(f"\nExposed households:     {len(exposed_hh):,}")
print(f"Redeemed (treatment):   {len(redeemed_hh):,}")
print(f"Non-redeemed (control): {len(non_redeemed_hh):,}")

# 2. BUILD PRE/POST SPEND PANEL
trans = transactions[transactions.household_id.isin(exposed_hh)].copy()
trans['date'] = pd.to_datetime(trans['transaction_timestamp']).dt.normalize()

pre_mask  = (trans['date'] >= PRE_START) & (trans['date'] < CAMP_START)
post_mask = (trans['date'] >= CAMP_START) & (trans['date'] <= CAMP_END)

pre_spend = trans[pre_mask].groupby('household_id').agg(
    pre_spend=('sales_value','sum'),
    pre_visits=('basket_id','nunique')
).reset_index()
post_spend = trans[post_mask].groupby('household_id').agg(
    post_spend=('sales_value','sum'),
    post_visits=('basket_id','nunique')
).reset_index()

panel = pd.DataFrame({'household_id': list(exposed_hh)})
panel = panel.merge(pre_spend, on='household_id', how='left')
panel = panel.merge(post_spend, on='household_id', how='left')
panel[['pre_spend','pre_visits','post_spend','post_visits']] = panel[
    ['pre_spend','pre_visits','post_spend','post_visits']].fillna(0)
panel['redeemed'] = panel.household_id.isin(redeemed_hh).astype(int)
panel['spend_change'] = panel.post_spend - panel.pre_spend
panel = panel.merge(demographics, on='household_id', how='left')

print(f"\nPanel built: {len(panel):,} households")
print(f"  With demographics: {panel.age.notna().sum():,}")

# 3. NAIVE COMPARISON
naive_treat = panel[panel.redeemed==1].post_spend
naive_ctrl  = panel[panel.redeemed==0].post_spend
naive_diff_pct = (naive_treat.mean() - naive_ctrl.mean()) / naive_ctrl.mean() * 100

print(f"\n{'='*70}")
print("NAIVE COMPARISON (post-period spend only, no bias correction)")
print(f"{'='*70}")
print(f"  Redeemers post-spend:     ${naive_treat.mean():.2f}")
print(f"  Non-redeemers post-spend: ${naive_ctrl.mean():.2f}")
print(f"  Naive 'lift':             {naive_diff_pct:+.1f}%")
print(f"  >>> This number is BIASED if redeemers were already bigger spenders <<<")

pre_treat = panel[panel.redeemed==1].pre_spend
pre_ctrl  = panel[panel.redeemed==0].pre_spend
pre_diff_pct = (pre_treat.mean() - pre_ctrl.mean()) / (pre_ctrl.mean()+0.01) * 100
print(f"\n  SELECTION BIAS CHECK (pre-period, before any campaign exposure):")
print(f"  Redeemers pre-spend:     ${pre_treat.mean():.2f}")
print(f"  Non-redeemers pre-spend: ${pre_ctrl.mean():.2f}")
print(f"  Pre-existing gap:        {pre_diff_pct:+.1f}%")
if abs(pre_diff_pct) > 5:
    print(f"  >>> CONFIRMED: Redeemers were already different pre-campaign. Naive comparison is invalid. <<<")

# 4. PROPENSITY SCORE MATCHING
print(f"\n{'='*70}")
print("PROPENSITY SCORE MATCHING")
print(f"{'='*70}")

panel['has_demo'] = panel.age.notna().astype(int)
match_features = ['pre_spend', 'pre_visits']

X = panel[match_features].fillna(0).values
y = panel['redeemed'].values

ps_model = LogisticRegression(max_iter=1000)
ps_model.fit(X, y)
panel['propensity_score'] = ps_model.predict_proba(X)[:, 1]

treated = panel[panel.redeemed == 1].copy()
control = panel[panel.redeemed == 0].copy()

nn = NearestNeighbors(n_neighbors=1)
nn.fit(control[['propensity_score']].values)
distances, indices = nn.kneighbors(treated[['propensity_score']].values)

CALIPER = 0.05
valid_matches = distances.flatten() < CALIPER
matched_treated = treated.iloc[valid_matches].reset_index(drop=True)
matched_control = control.iloc[indices.flatten()[valid_matches]].reset_index(drop=True)

print(f"  Treated households:        {len(treated)}")
print(f"  Matched within caliper:    {len(matched_treated)} ({len(matched_treated)/len(treated)*100:.0f}%)")
print(f"  Dropped (no good match):   {len(treated)-len(matched_treated)}")

bal_before = pg.ttest(treated.pre_spend, control.pre_spend)
bal_after  = pg.ttest(matched_treated.pre_spend, matched_control.pre_spend)
print(f"\n  Covariate balance (pre-spend) BEFORE matching: p={bal_before['p_val'].values[0]:.4f}")
print(f"  Covariate balance (pre-spend) AFTER matching:  p={bal_after['p_val'].values[0]:.4f}")

# 5. DIFFERENCE-IN-DIFFERENCES
print(f"\n{'='*70}")
print("DIFFERENCE-IN-DIFFERENCES (matched sample)")
print(f"{'='*70}")

did_treat_pre  = matched_treated.pre_spend.mean()
did_treat_post = matched_treated.post_spend.mean()
did_ctrl_pre   = matched_control.pre_spend.mean()
did_ctrl_post  = matched_control.post_spend.mean()

treat_change = did_treat_post - did_treat_pre
ctrl_change  = did_ctrl_post - did_ctrl_pre
did_estimate = treat_change - ctrl_change

print(f"  Treatment group: pre=${did_treat_pre:.2f} -> post=${did_treat_post:.2f} (change: {treat_change:+.2f})")
print(f"  Control group:   pre=${did_ctrl_pre:.2f} -> post=${did_ctrl_post:.2f} (change: {ctrl_change:+.2f})")
print(f"\n  >>> DiD CAUSAL ESTIMATE: ${did_estimate:+.2f} incremental spend per household <<<")

did_ttest = pg.ttest(matched_treated.spend_change, matched_control.spend_change)
did_cohen_d = did_ttest['cohen_d'].values[0]
did_pval = did_ttest['p_val'].values[0]
did_ci = did_ttest['CI95'].values[0]

print(f"  Cohen's d:  {did_cohen_d:.3f}")
print(f"  p-value:    {did_pval:.4f}")
print(f"  95% CI:     [${did_ci[0]:.2f}, ${did_ci[1]:.2f}]")

# 6. VISIT FREQUENCY DiD
visit_treat_change = matched_treated.post_visits.mean() - matched_treated.pre_visits.mean()
visit_ctrl_change  = matched_control.post_visits.mean() - matched_control.pre_visits.mean()
visit_did = visit_treat_change - visit_ctrl_change
print(f"\n  Visit frequency DiD: {visit_did:+.2f} incremental visits per household")

# 7. DEMOGRAPHIC SUBGROUP ANALYSIS
print(f"\n{'='*70}")
print("DEMOGRAPHIC RESPONSE ANALYSIS")
print(f"{'='*70}")

demo_panel = panel[panel.has_demo == 1].copy()
income_response = demo_panel.groupby(['income','redeemed'], observed=True).spend_change.mean().reset_index()
print("\nSpend change by income bracket and redemption status:")
print(income_response.to_string(index=False))

kids_response = demo_panel.groupby(['kids_count','redeemed'])['spend_change'].mean().reset_index()
print("\nSpend change by household kids count and redemption status:")
print(kids_response.to_string(index=False))

# 8. CAMPAIGN ROI
print(f"\n{'='*70}")
print("CAMPAIGN ROI")
print(f"{'='*70}")

coupon_cost = abs(trans[(trans.household_id.isin(redeemed_hh)) & post_mask]['coupon_disc'].sum())
incremental_revenue = did_estimate * len(redeemed_hh)
roi = (incremental_revenue - coupon_cost) / coupon_cost * 100 if coupon_cost > 0 else None

print(f"  Total coupon discount cost:        ${coupon_cost:,.2f}")
print(f"  Estimated incremental revenue:     ${incremental_revenue:,.2f}")
print(f"  (= ${did_estimate:.2f}/household x {len(redeemed_hh)} redeemers)")
if roi is not None:
    print(f"  Campaign ROI:                      {roi:+.1f}%")

# 9. SAVE RESULTS
results_summary = {
    'campaign_id': CAMPAIGN_ID,
    'exposed_households': len(exposed_hh),
    'redeemed_households': len(redeemed_hh),
    'naive_lift_pct': round(naive_diff_pct, 2),
    'pre_period_selection_bias_pct': round(pre_diff_pct, 2),
    'matched_pairs': len(matched_treated),
    'did_causal_estimate_dollars': round(did_estimate, 2),
    'did_cohen_d': round(did_cohen_d, 3),
    'did_p_value': round(did_pval, 4),
    'did_ci_lower': round(did_ci[0], 2),
    'did_ci_upper': round(did_ci[1], 2),
    'visit_frequency_did': round(visit_did, 3),
    'coupon_cost_total': round(coupon_cost, 2),
    'incremental_revenue_total': round(incremental_revenue, 2),
    'campaign_roi_pct': round(roi, 1) if roi else None,
}

out_dir = os.path.dirname(os.path.abspath(__file__))
pd.DataFrame([results_summary]).to_csv(f'{out_dir}/causal_results_summary.csv', index=False)
panel.to_csv(f'{out_dir}/household_panel.csv', index=False)
matched_treated.to_csv(f'{out_dir}/matched_treated.csv', index=False)
matched_control.to_csv(f'{out_dir}/matched_control.csv', index=False)
income_response.to_csv(f'{out_dir}/income_response.csv', index=False)
kids_response.to_csv(f'{out_dir}/kids_response.csv', index=False)

print(f"\nAll results saved to {out_dir}/")
print("\n" + "="*70)
print("EXECUTIVE SUMMARY")
print("="*70)
print(f"""
Naive analysis would claim: {naive_diff_pct:+.1f}% spend lift from coupon redemption
Reality (after bias correction): ${did_estimate:+.2f} incremental spend per household
  (Cohen's d={did_cohen_d:.3f}, p={did_pval:.4f}, 95% CI ${did_ci[0]:.2f} to ${did_ci[1]:.2f})

This matters because the naive comparison conflates CORRELATION
(big spenders redeem more coupons) with CAUSATION (coupons cause
incremental spend). Propensity matching + DiD isolates the true effect.
""")
