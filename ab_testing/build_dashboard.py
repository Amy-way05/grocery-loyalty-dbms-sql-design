import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

out_dir = os.path.dirname(os.path.abspath(__file__))
summary = pd.read_csv(f'{out_dir}/causal_results_summary.csv').iloc[0]
panel = pd.read_csv(f'{out_dir}/household_panel.csv')
matched_t = pd.read_csv(f'{out_dir}/matched_treated.csv')
matched_c = pd.read_csv(f'{out_dir}/matched_control.csv')
income_resp = pd.read_csv(f'{out_dir}/income_response.csv')
kids_resp = pd.read_csv(f'{out_dir}/kids_response.csv')

NAV='#1F3864'; RED='#C0504D'; GLD='#E8A838'; GRN='#27AE60'
GRY='#7F8C8D'; BG='#F4F6FA'; WH='#FFFFFF'; GD='#E8ECF0'; F='Arial'
AX = dict(showgrid=True,gridcolor=GD,linecolor='#CCC',showline=True,
          zeroline=False,tickfont=dict(family=F,size=10,color='#666'),automargin=True)

fig = make_subplots(
    rows=3, cols=3,
    subplot_titles=[
        'Naive vs Causal Estimate (Selection Bias Correction)',
        'Covariate Balance: Before vs After Matching',
        'Difference-in-Differences: Spend Trajectory',
        'Visit Frequency: Treatment vs Control',
        'Incremental Spend by Household Income',
        'Incremental Spend by Kids Count',
        'Campaign Economics: Cost vs Revenue',
        'Spend Change Distribution (Matched Sample)',
        'Propensity Score Overlap',
    ],
    vertical_spacing=0.13, horizontal_spacing=0.09,
    row_heights=[0.33,0.33,0.33]
)

# Panel 1: Naive vs Causal
naive_lift_dollars = panel[panel.redeemed==1].post_spend.mean() - panel[panel.redeemed==0].post_spend.mean()
fig.add_trace(go.Bar(
    x=['Naive Estimate<br>(biased)', 'Causal Estimate<br>(DiD + matching)'],
    y=[naive_lift_dollars, summary.did_causal_estimate_dollars],
    marker_color=[RED, GRN], opacity=0.85,
    text=[f"${naive_lift_dollars:.0f}", f"${summary.did_causal_estimate_dollars:.0f}"],
    textposition='outside', textfont=dict(size=13,family=F),
    error_y=dict(type='data', array=[0, summary.did_ci_upper-summary.did_causal_estimate_dollars],
                 arrayminus=[0, summary.did_causal_estimate_dollars-summary.did_ci_lower],
                 visible=True, thickness=1.5, color='#555'),
    showlegend=False), row=1, col=1)
fig.add_annotation(x=0.5, y=naive_lift_dollars*0.5, xref='x domain', yref='y1',
    text=f"Overstated by<br>${naive_lift_dollars-summary.did_causal_estimate_dollars:.0f}",
    showarrow=False, font=dict(size=9,color=RED,family=F))

# Panel 2: Covariate balance before/after
before_t = panel[panel.redeemed==1].pre_spend.mean()
before_c = panel[panel.redeemed==0].pre_spend.mean()
after_t = matched_t.pre_spend.mean()
after_c = matched_c.pre_spend.mean()
fig.add_trace(go.Bar(x=['Before Matching','After Matching'], y=[before_t,after_t],
    name='Redeemers', marker_color=RED, opacity=0.85,
    text=[f"${v:.0f}" for v in [before_t,after_t]], textposition='outside',
    textfont=dict(size=10,family=F)), row=1,col=2)
fig.add_trace(go.Bar(x=['Before Matching','After Matching'], y=[before_c,after_c],
    name='Non-redeemers', marker_color=NAV, opacity=0.85,
    text=[f"${v:.0f}" for v in [before_c,after_c]], textposition='outside',
    textfont=dict(size=10,family=F)), row=1,col=2)

# Panel 3: DiD trajectory
fig.add_trace(go.Scatter(x=['Pre-period','Post-period'],
    y=[matched_t.pre_spend.mean(), matched_t.post_spend.mean()],
    mode='lines+markers+text', name='Redeemers (matched)',
    line=dict(color=RED,width=3), marker=dict(size=12,color=RED),
    text=[f"${v:.0f}" for v in [matched_t.pre_spend.mean(),matched_t.post_spend.mean()]],
    textposition='top center', textfont=dict(size=10,family=F),
    showlegend=True), row=1,col=3)
fig.add_trace(go.Scatter(x=['Pre-period','Post-period'],
    y=[matched_c.pre_spend.mean(), matched_c.post_spend.mean()],
    mode='lines+markers+text', name='Non-redeemers (matched)',
    line=dict(color=NAV,width=3), marker=dict(size=12,color=NAV),
    text=[f"${v:.0f}" for v in [matched_c.pre_spend.mean(),matched_c.post_spend.mean()]],
    textposition='bottom center', textfont=dict(size=10,family=F),
    showlegend=True), row=1,col=3)

# Panel 4: Visit frequency
fig.add_trace(go.Bar(x=['Redeemers','Non-redeemers'],
    y=[matched_t.post_visits.mean()-matched_t.pre_visits.mean(),
       matched_c.post_visits.mean()-matched_c.pre_visits.mean()],
    marker_color=[RED,NAV], opacity=0.85,
    text=[f"{v:+.2f}" for v in [matched_t.post_visits.mean()-matched_t.pre_visits.mean(),
                                  matched_c.post_visits.mean()-matched_c.pre_visits.mean()]],
    textposition='outside', textfont=dict(size=11,family=F),
    showlegend=False), row=2,col=1)

