import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.ensemble import GradientBoostingRegressor
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="The $140 Truth Behind a Grocery Coupon Campaign",
                    page_icon="shopping_cart", layout="wide")

NAV='#1F3864'; RED='#C0504D'; GLD='#E8A838'; GRN='#27AE60'; GRY='#7F8C8D'

st.markdown(f"""
<style>
  [data-testid="stAppViewContainer"] {{ background:#FAFAF8; }}
  [data-testid="stSidebar"] {{ display:none; }}
  .hero {{ text-align:center; padding:60px 20px 40px 20px; }}
  .hero h1 {{ font-size:2.6rem; color:{NAV}; font-weight:800; line-height:1.25; margin-bottom:8px; }}
  .hero .sub {{ font-size:1.1rem; color:#777; max-width:700px; margin:0 auto; }}
  .section {{ max-width:880px; margin:0 auto; padding:50px 20px; }}
  .section h2 {{ color:{NAV}; font-size:1.7rem; border-bottom:3px solid {NAV}; padding-bottom:8px; }}
  .lead {{ font-size:1.15rem; line-height:1.75; color:#333; }}
  .callout {{ background:white; border-left:5px solid {RED}; border-radius:0 10px 10px 0;
              padding:20px 24px; margin:20px 0; font-size:1.05rem; box-shadow:0 2px 8px rgba(0,0,0,.05); }}
  .callout.green {{ border-left-color:{GRN}; }}
  .callout.gold {{ border-left-color:{GLD}; }}
  .kpi-row {{ display:flex; gap:16px; justify-content:center; flex-wrap:wrap; margin:24px 0; }}
  .kpi {{ background:white; border-radius:12px; padding:18px 26px; text-align:center;
          box-shadow:0 2px 8px rgba(0,0,0,.06); min-width:140px; }}
  .kpi .v {{ font-size:1.8rem; font-weight:800; }}
  .kpi .l {{ font-size:.72rem; color:#888; text-transform:uppercase; letter-spacing:.06em; margin-top:4px; }}
  .divider {{ max-width:880px; margin:0 auto; border-top:1px solid #eee; }}
  .toolbox {{ background:{NAV}; border-radius:20px; padding:40px; max-width:880px; margin:40px auto; }}
  .toolbox h2 {{ color:white; border-bottom:3px solid {GLD}; }}
  .toolbox p {{ color:#D8E2F0; }}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load():
    import os
    base = os.path.dirname(os.path.abspath(__file__))
    panel = pd.read_csv(f'{base}/household_panel.csv')
    summary = pd.read_csv(f'{base}/causal_results_summary.csv').iloc[0]
    income_resp = pd.read_csv(f'{base}/income_response.csv')
    kids_resp = pd.read_csv(f'{base}/kids_response.csv')
    cat = pd.read_csv(f'{base}/category_breakdown.csv')
    decay = pd.read_csv(f'{base}/decay_and_breadth.csv').iloc[0]
    return panel, summary, income_resp, kids_resp, cat, decay

panel, summary, income_resp, kids_resp, cat, decay = load()

AXIS = dict(showgrid=True, gridcolor='#EEE', zeroline=False, linecolor='#DDD',
            tickfont=dict(family='Arial', size=11, color='#666'))

st.markdown(f"""
<div class="hero">
  <h1>This coupon campaign claimed a 78% sales lift.<br>The real number is $140.</h1>
  <p class="sub">A causal investigation into Campaign 18 - one of the largest promotions run by a real
  U.S. grocery retailer - using propensity score matching and difference-in-differences on
  1.47 million real transactions from 2,500 households.</p>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="kpi-row">
  <div class="kpi"><div class="v" style="color:{NAV}">{int(summary.exposed_households):,}</div><div class="l">Households Exposed</div></div>
  <div class="kpi"><div class="v" style="color:{RED}">{int(summary.redeemed_households)}</div><div class="l">Redeemed a Coupon</div></div>
  <div class="kpi"><div class="v" style="color:{GRN}">${summary.did_causal_estimate_dollars:.0f}</div><div class="l">Real Incremental Spend</div></div>
  <div class="kpi"><div class="v" style="color:{GLD}">{summary.campaign_roi_pct:+.0f}%</div><div class="l">Campaign ROI</div></div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="section">
<h2>1. The number everyone would report is wrong</h2>
<p class="lead">If you ran this analysis the way most dashboards do - just compare spend
between people who redeemed a coupon and people who didn't - you'd get a <b>78% lift</b>.
That number would go in a slide deck. It would be wrong.</p>
</div>
""", unsafe_allow_html=True)

naive_lift = panel[panel.redeemed==1].post_spend.mean() - panel[panel.redeemed==0].post_spend.mean()
pre_t = panel[panel.redeemed==1].pre_spend.mean()
pre_c = panel[panel.redeemed==0].pre_spend.mean()

fig1 = go.Figure()
fig1.add_trace(go.Bar(x=['Before the campaign<br>even started'], y=[pre_t],
    name='Would-be redeemers', marker_color=RED, opacity=0.85, width=0.35,
    text=[f"${pre_t:.0f}"], textposition='outside', textfont=dict(size=14)))
fig1.add_trace(go.Bar(x=['Before the campaign<br>even started'], y=[pre_c],
    name='Would-be non-redeemers', marker_color=NAV, opacity=0.85, width=0.35,
    text=[f"${pre_c:.0f}"], textposition='outside', textfont=dict(size=14)))
fig1.update_layout(height=340, plot_bgcolor='white', paper_bgcolor='white',
    barmode='group', showlegend=True,
    legend=dict(orientation='h', y=1.15, x=0.5, xanchor='center'),
    xaxis=dict(**AXIS), yaxis=dict(**AXIS, title='Avg. spend, 8 weeks before campaign'),
    margin=dict(t=40,b=20,l=50,r=30))
st.plotly_chart(fig1, use_container_width=True)

st.markdown(f"""
<div class="section">
<div class="callout">
People who went on to redeem the coupon were already spending <b>54% more</b>
before the campaign even began. They are not an average customer who was converted
by a coupon - they are a pre-existing heavy shopper who happened to also clip a coupon.
Comparing their after-campaign spend to everyone else's doesn't measure the campaign.
It measures who they already were.
</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="section">
<h2>2. What's the campaign actually worth?</h2>
<p class="lead">To isolate the true effect, I matched each redeemer to a non-redeemer
with a near-identical pre-campaign spending history (propensity score matching), then
measured how much <i>more</i> each group's spending changed from before to during the
campaign (difference-in-differences). This cancels out who they already were and
leaves only what the campaign caused.</p>
</div>
""", unsafe_allow_html=True)

fig2 = go.Figure()
fig2.add_trace(go.Bar(x=['What a naive<br>comparison claims', 'What actually<br>happened'],
    y=[naive_lift, summary.did_causal_estimate_dollars],
    marker_color=[RED, GRN], opacity=0.88, width=0.45,
    text=[f"${naive_lift:.0f}", f"${summary.did_causal_estimate_dollars:.0f}"],
    textposition='outside', textfont=dict(size=16)))
fig2.update_layout(height=380, plot_bgcolor='white', paper_bgcolor='white',
    showlegend=False, xaxis=dict(**AXIS),
    yaxis=dict(**AXIS, title='Spend lift per household'),
    margin=dict(t=30,b=20,l=50,r=30))
st.plotly_chart(fig2, use_container_width=True)

st.markdown(f"""
<div class="section">
<div class="callout green">
The real, bias-corrected effect is <b>${summary.did_causal_estimate_dollars:.2f} in incremental
spend per household</b> (statistically significant, p&lt;0.0001, 95% confidence interval
${summary.did_ci_lower:.0f}-${summary.did_ci_upper:.0f}). Against a coupon cost of just
${summary.coupon_cost_total:,.0f} across all redeemers, that's an estimated
<b>{summary.campaign_roi_pct:+.0f}% return</b>. The campaign genuinely worked - just not
by nearly as much as the naive number suggested.
</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="section">
<h2>3. The households who needed it most responded the most</h2>
<p class="lead">Breaking the incremental spend down by income shows a pattern that's
both a business insight and, frankly, a good one: this coupon worked best on the
households with the least room in their budget.</p>
</div>
""", unsafe_allow_html=True)

inc_t = income_resp[income_resp.redeemed==1].sort_values('spend_change')
fig3 = go.Figure(go.Bar(x=inc_t.spend_change, y=inc_t.income, orientation='h',
    marker_color=[RED if v>0 else GRY for v in inc_t.spend_change],
    text=[f"${v:+.0f}" for v in inc_t.spend_change], textposition='outside',
    textfont=dict(size=11)))
fig3.update_layout(height=460, plot_bgcolor='white', paper_bgcolor='white',
    xaxis=dict(**AXIS, title='Incremental spend ($) - redeemers only'),
    yaxis=dict(**AXIS, title=''),
    margin=dict(t=20,b=20,l=110,r=50))
st.plotly_chart(fig3, use_container_width=True)

kids_t = kids_resp[kids_resp.redeemed==1]
fig3b = go.Figure(go.Bar(x=kids_t.kids_count.astype(str), y=kids_t.spend_change,
    marker_color=GLD, opacity=0.85,
    text=[f"${v:.0f}" for v in kids_t.spend_change], textposition='outside',
    textfont=dict(size=13)))
fig3b.update_layout(height=320, plot_bgcolor='white', paper_bgcolor='white',
    xaxis=dict(**AXIS, title='Children in household'),
    yaxis=dict(**AXIS, title='Incremental spend ($)'),
    margin=dict(t=20,b=20,l=50,r=30))
st.plotly_chart(fig3b, use_container_width=True)

st.markdown(f"""
<div class="section">
<div class="callout gold">
Households under $15K income showed <b>$244</b> in incremental spend - among the
highest of any segment - and households with 3+ kids showed the single largest
response at <b>$244</b> as well. Larger, lower-income households are the most
price-sensitive, and a well-targeted coupon moves them the most. This is the
rare case where the most profitable targeting strategy and the most equitable
one are the same strategy.
</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="section">
<h2>4. Does the effect last - or is it just pantry-loading?</h2>
<p class="lead">The real test of a loyalty-building promotion isn't what happens during
the campaign. It's what happens the week after, once the discount is gone.</p>
</div>
""", unsafe_allow_html=True)

fig4 = go.Figure()
fig4.add_trace(go.Bar(x=['During the<br>campaign'], y=[decay.during_campaign_did],
    marker_color=GRN, opacity=0.88, width=0.35,
    text=[f"${decay.during_campaign_did:.0f}"], textposition='outside', textfont=dict(size=15)))
fig4.add_trace(go.Bar(x=['Equal-length window<br>right after it ends'], y=[decay.post_campaign_decay_did],
    marker_color=RED, opacity=0.88, width=0.35,
    text=[f"${decay.post_campaign_decay_did:.0f}"], textposition='outside', textfont=dict(size=15)))
fig4.update_layout(height=340, plot_bgcolor='white', paper_bgcolor='white',
    showlegend=False, xaxis=dict(**AXIS),
    yaxis=dict(**AXIS, title='Incremental spend vs. matched control'),
    margin=dict(t=30,b=20,l=50,r=30))
st.plotly_chart(fig4, use_container_width=True)

st.markdown(f"""
<div class="section">
<div class="callout">
Only <b>{decay.retention_pct:.0f}%</b> of the lift survives once the promotion ends.
This is mostly pantry-loading, not habit formation - redeemers bought more while the
deal was live, then reverted almost immediately. The business implication: a single
big campaign won't build lasting loyalty on its own. A steady cadence of smaller,
rotating promotions is likely to produce more durable engagement than one large push.
</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="section">
<h2>5. They didn't just buy the discounted item - they shopped more broadly</h2>
<p class="lead">One risk with coupons is that shoppers buy only the promoted item and
nothing else. That's not what happened here.</p>
</div>
""", unsafe_allow_html=True)

cat_top = cat.sort_values('total', ascending=False).head(8)
fig5 = go.Figure()
fig5.add_trace(go.Bar(x=cat_top.department, y=cat_top['Non-redeemer'],
    name='Non-redeemers', marker_color=NAV, opacity=0.85))
fig5.add_trace(go.Bar(x=cat_top.department, y=cat_top['Redeemer'],
    name='Redeemers', marker_color=RED, opacity=0.85))
fig5.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='white',
    barmode='group', legend=dict(orientation='h', y=1.12, x=0.5, xanchor='center'),
    xaxis=dict(**AXIS, tickangle=-30), yaxis=dict(**AXIS, title='Total category spend ($)'),
    margin=dict(t=40,b=60,l=50,r=30))
st.plotly_chart(fig5, use_container_width=True)

st.markdown(f"""
<div class="section">
<div class="callout green">
Redeemers shopped <b>{decay.redeemer_avg_departments:.1f} distinct departments</b> on
average during the campaign, versus <b>{decay.nonredeemer_avg_departments:.1f}</b> for
non-redeemers - and their incremental spend was spread broadly across grocery, produce,
meat, and drug/GM categories rather than concentrated in one place. The coupon created
a genuine cross-sell halo: it got people into the store and buying more broadly, not
just cherry-picking a single discounted product.
</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="toolbox">
<h2>The Coupon Targeting Tool</h2>
<p>Five questions answered is useful. A tool a marketing team can actually use tomorrow
morning is better. Below is an uplift model trained on this campaign's real data - it
predicts how much <i>incremental</i> spend a specific household profile is likely to
generate if targeted with a coupon, using a two-model (T-learner) approach: one model
learns redeemer behavior, one learns non-redeemer behavior, and the gap between their
predictions for the same household is the personalized uplift estimate.</p>
</div>
""", unsafe_allow_html=True)

@st.cache_resource
def train_uplift_model(panel):
    demo = panel[panel.has_demo==1].copy()
    demo['household_size'] = pd.to_numeric(demo['household_size'], errors='coerce')
    demo['kids_count_num'] = demo['kids_count'].replace({'3+':3}).astype(float)

    income_map = {'Under 15K':7.5,'15-24K':19.5,'25-34K':29.5,'35-49K':42,'50-74K':62,
                  '75-99K':87,'100-124K':112,'125-149K':137,'150-174K':162,
                  '175-199K':187,'200-249K':225,'250K+':275}
    demo['income_num'] = demo['income'].map(income_map)
    demo = demo.dropna(subset=['income_num','household_size'])

    feats = ['pre_spend','pre_visits','income_num','household_size','kids_count_num']
    treat = demo[demo.redeemed==1]
    ctrl  = demo[demo.redeemed==0]

    m_treat = GradientBoostingRegressor(n_estimators=80, max_depth=3, random_state=42)
    m_ctrl  = GradientBoostingRegressor(n_estimators=80, max_depth=3, random_state=42)
    m_treat.fit(treat[feats], treat['spend_change'])
    m_ctrl.fit(ctrl[feats], ctrl['spend_change'])
    return m_treat, m_ctrl, feats, income_map

m_treat, m_ctrl, feats, income_map = train_uplift_model(panel)

avg_coupon_cost = summary.coupon_cost_total / summary.redeemed_households

c1, c2 = st.columns(2)
with c1:
    pre_spend_in = st.slider("Household's typical 8-week grocery spend ($)", 50, 2000, 400, 25)
    pre_visits_in = st.slider("Visits in that 8-week window", 1, 40, 12)
    income_in = st.select_slider("Household income bracket", options=list(income_map.keys()), value='50-74K')
with c2:
    hh_size_in = st.slider("Household size", 1, 8, 2)
    kids_in = st.select_slider("Children in household", options=['0','1','2','3+'], value='0')

kids_num = 3 if kids_in=='3+' else int(kids_in)
X_input = pd.DataFrame([{
    'pre_spend': pre_spend_in, 'pre_visits': pre_visits_in,
    'income_num': income_map[income_in], 'household_size': hh_size_in,
    'kids_count_num': kids_num
}])[feats]

pred_treat = m_treat.predict(X_input)[0]
pred_ctrl = m_ctrl.predict(X_input)[0]
uplift = pred_treat - pred_ctrl
expected_roi = (uplift - avg_coupon_cost) / avg_coupon_cost * 100 if avg_coupon_cost > 0 else 0
recommend = uplift > avg_coupon_cost * 1.5

st.markdown("<br>", unsafe_allow_html=True)
r1,r2,r3 = st.columns(3)
r1.metric("Predicted incremental spend", f"${uplift:.0f}")
r2.metric("Est. coupon cost", f"${avg_coupon_cost:.2f}")
r3.metric("Expected ROI", f"{expected_roi:+.0f}%")

if recommend:
    st.success(f"Target this household. Predicted uplift (${uplift:.0f}) comfortably exceeds the typical coupon cost (${avg_coupon_cost:.2f}) - expected ROI of {expected_roi:+.0f}%.")
else:
    st.warning(f"Lower priority for this campaign. Predicted uplift (${uplift:.0f}) is close to or below the break-even threshold. Consider for a lighter-touch or lower-cost offer instead.")

st.markdown(f"""
<div class="section" style="font-size:0.85rem; color:#888; padding-top:30px;">
<b>Methodology:</b> Propensity score matching (nearest-neighbor, caliper=0.05) on
pre-period spend and visit frequency, validated by covariate balance testing. Causal
effect estimated via difference-in-differences on the matched sample. Targeting tool
uses a T-learner uplift model (gradient boosted trees, trained separately on redeemers
and non-redeemers).<br><br>
<b>Data:</b> Dunnhumby "The Complete Journey" - 1,469,307 real transactions from 2,500
U.S. households, including real campaign exposure and coupon redemption records.<br>
Amrutha Ravikumar - MPS Analytics - Northeastern Roux Institute - 2026
</div>
""", unsafe_allow_html=True)
