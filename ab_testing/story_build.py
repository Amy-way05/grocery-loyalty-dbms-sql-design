# -*- coding: utf-8 -*-
import os

base = os.path.dirname(os.path.abspath(__file__))

def read(name):
    with open(f'{base}/{name}') as f:
        return f.read()

chart_bias = read('chart_bias.svg')
chart_naive = read('chart_naive_vs_causal.svg')
chart_income = read('chart_income.svg')
chart_decay = read('chart_decay.svg')
chart_categories = read('chart_categories.svg')

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Campaign 18: What a $140 Coupon Effect Actually Looks Like</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {
    --ink: #111111; --paper: #FFFFFF; --accent: #2546F0;
    --muted: #B9B9B9; --muted-text: #8A8A8A; --line: #EAEAEA; --panel: #F7F7F8;
  }
  * { box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body {
    margin: 0; background: var(--paper); color: var(--ink);
    font-family: 'Inter', -apple-system, sans-serif;
    -webkit-font-smoothing: antialiased;
  }
  .mono { font-family: 'IBM Plex Mono', monospace; }
  .wrap { max-width: 740px; margin: 0 auto; padding: 0 28px; }
  .wrap-wide { max-width: 860px; margin: 0 auto; padding: 0 28px; }

  header.masthead { padding: 80px 0 0 0; }
  h1.headline {
    font-size: 2.6rem; line-height: 1.2; font-weight: 800; letter-spacing: -0.02em;
    color: var(--ink); margin: 0 0 24px 0; max-width: 680px;
  }
  h1.headline .accent { color: var(--accent); }
  .dek { font-size: 1.1rem; line-height: 1.6; color: #444; max-width: 580px; margin: 0 0 8px 0; }
  .byline { font-size: 0.85rem; color: var(--muted-text); margin-top: 18px; }

  .stat-strip {
    display: flex; flex-wrap: wrap; margin-top: 50px; border-top: 1px solid var(--ink);
  }
  .stat { flex: 1; min-width: 150px; padding: 20px 24px 20px 0; border-right: 1px solid var(--line); }
  .stat:last-child { border-right: none; }
  .stat .num { font-size: 2rem; font-weight: 700; display: block; }
  .stat .lbl { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted-text); margin-top: 6px; display: block; }

  section { padding: 64px 0; border-bottom: 1px solid var(--line); }
  section.panel { background: var(--panel); }
  h2 {
    font-size: 1.6rem; font-weight: 700; line-height: 1.3; letter-spacing: -0.01em;
    margin: 0 0 20px 0; max-width: 620px;
  }
  p.body { font-size: 1.05rem; line-height: 1.72; color: #333; margin-bottom: 18px; max-width: 640px; }
  p.body b { color: var(--ink); font-weight: 700; }

  .chart-frame { background: white; border: 1px solid var(--line); padding: 24px 22px 16px 22px; margin: 28px 0; }
  .chart-caption { font-size: 0.8rem; color: var(--muted-text); margin-top: 12px; border-top: 1px solid var(--line); padding-top: 12px; line-height: 1.5; }

  .emphasis {
    font-size: 1.3rem; font-weight: 600; line-height: 1.5; color: var(--ink);
    margin: 30px 0; max-width: 600px;
  }
  .emphasis .accent { color: var(--accent); }

  .tool-card { background: var(--panel); border: 1px solid var(--line); padding: 32px; margin-top: 28px; }
  .tool-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 26px; margin-bottom: 26px; }
  @media (max-width: 640px) { .tool-grid { grid-template-columns: 1fr; } }
  .field { margin-bottom: 20px; }
  .field label { display: block; font-size: 0.82rem; color: #555; margin-bottom: 8px; font-weight: 500; }
  .field .val { color: var(--accent); font-weight: 700; }
  input[type=range] { width: 100%; accent-color: var(--accent); height: 4px; }
  select {
    width: 100%; background: white; color: var(--ink); border: 1px solid #CCC;
    padding: 10px 12px; font-size: 0.95rem; font-family: inherit;
  }
  .result-row { display: flex; gap: 14px; flex-wrap: wrap; margin-top: 26px; padding-top: 26px; border-top: 1px solid var(--line); }
  .result { flex: 1; min-width: 140px; text-align: center; background: white; border: 1px solid var(--line); padding: 16px 10px; }
  .result .v { font-size: 1.6rem; font-weight: 700; }
  .result .l { font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted-text); margin-top: 4px; }
  .verdict { margin-top: 18px; padding: 16px 18px; border-left: 3px solid var(--ink); font-size: 0.95rem; line-height: 1.55; background: white; }
  .verdict.go { border-left-color: var(--accent); }
  .verdict.hold { border-left-color: var(--muted); }

  footer { padding: 40px 0 70px 0; font-size: 0.82rem; color: var(--muted-text); line-height: 1.7; }
  footer a { color: var(--accent); }
  .methodology { font-size: 0.85rem; color: #444; background: white; border: 1px solid var(--line); padding: 18px 20px; margin-top: 18px; line-height: 1.7; }
</style>
</head>
<body>

<header class="masthead">
  <div class="wrap">
    <h1 class="headline">This coupon campaign claimed a 78% lift.<br>The real number is <span class="accent mono">$140</span>.</h1>
    <p class="dek">A causal analysis of a real promotion run by a U.S. grocery retailer, using propensity matching and difference in differences on 1.47 million real transactions.</p>
    <div class="byline">Amrutha Ravikumar. Data: Dunnhumby, "The Complete Journey"</div>
    <div class="stat-strip">
      <div class="stat"><span class="num mono">1,133</span><span class="lbl">Households Exposed</span></div>
      <div class="stat"><span class="num mono">214</span><span class="lbl">Redeemed a Coupon</span></div>
      <div class="stat"><span class="num mono accent" style="color:var(--accent)">$140</span><span class="lbl">True Incremental Spend</span></div>
      <div class="stat"><span class="num mono">+1,094%</span><span class="lbl">Campaign ROI</span></div>
    </div>
  </div>
</header>

<section>
  <div class="wrap">
    <h2>The number everyone would have reported is wrong</h2>
    <p class="body">If this analysis were run the way most retail dashboards run it, comparing the spending of people who redeemed a coupon against everyone who didn't, the headline would write itself: <b>a 78% increase in spend.</b> That figure would make it into a slide deck, a board update, perhaps a case study. It would also be almost entirely wrong.</p>
    <p class="body">The problem surfaces the moment you look at these two groups <i>before</i> the campaign ever launched.</p>
    <div class="chart-frame">
      CHART_BIAS_PLACEHOLDER
      <div class="chart-caption">Average household grocery spend in the eight weeks preceding the campaign, before any coupon had been issued or redeemed.</div>
    </div>
    <p class="emphasis">They are not an average customer converted by a coupon. They are a pre-existing heavy shopper who also happened to clip one.</p>
    <p class="body">People who went on to redeem this coupon were already spending 54% more than everyone else, weeks before the promotion existed. Comparing their post-campaign spend to the rest of the base doesn't measure what the campaign did. It measures who these people already were.</p>
  </div>
</section>

<section class="panel">
  <div class="wrap">
    <h2>What is the campaign actually worth?</h2>
    <p class="body">To isolate the campaign's true effect, each redeemer was matched to a non-redeemer with a near-identical pre-campaign spending history, a technique called <b>propensity score matching</b>. With comparable households on both sides, the change in spending from before the campaign to during it was measured for each group. The difference between those two changes is the effect the campaign actually caused, a method known as <b>difference in differences</b>.</p>
    <div class="chart-frame">
      CHART_NAIVE_PLACEHOLDER
      <div class="chart-caption">Spend lift per household: the naive estimate (dashed) versus the bias corrected causal estimate, with its 95% confidence interval.</div>
    </div>
    <p class="body">The corrected effect is <b>$139.99 in incremental spend per household</b>, statistically robust (p is less than 0.0001, Cohen's d equals 0.58). Set against a coupon cost of just $2,509 across all 214 redeemers, that is an estimated <b>1,094% return</b>. The campaign worked. It simply worked at roughly 44 cents on every naive dollar claimed.</p>
  </div>
</section>

<section>
  <div class="wrap">
    <h2>The households who needed it most responded the most</h2>
    <p class="body">Breaking the corrected effect down by income tells a story that is both a business insight and, unusually, a socially welcome one.</p>
    <div class="chart-frame">
      CHART_INCOME_PLACEHOLDER
      <div class="chart-caption">Incremental spend by household income bracket, redeemers only.</div>
    </div>
    <p class="body">Households earning under $15,000 a year showed <b>$244</b> in incremental spend, among the strongest response of any segment, and households with three or more children showed an equally strong <b>$244</b> response. The highest income households showed no meaningful lift at all. Larger, lower income households are the most price sensitive shoppers in the base, and a well targeted coupon moves them furthest. The most profitable way to target this campaign and the most equitable way to target it are the same strategy.</p>
  </div>
</section>

<section class="panel">
  <div class="wrap">
    <h2>Does it last, or is it just pantry loading?</h2>
    <p class="body">The real test of a promotion built to earn loyalty isn't what happens while the discount is live. It's what happens the week after, once it's gone.</p>
    <div class="chart-frame">
      CHART_DECAY_PLACEHOLDER
      <div class="chart-caption">Causal spend lift during the campaign versus an equal length window immediately afterward.</div>
    </div>
    <p class="body">Only <b>16%</b> of the lift survives once the promotion ends. This is consistent with pantry loading rather than habit formation. A single large campaign is unlikely to build lasting engagement on its own. A steadier cadence of smaller, rotating promotions would likely produce more durable results per dollar spent.</p>
  </div>
</section>

<section>
  <div class="wrap">
    <h2>They didn't just buy the discounted item</h2>
    <p class="body">A common risk with coupon promotions is that shoppers buy only the promoted product and nothing else. The basket data says otherwise here.</p>
    <div class="chart-frame">
      CHART_CATEGORIES_PLACEHOLDER
      <div class="chart-caption">Total category spend during the campaign window, by redemption status, across the six largest departments.</div>
    </div>
    <p class="body">Redeemers shopped <b>9.3 distinct departments</b> on average during the campaign, against <b>8.4</b> for non-redeemers. The coupon produced a genuine cross sell halo: it drew people toward a wider basket, not merely toward the one item on sale.</p>
  </div>
</section>

<section class="panel" id="tool">
  <div class="wrap-wide">
    <h2>A targeting tool a marketing team could use tomorrow morning</h2>
    <p class="body">Five findings are useful. A working tool is better. This is an uplift model trained on this campaign's real household data, using a two model (T-learner) approach: one model learns how redeemers' spending changed, a second learns how non-redeemers' spending changed under identical conditions, and the gap between their predictions for any given household profile is that household's personalized expected uplift from being targeted.</p>

    <div class="tool-card">
      <div class="tool-grid">
        <div>
          <div class="field">
            <label>Typical 8 week grocery spend: <span class="val mono" id="spendVal">$400</span></label>
            <input type="range" id="spend" min="50" max="2000" value="400" step="25">
          </div>
          <div class="field">
            <label>Visits in that window: <span class="val mono" id="visitsVal">12</span></label>
            <input type="range" id="visits" min="1" max="40" value="12" step="1">
          </div>
          <div class="field">
            <label>Household income bracket</label>
            <select id="income">
              <option value="7.5">Under $15K</option>
              <option value="19.5">$15K to $24K</option>
              <option value="29.5">$25K to $34K</option>
              <option value="42">$35K to $49K</option>
              <option value="62" selected>$50K to $74K</option>
              <option value="87">$75K to $99K</option>
              <option value="112">$100K to $124K</option>
              <option value="137">$125K to $149K</option>
              <option value="162">$150K to $174K</option>
              <option value="187">$175K to $199K</option>
              <option value="225">$200K to $249K</option>
              <option value="275">$250K+</option>
            </select>
          </div>
        </div>
        <div>
          <div class="field">
            <label>Household size: <span class="val mono" id="hhVal">2</span></label>
            <input type="range" id="hhsize" min="1" max="8" value="2" step="1">
          </div>
          <div class="field">
            <label>Children in household</label>
            <select id="kids">
              <option value="0" selected>0</option>
              <option value="1">1</option>
              <option value="2">2</option>
              <option value="3">3+</option>
            </select>
          </div>
        </div>
      </div>

      <div class="result-row">
        <div class="result"><div class="v mono" id="upliftOut" style="color:var(--accent)">$0</div><div class="l">Predicted Uplift</div></div>
        <div class="result"><div class="v mono" id="costOut">$11.73</div><div class="l">Est. Coupon Cost</div></div>
        <div class="result"><div class="v mono" id="roiOut">0%</div><div class="l">Expected ROI</div></div>
      </div>
      <div class="verdict go" id="verdict">Adjust the inputs above to see a live targeting recommendation.</div>
    </div>

    <div class="methodology">
      <b>Methodology.</b> Uplift coefficients were estimated via two separate ordinary least squares models fit on the matched causal sample: one on redeemers, one on non-redeemers, each regressing spend change on pre-period spend, pre-period visit count, household income midpoint, household size, and number of children. The uplift score for a given profile is the difference between the two models' predictions. Coefficients are fixed and computed from the full analysis. This calculator runs entirely in your browser.
    </div>
  </div>
</section>

<footer>
  <div class="wrap">
    <p><b>Data source.</b> Dunnhumby, "The Complete Journey," 1,469,307 real transactions from 2,500 U.S. households over two years, including genuine campaign exposure and coupon redemption records.</p>
    <p><b>Methods.</b> Propensity score matching (nearest neighbor, caliper equals 0.05) validated by covariate balance testing, difference in differences estimation, T-learner uplift modeling.</p>
    <p>Amrutha Ravikumar. M.P.S. Analytics, Northeastern University, Roux Institute. 2026 &nbsp;&middot;&nbsp; <a href="https://github.com/Amy-way05/grocery-loyalty-dbms-sql-design">View the code on GitHub</a></p>
  </div>
</footer>

<script>
  const spend = document.getElementById('spend');
  const visits = document.getElementById('visits');
  const income = document.getElementById('income');
  const hhsize = document.getElementById('hhsize');
  const kids = document.getElementById('kids');
  const spendVal = document.getElementById('spendVal');
  const visitsVal = document.getElementById('visitsVal');
  const hhVal = document.getElementById('hhVal');
  const upliftOut = document.getElementById('upliftOut');
  const costOut = document.getElementById('costOut');
  const roiOut = document.getElementById('roiOut');
  const verdict = document.getElementById('verdict');

  const COEF = {
    intercept: 83.6407, pre_spend: 0.1648, pre_visits: -1.3944,
    income_num: -0.3634, household_size: -19.3854, kids_count_num: 34.3229
  };
  const AVG_COST = 11.73;

  function calc() {
    const s = parseFloat(spend.value);
    const v = parseFloat(visits.value);
    const inc = parseFloat(income.value);
    const hh = parseFloat(hhsize.value);
    const k = parseFloat(kids.value);
    spendVal.textContent = '$' + s.toLocaleString();
    visitsVal.textContent = v;
    hhVal.textContent = hh;
    let uplift = COEF.intercept + COEF.pre_spend*s + COEF.pre_visits*v +
                 COEF.income_num*inc + COEF.household_size*hh + COEF.kids_count_num*k;
    const roi = ((uplift - AVG_COST) / AVG_COST) * 100;
    upliftOut.textContent = '$' + uplift.toFixed(0);
    costOut.textContent = '$' + AVG_COST.toFixed(2);
    roiOut.textContent = (roi>=0?'+':'') + roi.toFixed(0) + '%';
    roiOut.style.color = roi >= 0 ? 'var(--accent)' : '#999';
    if (uplift > AVG_COST * 1.5) {
      verdict.className = 'verdict go';
      verdict.innerHTML = '<b>Target this household.</b> Predicted uplift of $' + uplift.toFixed(0) +
        ' comfortably exceeds the typical coupon cost of $' + AVG_COST.toFixed(2) +
        ', for an expected return of ' + (roi>=0?'+':'') + roi.toFixed(0) + '%.';
    } else {
      verdict.className = 'verdict hold';
      verdict.innerHTML = '<b>Lower priority for this campaign.</b> Predicted uplift of $' +
        uplift.toFixed(0) + ' is close to or below the break even threshold. Consider a ' +
        'lighter touch or lower cost offer for this profile instead.';
    }
  }
  [spend, visits, income, hhsize, kids].forEach(el => el.addEventListener('input', calc));
  calc();
</script>

</body>
</html>
"""

HTML = HTML.replace('CHART_BIAS_PLACEHOLDER', chart_bias)
HTML = HTML.replace('CHART_NAIVE_PLACEHOLDER', chart_naive)
HTML = HTML.replace('CHART_INCOME_PLACEHOLDER', chart_income)
HTML = HTML.replace('CHART_DECAY_PLACEHOLDER', chart_decay)
HTML = HTML.replace('CHART_CATEGORIES_PLACEHOLDER', chart_categories)

with open(f'{base}/index.html', 'w') as f:
    f.write(HTML)

print(f"Page rebuilt: {len(HTML):,} characters, no dashes")
