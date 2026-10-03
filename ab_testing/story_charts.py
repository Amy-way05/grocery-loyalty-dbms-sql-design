# -*- coding: utf-8 -*-
INK = "#111111"
ACCENT = "#2546F0"
MUTED = "#B9B9B9"
MUTED_TEXT = "#8A8A8A"
LINE = "#EAEAEA"

naive_lift = 731.52 - 410.56
pre_t, pre_c = 598.74, 387.62
did_estimate = 139.99
ci_lo, ci_hi = 94.35, 185.64
retention_pct = 15.8
during_did = 139.99
after_did = 22.14

income_data = [
    ("250K+", -146.12), ("175 to 199K", -8.01), ("25 to 34K", 21.03), ("15 to 24K", 88.48),
    ("35 to 49K", 83.80), ("50 to 74K", 106.94), ("125 to 149K", 125.55), ("75 to 99K", 142.07),
    ("200 to 249K", 184.43), ("100 to 124K", 234.00), ("Under 15K", 243.89), ("150 to 174K", 259.75),
]

cat_data = [
    ("Grocery", 50186.42, 77504.89), ("Drug / GM", 13924.81, 20818.20),
    ("Fuel", 7416.77, 12826.84), ("Produce", 6636.72, 9863.02),
    ("Meat", 6553.21, 9806.45), ("Deli", 3631.77, 4867.18),
]

def svg_open(w, h):
    return f'<svg viewBox="0 0 {w} {h}" width="100%" xmlns="http://www.w3.org/2000/svg">'

def text(x, y, s, size=13, color=INK, weight=400, anchor="start"):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}" font-family="Inter, -apple-system, sans-serif">{s}</text>'

def num_text(x, y, s, size=24, color=INK, weight=700, anchor="start"):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}" font-family="\'IBM Plex Mono\', monospace">{s}</text>'

def chart_bias():
    w, h = 640, 260
    max_v = 700; bar_h = 44; y1, y2 = 60, 148; bx = 230
    bw1 = (pre_t/max_v)*330; bw2 = (pre_c/max_v)*330
    svg = [svg_open(w,h)]
    svg.append(text(0, 28, "AVG SPEND, 8 WEEKS BEFORE THE CAMPAIGN BEGAN", size=11, color=MUTED_TEXT, weight=600))
    svg.append(f'<rect x="{bx}" y="{y1}" width="{bw1:.1f}" height="{bar_h}" fill="{ACCENT}"/>')
    svg.append(text(bx-14, y1+bar_h/2+5, "Would be redeemers", size=13, anchor="end"))
    svg.append(num_text(bx+bw1+14, y1+bar_h/2+7, f"${pre_t:,.0f}", size=20, color=ACCENT))
    svg.append(f'<rect x="{bx}" y="{y2}" width="{bw2:.1f}" height="{bar_h}" fill="{INK}"/>')
    svg.append(text(bx-14, y2+bar_h/2+5, "Would be non redeemers", size=13, anchor="end"))
    svg.append(num_text(bx+bw2+14, y2+bar_h/2+7, f"${pre_c:,.0f}", size=20, color=INK))
    svg.append(f'<line x1="{bx}" y1="{y1-10}" x2="{bx}" y2="{y2+bar_h+16}" stroke="{LINE}" stroke-width="1"/>')
    svg.append(text(bx, y2+bar_h+36, "54.5% GAP, BEFORE EITHER GROUP EVER SAW THIS CAMPAIGN", size=11, color=ACCENT, weight=600))
    svg.append('</svg>')
    return "".join(svg)

def chart_naive_vs_causal():
    w, h = 640, 300
    max_v = naive_lift * 1.15; bw = 120; base_y = 230; scale = 150/max_v
    x1, x2 = 170, 400
    h1 = naive_lift*scale; h2 = did_estimate*scale
    svg = [svg_open(w,h)]
    svg.append(f'<line x1="60" y1="{base_y}" x2="580" y2="{base_y}" stroke="{INK}" stroke-width="1"/>')
    svg.append(f'<rect x="{x1}" y="{base_y-h1:.1f}" width="{bw}" height="{h1:.1f}" fill="none" stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="5,4"/>')
    svg.append(num_text(x1+bw/2, base_y-h1-16, f"${naive_lift:,.0f}", size=26, color=MUTED_TEXT, anchor="middle"))
    svg.append(text(x1+bw/2, base_y+26, "NAIVE COMPARISON", size=10.5, color=MUTED_TEXT, anchor="middle", weight=600))
    svg.append(f'<rect x="{x2}" y="{base_y-h2:.1f}" width="{bw}" height="{h2:.1f}" fill="{ACCENT}"/>')
    svg.append(num_text(x2+bw/2, base_y-h2-16, f"${did_estimate:,.0f}", size=26, color=ACCENT, anchor="middle"))
    svg.append(text(x2+bw/2, base_y+26, "CAUSAL ESTIMATE", size=10.5, color=INK, anchor="middle", weight=600))
    ci_top = base_y - ci_hi*scale; ci_bot = base_y - ci_lo*scale
    svg.append(f'<line x1="{x2+bw+16}" y1="{ci_top:.1f}" x2="{x2+bw+16}" y2="{ci_bot:.1f}" stroke="{INK}" stroke-width="1"/>')
    svg.append(f'<line x1="{x2+bw+11}" y1="{ci_top:.1f}" x2="{x2+bw+21}" y2="{ci_top:.1f}" stroke="{INK}" stroke-width="1"/>')
    svg.append(f'<line x1="{x2+bw+11}" y1="{ci_bot:.1f}" x2="{x2+bw+21}" y2="{ci_bot:.1f}" stroke="{INK}" stroke-width="1"/>')
    svg.append(text(x2+bw+27, (ci_top+ci_bot)/2+4, "95% CI", size=10, color=MUTED_TEXT))
    svg.append('</svg>')
    return "".join(svg)

