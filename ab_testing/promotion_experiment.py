import numpy as np, pandas as pd, scipy.stats as stats
import pingouin as pg
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os, warnings
warnings.filterwarnings('ignore')

np.random.seed(42)

N_CUSTOMERS = 2400
N_STORES    = 12
PRE_WEEKS   = 8
PROMO_WEEKS = 4
POST_WEEKS  = 12

TIERS = {
    'Bronze': {'weight':0.55,'base_spend':42,'visit_freq':1.8,'points':(500,3000)},
    'Silver': {'weight':0.30,'base_spend':68,'visit_freq':2.4,'points':(3001,8000)},
    'Gold':   {'weight':0.15,'base_spend':112,'visit_freq':3.1,'points':(8001,25000)},
}

STORE_SIZES = np.random.choice([8000,12000,18000,25000,35000],N_STORES,p=[0.15,0.25,0.30,0.20,0.10])
tier_labels = np.random.choice(list(TIERS.keys()),N_CUSTOMERS,p=[v['weight'] for v in TIERS.values()])
store_ids   = np.random.randint(0,N_STORES,N_CUSTOMERS)
store_sqft  = STORE_SIZES[store_ids]

treatment = np.zeros(N_CUSTOMERS,dtype=int)
for tier in TIERS:
    idx = np.where(tier_labels==tier)[0]
    treatment[np.random.choice(idx,len(idx)//2,replace=False)] = 1

loyalty_points = np.array([np.random.randint(*TIERS[t]['points']) for t in tier_labels])

customers = pd.DataFrame({'customer_id':range(N_CUSTOMERS),'tier':tier_labels,
    'store_id':store_ids,'store_sqft':store_sqft,'treatment':treatment,
    'loyalty_points_pre':loyalty_points})

def generate_visits(customer_id,tier,treatment,store_sqft,phase):
    t = TIERS[tier]
    base_spend = t['base_spend']
    freq = t['visit_freq']
    size_mult = 1 + (store_sqft-15000)/100000
    if phase=='pre':
        weeks=PRE_WEEKS; spend_mult=1.0; freq_mult=1.0
    elif phase=='promo':
        weeks=PROMO_WEEKS
        if treatment==1:
            tier_lift={'Bronze':0.18,'Silver':0.12,'Gold':0.06}
            spend_mult=1+tier_lift[tier]+np.random.normal(0,0.04)
            freq_mult=1+{'Bronze':0.22,'Silver':0.14,'Gold':0.05}[tier]
        else:
            spend_mult=1.0; freq_mult=1.0
    elif phase=='post':
        weeks=POST_WEEKS
        if treatment==1:
            churn_prob={'Bronze':0.38,'Silver':0.18,'Gold':0.07}[tier]
            if np.random.rand()<churn_prob:
                spend_mult=0.72; freq_mult=0.61
            else:
                spend_mult=1.08; freq_mult=1.05
        else:
            spend_mult=1.0; freq_mult=1.0
    visits=[]
    for week in range(weeks):
        for _ in range(np.random.poisson(freq*freq_mult/4)):
            spend=max(5,np.random.normal(base_spend*spend_mult*size_mult,base_spend*0.35))
            visits.append({'customer_id':customer_id,'tier':tier,'treatment':treatment,
                'store_sqft':store_sqft,'phase':phase,'week':week,'spend':round(spend,2),
                'points_earned':int(spend*(2 if (treatment==1 and phase=='promo') else 1))})
    return visits

print("Generating transactions...")
all_visits=[]
for _,row in customers.iterrows():
    for phase in ['pre','promo','post']:
        all_visits.extend(generate_visits(row.customer_id,row.tier,row.treatment,row.store_sqft,phase))
visits=pd.DataFrame(all_visits)
print(f"  {len(visits):,} visits across {N_CUSTOMERS:,} customers")

cust_metrics=visits.groupby(['customer_id','tier','treatment','store_sqft','phase']).agg(
    total_spend=('spend','sum'),n_visits=('spend','count'),
    avg_basket=('spend','mean'),points_earned=('points_earned','sum')).reset_index()

promo=cust_metrics[cust_metrics.phase=='promo'].copy()
post=cust_metrics[cust_metrics.phase=='post'].copy()
ctrl_promo=promo[promo.treatment==0]; treat_promo=promo[promo.treatment==1]
ctrl_post=post[post.treatment==0];   treat_post=post[post.treatment==1]

res_spend=pg.ttest(treat_promo.total_spend,ctrl_promo.total_spend)
cohen_d=res_spend['cohen-d'].values[0]; p_val=res_spend['p-val'].values[0]
ci=res_spend['CI95%'].values[0]
treat_mean=treat_promo.total_spend.mean(); ctrl_mean=ctrl_promo.total_spend.mean()
lift_pct=(treat_mean-ctrl_mean)/ctrl_mean*100

print(f"\nPrimary: lift={lift_pct:+.1f}% p={p_val:.4f} d={cohen_d:.3f}")

tier_retention={}
for tier in ['Bronze','Silver','Gold']:
    t_vis=set(promo[(promo.treatment==1)&(promo.tier==tier)].customer_id)
    t_post=set(post[(post.treatment==1)&(post.tier==tier)].customer_id)
    c_vis=set(promo[(promo.treatment==0)&(promo.tier==tier)].customer_id)
    c_post=set(post[(post.treatment==0)&(post.tier==tier)].customer_id)
    t_ret=len(t_vis&t_post)/len(t_vis)*100 if t_vis else 0
    c_ret=len(c_vis&c_post)/len(c_vis)*100 if c_vis else 0
    tier_retention[tier]={'treatment':t_ret,'control':c_ret,'gap':t_ret-c_ret}
    print(f"Retention {tier}: treat={t_ret:.1f}% ctrl={c_ret:.1f}% gap={t_ret-c_ret:+.1f}pp")

UPGRADE_THRESH={'Bronze':3000,'Silver':8000}
promo_pts=promo[['customer_id','tier','treatment','points_earned']].merge(
    customers[['customer_id','loyalty_points_pre']],on='customer_id')
promo_pts['total_points']=promo_pts.loyalty_points_pre+promo_pts.points_earned
mig_df=promo_pts.assign(upgraded=((promo_pts.tier=='Bronze')&(promo_pts.total_points>=3000))|
    ((promo_pts.tier=='Silver')&(promo_pts.total_points>=8000))).astype({'upgraded':int})
mig_summary=mig_df.groupby(['tier','treatment'])['upgraded'].agg(['sum','count']).reset_index()
mig_summary['upgrade_rate']=mig_summary['sum']/mig_summary['count']*100

treat_mig=set(mig_df[(mig_df.treatment==1)&(mig_df.upgraded==1)].customer_id)
treat_nomig=set(mig_df[(mig_df.treatment==1)&(mig_df.upgraded==0)].customer_id)
post_mig=post[post.customer_id.isin(treat_mig)].total_spend.mean()
post_nomig=post[post.customer_id.isin(treat_nomig)].total_spend.mean()
ltv_delta=post_mig-post_nomig
print(f"LTV delta (migrated vs not): \${ltv_delta:+.2f}")

promo['size_bucket']=pd.cut(promo.store_sqft,bins=[0,12000,20000,50000],
    labels=['Small (<12k sqft)','Medium (12-20k)','Large (>20k sqft)'])
roi_pivot=promo.groupby(['size_bucket','treatment']).total_spend.mean().unstack()
roi_pivot.columns=['control','treatment']
roi_pivot['lift_pct']=(roi_pivot.treatment-roi_pivot.control)/roi_pivot.control*100
roi_pivot['incr']=roi_pivot.treatment-roi_pivot.control

tier_results=[]
for tier in ['Bronze','Silver','Gold']:
    tc=ctrl_promo[ctrl_promo.tier==tier].total_spend
    tt=treat_promo[treat_promo.tier==tier].total_spend
    r=pg.ttest(tt,tc)
    tier_results.append({'tier':tier,'control_mean':tc.mean(),'treatment_mean':tt.mean(),
        'lift_pct':(tt.mean()-tc.mean())/tc.mean()*100,
        'cohen_d':r['cohen-d'].values[0],'p_val':r['p-val'].values[0],
        'p_bonferroni':min(r['p-val'].values[0]*3,1.0)})
tier_df=pd.DataFrame(tier_results)

freq_res=pg.mwu(treat_promo.n_visits,ctrl_promo.n_visits)
freq_lift=(treat_promo.n_visits.mean()-ctrl_promo.n_visits.mean())/ctrl_promo.n_visits.mean()*100

NAV='#1F3864';RED='#C0504D';GLD='#E8A838';GRN='#27AE60';GRY='#7F8C8D'
BG='#F4F6FA';WH='#FFFFFF';GD='#E8ECF0';F='Arial'
AX=dict(showgrid=True,gridcolor=GD,linecolor='#CCC',showline=True,zeroline=False,
    tickfont=dict(family=F,size=10,color='#666'),automargin=True)

fig=make_subplots(rows=3,cols=3,
    subplot_titles=[
        'Primary: Spend Distribution — Control vs Treatment',
        'Spend Lift by Tier (Bonferroni-corrected)',
        'Visit Frequency by Group',
        'INSIGHT 1 · Post-Promotion Retention by Tier',
        'INSIGHT 2 · Tier Migration Rate',
        'INSIGHT 2 · 90-Day LTV: Migrated vs Non-Migrated',
        'INSIGHT 3 · Promotion ROI by Store Size',
        'Points Earned — Treatment Group',
        'Avg Spend per Visit: Pre / Promo / Post',
    ],
    vertical_spacing=0.13,horizontal_spacing=0.08,
    row_heights=[0.33,0.33,0.33])

for grp,color,name in [(0,NAV,'Control'),(1,RED,'Treatment')]:
    fig.add_trace(go.Violin(x=promo[promo.treatment==grp].total_spend,
        name=name,fillcolor=color,line_color=color,opacity=0.6,
        box_visible=True,meanline_visible=True,orientation='h',
        side='positive' if grp==1 else 'negative',
        showlegend=True,legendgroup=name),row=1,col=1)
fig.add_annotation(x=treat_mean,y=0.4,
    text=f"<b>+{lift_pct:.1f}% lift</b><br>p={p_val:.4f} d={cohen_d:.2f}",
    showarrow=True,ax=70,ay=-35,
    font=dict(size=10,color=RED,family=F),
    bgcolor='white',bordercolor=RED,borderwidth=1,borderpad=3,
    xref='x1',yref='y1')

colors_t=[GRN if p<0.05 else GLD for p in tier_df.p_bonferroni]
fig.add_trace(go.Bar(x=tier_df.tier,y=tier_df.lift_pct,marker_color=colors_t,opacity=0.88,
    text=[f"{v:+.1f}%\n{'★' if p<0.05 else 'ns'}" for v,p in zip(tier_df.lift_pct,tier_df.p_bonferroni)],
    textposition='outside',textfont=dict(size=10,family=F),showlegend=False),row=1,col=2)
fig.add_hline(y=0,line_color='#CCC',line_width=1,row=1,col=2)

for grp,color,name in [(0,NAV,'Control'),(1,RED,'Treatment')]:
    fig.add_trace(go.Box(y=promo[promo.treatment==grp].n_visits,name=name,
        marker_color=color,line_color=color,fillcolor=color,opacity=0.6,
        boxmean=True,legendgroup=name,showlegend=False),row=1,col=3)

tiers=['Bronze','Silver','Gold']
for vals,name,color,lg in [
    ([tier_retention[t]['control'] for t in tiers],'Control',NAV,'c'),
    ([tier_retention[t]['treatment'] for t in tiers],'Treatment',RED,'t')]:
    fig.add_trace(go.Bar(x=tiers,y=vals,name=name,marker_color=color,opacity=0.88,
        legendgroup=name,showlegend=False,
        text=[f"{v:.1f}%" for v in vals],textposition='outside',
        textfont=dict(size=10,family=F)),row=2,col=1)

for grp,color,name,lg in [(0,NAV,'Control','c'),(1,RED,'Treatment','t')]:
    sub=mig_summary[mig_summary.treatment==grp]
    fig.add_trace(go.Bar(x=sub.tier,y=sub.upgrade_rate,name=name,marker_color=color,
        opacity=0.88,legendgroup=name,showlegend=False,
        text=[f"{v:.1f}%" for v in sub.upgrade_rate],textposition='outside',
        textfont=dict(size=10,family=F)),row=2,col=2)

fig.add_trace(go.Bar(
    x=['Tier-Migrated','Non-Migrated'],y=[post_mig,post_nomig],
    marker_color=[GRN,GLD],opacity=0.88,
    text=[f"\${v:.0f}" for v in [post_mig,post_nomig]],
    textposition='outside',textfont=dict(size=11,family=F),showlegend=False),row=2,col=3)

roi2=roi_pivot.reset_index()
fig.add_trace(go.Bar(x=roi2.size_bucket,y=roi2.lift_pct,
    marker_color=[RED if v<8 else GRN for v in roi2.lift_pct],opacity=0.88,
    text=[f"{v:+.1f}%\n\${i:+.0f}/cust" for v,i in zip(roi2.lift_pct,roi2.incr)],
    textposition='outside',textfont=dict(size=9,family=F),showlegend=False),row=3,col=1)

fig.add_trace(go.Histogram(x=promo[promo.treatment==1].points_earned,
    marker_color=RED,opacity=0.75,nbinsx=30,showlegend=False),row=3,col=2)
fig.add_vline(x=promo[promo.treatment==1].points_earned.mean(),
    line_dash='dash',line_color='#333',line_width=1.5,row=3,col=2)

phase_spend=visits.groupby(['phase','treatment']).spend.mean().reset_index()
phase_order={'pre':0,'promo':1,'post':2}
phase_spend['order']=phase_spend.phase.map(phase_order)
phase_spend=phase_spend.sort_values('order')
for grp,color,name in [(0,NAV,'Control'),(1,RED,'Treatment')]:
    sub=phase_spend[phase_spend.treatment==grp]
    fig.add_trace(go.Scatter(x=sub.phase,y=sub.spend,mode='lines+markers+text',
        name=name,line=dict(color=color,width=2.5),
        marker=dict(size=9,color=color,line=dict(color='white',width=2)),
        text=[f"\${v:.1f}" for v in sub.spend],textposition='top center',
        textfont=dict(size=10,family=F),legendgroup=name,showlegend=False),row=3,col=3)

fig.update_layout(height=1100,width=1380,paper_bgcolor=BG,plot_bgcolor=WH,
    font=dict(family=F,color='#1A1A1A'),barmode='group',
    title=dict(text=(f"<b>Grocery Loyalty — Double Points Promotion A/B Test</b><br>"
        f"<span style='font-size:12px;color:#888'>n={N_CUSTOMERS:,} loyalty members  ·  "
        f"{PROMO_WEEKS}-week promotion  ·  {POST_WEEKS}-week follow-up  ·  "
        f"Overall lift: {lift_pct:+.1f}% (p={p_val:.4f}, Cohen d={cohen_d:.3f})</span>"),
        x=0.5,xanchor='center',y=0.99,yanchor='top',
        font=dict(size=18,color=NAV,family=F)),
    legend=dict(orientation='h',x=0.5,xanchor='center',y=1.03,yanchor='bottom',
        font=dict(size=11,family=F),bgcolor='rgba(255,255,255,0.9)',
        bordercolor='#DDD',borderwidth=1),
    margin=dict(t=140,b=60,l=60,r=40))

for (r,c),(xt,yt) in {
    (1,1):('Spend (\$)',''),
    (1,2):('Tier','Lift (%)'),
    (1,3):('Group','Visits'),
    (2,1):('Tier','Retention (%)'),
    (2,2):('Tier','Upgrade Rate (%)'),
    (2,3):('Segment','90-Day Spend (\$)'),
    (3,1):('Store Size','Lift (%)'),
    (3,2):('Points Earned','Count'),
    (3,3):('Phase','Avg Spend/Visit (\$)'),
}.items():
    fig.update_xaxes(title_text=xt,title_font=dict(family=F,size=11,color='#555'),**AX,row=r,col=c)
    fig.update_yaxes(title_text=yt,title_font=dict(family=F,size=11,color='#555'),**AX,row=r,col=c)

for ann in fig.layout.annotations:
    ann.update(font=dict(color=NAV,family=F,size=12))

out='/Users/amyway/Desktop/grocery-loyalty-dbms-sql-design/ab_testing/promotion_ab_dashboard.html'
fig.write_html(out,include_plotlyjs='cdn',full_html=True)
print(f"Dashboard saved: {out}")

pd.DataFrame(tier_results).to_csv(
    '/Users/amyway/Desktop/grocery-loyalty-dbms-sql-design/ab_testing/ab_test_results.csv',index=False)

print(f"""
EXECUTIVE SUMMARY
Overall lift: {lift_pct:+.1f}%  p={p_val:.4f}  Cohen d={cohen_d:.3f}
Freq lift: {freq_lift:+.1f}%
Bronze retention gap: {tier_retention['Bronze']['gap']:+.1f}pp  (cherry-picker risk)
Gold   retention gap: {tier_retention['Gold']['gap']:+.1f}pp
LTV delta migrated:   \${ltv_delta:+.2f}
""")
