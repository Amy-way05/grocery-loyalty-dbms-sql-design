import pandas as pd, numpy as np
from completejourney_py import get_data
import os

out_dir = os.path.dirname(os.path.abspath(__file__))
panel = pd.read_csv(f'{out_dir}/household_panel.csv')
matched_t = pd.read_csv(f'{out_dir}/matched_treated.csv')
matched_c = pd.read_csv(f'{out_dir}/matched_control.csv')

print("Loading transactions + products for deeper analysis...")
data = get_data()
transactions = data['transactions']
products = data['products']
campaign_desc = data['campaign_descriptions']

CAMPAIGN_ID = 18
camp_info = campaign_desc[campaign_desc.campaign_id==CAMPAIGN_ID].iloc[0]
CAMP_START = camp_info.start_date
CAMP_END = camp_info.end_date
WINDOW = (CAMP_END - CAMP_START).days
PRE_START = CAMP_START - pd.Timedelta(days=WINDOW)
DECAY_END = CAMP_END + pd.Timedelta(days=WINDOW)

matched_ids = set(matched_t.household_id) | set(matched_c.household_id)
trans = transactions[transactions.household_id.isin(matched_ids)].copy()
trans['date'] = pd.to_datetime(trans['transaction_timestamp']).dt.normalize()

# ---- INSIGHT 3: Does the effect decay after the campaign ends? ----
decay_mask = (trans['date'] > CAMP_END) & (trans['date'] <= DECAY_END)
decay_spend = trans[decay_mask].groupby('household_id')['sales_value'].sum().reset_index()
decay_spend.columns = ['household_id','decay_period_spend']

mt = matched_t.merge(decay_spend, on='household_id', how='left').fillna(0)
mc = matched_c.merge(decay_spend, on='household_id', how='left').fillna(0)

promo_did = (mt.post_spend.mean()-mt.pre_spend.mean()) - (mc.post_spend.mean()-mc.pre_spend.mean())
decay_treat_change = mt.decay_period_spend.mean() - mt.pre_spend.mean()
decay_ctrl_change  = mc.decay_period_spend.mean() - mc.pre_spend.mean()
decay_did = decay_treat_change - decay_ctrl_change
retention_pct = decay_did/promo_did*100 if promo_did != 0 else np.nan

print(f"\n{'='*70}\nINSIGHT 3: Does the lift persist after the campaign ends?\n{'='*70}")
print(f"  During-campaign DiD effect:        ${promo_did:+.2f}")
print(f"  Equal-length post-campaign DiD:    ${decay_did:+.2f}")
print(f"  Effect retention:                  {retention_pct:.1f}% of original lift persists")

# ---- INSIGHT 4: basket composition shift (new categories vs more of same) ----
cat_mask = (trans['date']>=CAMP_START)&(trans['date']<=CAMP_END)
trans_cat = trans[cat_mask].merge(products[['product_id','department']], on='product_id', how='left')
trans_cat['group'] = np.where(trans_cat.household_id.isin(set(matched_t.household_id)),'Redeemer','Non-redeemer')

cat_summary = trans_cat.groupby(['department','group'])['sales_value'].sum().unstack(fill_value=0)
cat_summary['total'] = cat_summary.sum(axis=1)
cat_summary = cat_summary.sort_values('total', ascending=False).head(12)
if 'Redeemer' in cat_summary.columns:
    cat_summary['redeemer_share_pct'] = cat_summary['Redeemer']/cat_summary['total']*100

print(f"\n{'='*70}\nINSIGHT 4: Where does the incremental spend go?\n{'='*70}")
print(cat_summary)

# Category count = basket breadth (expansion) proxy
cat_breadth = trans_cat.groupby(['household_id','group'])['department'].nunique().reset_index()
cat_breadth.columns = ['household_id','group','n_departments']
breadth_summary = cat_breadth.groupby('group')['n_departments'].mean()
print(f"\nAvg distinct departments shopped during campaign:")
print(breadth_summary)

cat_summary.reset_index().to_csv(f'{out_dir}/category_breakdown.csv', index=False)
pd.DataFrame([{
    'during_campaign_did': round(promo_did,2),
    'post_campaign_decay_did': round(decay_did,2),
    'retention_pct': round(retention_pct,1),
    'redeemer_avg_departments': round(breadth_summary.get('Redeemer',0),2),
    'nonredeemer_avg_departments': round(breadth_summary.get('Non-redeemer',0),2),
}]).to_csv(f'{out_dir}/decay_and_breadth.csv', index=False)

print(f"\nSaved: category_breakdown.csv, decay_and_breadth.csv")