def chart_income():
    w, h = 680, 420
    category_label_x = 126
    zero_x = 380
    scale = 0.5
    row_h = 30
    svg = [svg_open(w,h)]
    svg.append(f'<line x1="{zero_x}" y1="20" x2="{zero_x}" y2="{20+len(income_data)*row_h+6}" stroke="{INK}" stroke-width="1"/>')
    for i,(label,val) in enumerate(income_data):
        y = 20 + i*row_h + row_h*0.65
        bw = abs(val)*scale
        color = ACCENT if val>=0 else MUTED
        bx = zero_x if val>=0 else zero_x-bw
        svg.append(f'<rect x="{bx:.1f}" y="{y-13:.1f}" width="{bw:.1f}" height="16" fill="{color}"/>')
        svg.append(text(category_label_x, y, label, size=12, anchor="end"))
        if val >= 0:
            label_x = zero_x+bw+10
            anchor = "start"
        else:
            label_x = zero_x-bw-10
            anchor = "end"
        tcolor = ACCENT if val>=0 else MUTED_TEXT
        svg.append(num_text(label_x, y+4, f"${val:+,.0f}", size=12, color=tcolor, weight=600, anchor=anchor))
    svg.append('</svg>')
    return "".join(svg)

def chart_decay():
    w, h = 560, 280
    max_v = during_did*1.2; scale = 170/max_v; base_y = 220; bw = 120
    x1, x2 = 140, 340
    h1 = during_did*scale; h2 = after_did*scale
    svg = [svg_open(w,h)]
    svg.append(f'<line x1="60" y1="{base_y}" x2="500" y2="{base_y}" stroke="{INK}" stroke-width="1"/>')
    svg.append(f'<rect x="{x1}" y="{base_y-h1:.1f}" width="{bw}" height="{h1:.1f}" fill="{ACCENT}"/>')
    svg.append(num_text(x1+bw/2, base_y-h1-14, f"${during_did:,.0f}", size=22, color=ACCENT, anchor="middle"))
    svg.append(text(x1+bw/2, base_y+24, "DURING THE CAMPAIGN", size=10.5, anchor="middle", weight=600))
    svg.append(f'<rect x="{x2}" y="{base_y-h2:.1f}" width="{bw}" height="{h2:.1f}" fill="{MUTED}"/>')
    svg.append(num_text(x2+bw/2, base_y-h2-14, f"${after_did:,.0f}", size=22, color=MUTED_TEXT, anchor="middle"))
    svg.append(text(x2+bw/2, base_y+24, "EQUAL WINDOW AFTER IT ENDED", size=10.5, anchor="middle", weight=600))
    svg.append(text(x2+bw/2, base_y+42, f"ONLY {retention_pct:.0f}% OF THE LIFT REMAINS", size=10.5, color=ACCENT, weight=700, anchor="middle"))
    svg.append('</svg>')
    return "".join(svg)

def chart_categories():
    w, h = 680, 360
    left = 70; top = 20; group_w = 95; bar_w = 32
    max_v = max(v for _,a,b in cat_data for v in (a,b))
    scale = 230/max_v; base_y = top+250
    svg = [svg_open(w,h)]
    svg.append(f'<line x1="{left-10}" y1="{base_y}" x2="{left + len(cat_data)*group_w}" y2="{base_y}" stroke="{INK}" stroke-width="1"/>')
    for i,(label,a,b) in enumerate(cat_data):
        gx = left + i*group_w
        ha = a*scale; hb = b*scale
        svg.append(f'<rect x="{gx}" y="{base_y-ha:.1f}" width="{bar_w}" height="{ha:.1f}" fill="{MUTED}"/>')
        svg.append(f'<rect x="{gx+bar_w+4}" y="{base_y-hb:.1f}" width="{bar_w}" height="{hb:.1f}" fill="{ACCENT}"/>')
        svg.append(text(gx+bar_w+2, base_y+20, label, size=11, anchor="middle"))
    svg.append(f'<rect x="{left}" y="{top-10}" width="14" height="14" fill="{MUTED}"/>')
    svg.append(text(left+20, top+1, "NON REDEEMERS", size=10.5, weight=600))
    svg.append(f'<rect x="{left+160}" y="{top-10}" width="14" height="14" fill="{ACCENT}"/>')
    svg.append(text(left+180, top+1, "REDEEMERS", size=10.5, weight=600))
    svg.append('</svg>')
    return "".join(svg)

if __name__ == "__main__":
    import os
    base = os.path.dirname(os.path.abspath(__file__))
    charts = {
        'chart_bias': chart_bias(), 'chart_naive_vs_causal': chart_naive_vs_causal(),
        'chart_income': chart_income(), 'chart_decay': chart_decay(),
        'chart_categories': chart_categories(),
    }
    for name, svg in charts.items():
        with open(f'{base}/{name}.svg', 'w') as f:
            f.write(svg)
        print(f"{name}: {len(svg)} chars")
    print("Charts regenerated, income chart fixed.")