# Panel 5: Income response
income_pivot = income_resp.pivot(index='income', columns='redeemed', values='spend_change')
income_pivot.columns = ['control','treatment'] if 0 in income_pivot.columns else income_pivot.columns
fig.add_trace(go.Bar(x=income_resp[income_resp.redeemed==1].income,
    y=income_resp[income_resp.redeemed==1].spend_change,
    marker_color=RED, opacity=0.85, name='Redeemers',
    showlegend=False), row=2,col=2)

# Panel 6: Kids response
fig.add_trace(go.Bar(x=kids_resp[kids_resp.redeemed==1].kids_count.astype(str),
    y=kids_resp[kids_resp.redeemed==1].spend_change,
    marker_color=RED, opacity=0.85, name='Redeemers kids',
    text=[f"${v:.0f}" for v in kids_resp[kids_resp.redeemed==1].spend_change],
    textposition='outside', textfont=dict(size=10,family=F),
    showlegend=False), row=2,col=3)
fig.add_trace(go.Bar(x=kids_resp[kids_resp.redeemed==0].kids_count.astype(str),
    y=kids_resp[kids_resp.redeemed==0].spend_change,
    marker_color=NAV, opacity=0.85, name='Non-redeemers kids',
    showlegend=False), row=2,col=3)

# Panel 7: Campaign economics
fig.add_trace(go.Bar(x=['Coupon Cost','Incremental Revenue','Net Profit'],
    y=[-summary.coupon_cost_total, summary.incremental_revenue_total,
       summary.incremental_revenue_total - abs(summary.coupon_cost_total)],
    marker_color=[RED, GRN, NAV], opacity=0.85,
    text=[f"${v:,.0f}" for v in [-summary.coupon_cost_total, summary.incremental_revenue_total,
          summary.incremental_revenue_total - abs(summary.coupon_cost_total)]],
    textposition='outside', textfont=dict(size=10,family=F),
    showlegend=False), row=3,col=1)
fig.add_annotation(x=1,y=summary.incremental_revenue_total*1.1,xref='x7',yref='y7',
    text=f"<b>ROI: {summary.campaign_roi_pct:+.0f}%</b>",
    showarrow=False, font=dict(size=12,color=GRN,family=F))

# Panel 8: Spend change distribution
fig.add_trace(go.Violin(x=matched_t.spend_change, name='Redeemers',
    fillcolor=RED, line_color=RED, opacity=0.6, box_visible=True,
    meanline_visible=True, orientation='h', side='positive',
    showlegend=False), row=3,col=2)
fig.add_trace(go.Violin(x=matched_c.spend_change, name='Non-redeemers',
    fillcolor=NAV, line_color=NAV, opacity=0.6, box_visible=True,
    meanline_visible=True, orientation='h', side='negative',
    showlegend=False), row=3,col=2)

# Panel 9: Propensity score overlap
fig.add_trace(go.Histogram(x=panel[panel.redeemed==1].propensity_score,
    name='Redeemers', marker_color=RED, opacity=0.6, nbinsx=25,
    histnorm='probability', showlegend=False), row=3,col=3)
fig.add_trace(go.Histogram(x=panel[panel.redeemed==0].propensity_score,
    name='Non-redeemers', marker_color=NAV, opacity=0.6, nbinsx=25,
    histnorm='probability', showlegend=False), row=3,col=3)

fig.update_layout(
    height=1150, width=1420,
    paper_bgcolor=BG, plot_bgcolor=WH,
    font=dict(family=F,color='#1A1A1A'),
    barmode='group',
    title=dict(
        text=(
            "<b>Grocery Loyalty · Campaign 18 Causal Impact Analysis</b><br>"
            f"<span style='font-size:12px;color:#888'>"
            f"Real Dunnhumby retail data · {int(summary.exposed_households):,} households exposed · "
            f"{int(summary.redeemed_households)} redeemed · "
            f"Causal estimate: ${summary.did_causal_estimate_dollars:.2f}/household "
            f"(p={summary.did_p_value:.4f}, d={summary.did_cohen_d:.2f}) · "
            f"Campaign ROI: {summary.campaign_roi_pct:+.0f}%"
            f"</span>"
        ),
        x=0.5, xanchor='center', y=0.99, yanchor='top',
        font=dict(size=18,color=NAV,family=F)),
    legend=dict(orientation='h',x=0.5,xanchor='center',y=1.035,
        yanchor='bottom',font=dict(size=11,family=F),
        bgcolor='rgba(255,255,255,0.9)',bordercolor='#DDD',borderwidth=1),
    margin=dict(t=150,b=50,l=55,r=30),
)

ax_labels = {
    (1,1):('','Spend Lift ($)'),(1,2):('','Pre-period Spend ($)'),
    (1,3):('','Avg Spend ($)'),(2,1):('Group','Visit Change'),
    (2,2):('Income Bracket','Spend Change ($)'),(2,3):('Kids Count','Spend Change ($)'),
    (3,1):('','Dollars ($)'),(3,2):('Spend Change ($)',''),
    (3,3):('Propensity Score','Density'),
}
for (r,c),(xt,yt) in ax_labels.items():
    fig.update_xaxes(title_text=xt,title_font=dict(family=F,size=10,color='#555'),**AX,row=r,col=c)
    fig.update_yaxes(title_text=yt,title_font=dict(family=F,size=10,color='#555'),**AX,row=r,col=c)
fig.update_xaxes(tickangle=-45, row=2, col=2)

for ann in fig.layout.annotations[:9]:
    ann.update(font=dict(color=NAV,family=F,size=11))

out = f'{out_dir}/campaign_causal_dashboard.html'
fig.write_html(out, include_plotlyjs='cdn', full_html=True)
print(f"Dashboard saved: {out}")
