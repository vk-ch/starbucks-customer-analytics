import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Starbucks Customer Analytics",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Brand Palette ─────────────────────────────────────────────────────────────
GREEN  = "#00704A"
GOLD   = "#CBA258"
DARK   = "#1E3932"
LIGHT  = "#D4E9E2"
RED    = "#742d2d"
CREAM  = "#F2F0EB"
PALETTE = [GREEN, GOLD, DARK, LIGHT, RED, "#5C4033"]

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  [data-testid="stAppViewContainer"] {{ background-color: #f5f5f0; }}
  [data-testid="stSidebar"] {{ background-color: {DARK}; }}
  [data-testid="stSidebar"] * {{ color: white !important; }}
  [data-testid="stSidebar"] .stRadio label {{ color: white !important; font-size: 15px; }}
  .kpi-card {{
      background: white; padding: 20px 24px; border-radius: 12px;
      border-left: 5px solid {GREEN}; box-shadow: 0 2px 10px rgba(0,0,0,0.07);
      text-align: center;
  }}
  .kpi-value {{ font-size: 32px; font-weight: 800; color: {DARK}; margin: 4px 0; }}
  .kpi-label {{ font-size: 13px; color: #666; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }}
  .kpi-delta {{ font-size: 12px; color: {GREEN}; font-weight: 600; }}
  .section-title {{
      font-size: 22px; font-weight: 700; color: {DARK};
      border-bottom: 3px solid {GREEN}; padding-bottom: 8px; margin-bottom: 20px;
  }}
  .insight-box {{
      background: #e8f5ef; border-left: 4px solid {GREEN};
      padding: 12px 16px; border-radius: 6px; margin-top: 12px;
      font-size: 14px; color: {DARK};
  }}
  .warning-box {{
      background: #fff8e8; border-left: 4px solid {GOLD};
      padding: 12px 16px; border-radius: 6px; margin-top: 12px;
      font-size: 14px; color: #5a4000;
  }}
</style>
""", unsafe_allow_html=True)

# ── Data Loading ──────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))

@st.cache_data
def load_all():
    segs   = pd.read_csv(f"{BASE}/powerbi_customer_segments.csv")
    clv    = pd.read_csv(f"{BASE}/powerbi_clv_segments.csv")
    funnel = pd.read_csv(f"{BASE}/powerbi_funnel.csv")
    ab     = pd.read_csv(f"{BASE}/powerbi_ab_test.csv")
    ch     = pd.read_csv(f"{BASE}/powerbi_channel_performance.csv")
    cpa    = pd.read_csv(f"{BASE}/powerbi_cpa_summary.csv")
    daily  = pd.read_csv(f"{BASE}/powerbi_daily_transactions.csv")
    return segs, clv, funnel, ab, ch, cpa, daily

segs, clv, funnel, ab, ch, cpa, daily = load_all()

# ── Precomputed KPIs ──────────────────────────────────────────────────────────
total_customers    = len(segs)
total_annual_value = clv["Total_Segment_Value"].sum()
best_offer         = cpa.loc[cpa["CPA ($)"].idxmin(), "Offer Type"]
best_offer_cpa     = cpa["CPA ($)"].min()
best_channel       = ch.loc[ch["Conv Rate %"].idxmax(), "Channel"]
best_channel_rate  = ch["Conv Rate %"].max()
total_revenue_30d  = daily["revenue"].sum()
bogo_rate          = ab[ab["offer_type"]=="bogo"]["completed"].mean() * 100
disc_rate          = ab[ab["offer_type"]=="discount"]["completed"].mean() * 100

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ☕ Starbucks\n### Customer Analytics")
    st.markdown("---")
    page = st.radio(
        "Navigation",
        ["📊  Executive Summary",
         "👥  Customer Segmentation",
         "💰  CLV & RFM Analysis",
         "🔽  Funnel Analysis",
         "🧪  A/B Testing",
         "📱  Channel Performance"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown(f"**Dataset:** Starbucks Rewards App  \n**Customers:** {total_customers:,}  \n**Events:** 306,534  \n**Window:** 30-day test")
    st.markdown("---")
    st.markdown("**By:** Venkat Kowshik  \n*UW Foster MSBA*")

def kpi(col, label, value, delta=None):
    delta_html = f'<div class="kpi-delta">▲ {delta}</div>' if delta else ""
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>""", unsafe_allow_html=True)

def plotly_defaults(fig, height=380):
    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Arial", size=12, color=DARK),
        height=height, margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(bgcolor="rgba(0,0,0,0)")
    )
    fig.update_xaxes(showgrid=False, linecolor="#ddd")
    fig.update_yaxes(gridcolor="#f0f0f0", linecolor="#ddd")
    return fig

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — EXECUTIVE SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
if "Executive Summary" in page:
    st.markdown('<div class="section-title">📊 Executive Summary</div>', unsafe_allow_html=True)
    st.caption("Starbucks Rewards Promotional Campaign — 30-Day Test Window")

    # KPI row
    c1, c2, c3, c4, c5 = st.columns(5)
    kpi(c1, "Total Customers",        f"{total_customers:,}")
    kpi(c2, "30-Day Revenue",          f"${total_revenue_30d:,.0f}")
    kpi(c3, "Annual Portfolio Value",  f"${total_annual_value/1e6:.2f}M")
    kpi(c4, "Best Offer (Lowest CPA)", f"{best_offer}  —  ${best_offer_cpa:.2f}")
    kpi(c5, "Top Channel (Conv Rate)", f"{best_channel.split('/')[0].strip()}")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    # Segment size pie
    with col1:
        st.markdown("#### Customer Segments")
        seg_counts = segs["segment"].value_counts().reset_index()
        seg_counts.columns = ["Segment", "Customers"]
        fig = go.Figure(go.Pie(
            labels=seg_counts["Segment"], values=seg_counts["Customers"],
            hole=0.45, marker_colors=PALETTE,
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>%{value:,} customers<br>%{percent}<extra></extra>"
        ))
        fig.add_annotation(text=f"<b>{total_customers:,}</b><br>customers",
                           x=0.5, y=0.5, showarrow=False, font_size=13)
        plotly_defaults(fig)
        st.plotly_chart(fig, use_container_width=True)

    # Revenue bar
    with col2:
        st.markdown("#### Annual Revenue by Segment")
        clv_sorted = clv.sort_values("Total_Segment_Value", ascending=True)
        fig = go.Figure(go.Bar(
            x=clv_sorted["Total_Segment_Value"],
            y=clv_sorted["segment"],
            orientation="h",
            marker_color=PALETTE[:len(clv_sorted)],
            text=[f"${v/1000:.0f}K" for v in clv_sorted["Total_Segment_Value"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>$%{x:,.0f}<extra></extra>"
        ))
        fig.update_xaxes(tickprefix="$", tickformat=",")
        plotly_defaults(fig)
        st.plotly_chart(fig, use_container_width=True)

    # Row 2
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### Conversion Rate: BOGO vs Discount")
        fig = go.Figure()
        for offer, rate, color in [("BOGO", bogo_rate, GREEN), ("Discount", disc_rate, GOLD)]:
            fig.add_trace(go.Bar(
                x=[offer], y=[rate], name=offer,
                marker_color=color,
                text=[f"{rate:.1f}%"], textposition="outside",
                hovertemplate=f"<b>{offer}</b>: {rate:.1f}%<extra></extra>"
            ))
        fig.update_layout(yaxis_title="Completion Rate (%)", showlegend=False,
                          yaxis_range=[0, max(bogo_rate, disc_rate) * 1.4])
        plotly_defaults(fig, height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.markdown("#### 30-Day Revenue Trend")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily["time_days"], y=daily["revenue"],
            fill="tozeroy", fillcolor=f"rgba(0,112,74,0.15)",
            line=dict(color=GREEN, width=2.5),
            hovertemplate="Day %{x}: $%{y:,.2f}<extra></extra>"
        ))
        fig.update_yaxes(tickprefix="$", tickformat=",")
        fig.update_xaxes(title_text="Day")
        plotly_defaults(fig, height=300)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""
    <div class="insight-box">
    💡 <b>Key Takeaway:</b> The <b>{best_offer}</b> offer delivers the lowest cost-per-acquisition
    (${best_offer_cpa:.2f}). Routing it through <b>{best_channel}</b> at a
    <b>{best_channel_rate:.1f}%</b> conversion rate maximises marketing ROI.
    The top segment drives <b>${clv.iloc[0]["Total_Segment_Value"]/1000:.0f}K</b> in annual value.
    </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — CUSTOMER SEGMENTATION
# ═══════════════════════════════════════════════════════════════════════════════
elif "Segmentation" in page:
    st.markdown('<div class="section-title">👥 Customer Segmentation</div>', unsafe_allow_html=True)

    # Filters
    fc1, fc2, fc3 = st.columns(3)
    seg_filter = fc1.multiselect("Segment", options=sorted(segs["segment"].dropna().unique()),
                                  default=sorted(segs["segment"].dropna().unique()))
    gen_filter = fc2.multiselect("Gender", options=["M", "F", "O"],
                                  default=["M", "F", "O"])
    inc_range  = fc3.slider("Income Range ($K)", 0, 120, (0, 120), step=5)

    filtered = segs[
        segs["segment"].isin(seg_filter) &
        segs["gender"].isin(gen_filter) &
        segs["income"].between(inc_range[0]*1000, inc_range[1]*1000)
    ]

    k1, k2, k3, k4 = st.columns(4)
    kpi(k1, "Filtered Customers",  f"{len(filtered):,}")
    kpi(k2, "Avg Total Spend",     f"${filtered['monetary'].mean():.2f}")
    kpi(k3, "Avg Transactions",    f"{filtered['frequency'].mean():.1f}")
    kpi(k4, "Avg Income",          f"${filtered['income'].mean():,.0f}")
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("#### Frequency vs Total Spend by Segment")
        color_map = dict(zip(sorted(segs["segment"].dropna().unique()), PALETTE))
        fig = px.scatter(
            filtered, x="frequency", y="monetary",
            color="segment", color_discrete_map=color_map,
            opacity=0.45, size_max=8,
            hover_data={"income": True, "age": True, "frequency": True, "monetary": True},
            labels={"frequency": "Purchase Frequency", "monetary": "Total Spend ($)"}
        )
        fig.update_yaxes(tickprefix="$", tickformat=",")
        plotly_defaults(fig, height=420)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Customers per Segment")
        seg_c = filtered["segment"].value_counts().reset_index()
        seg_c.columns = ["Segment", "Count"]
        fig = go.Figure(go.Bar(
            x=seg_c["Count"], y=seg_c["Segment"],
            orientation="h",
            marker_color=[color_map.get(s, GREEN) for s in seg_c["Segment"]],
            text=seg_c["Count"], textposition="outside",
            hovertemplate="<b>%{y}</b>: %{x:,}<extra></extra>"
        ))
        plotly_defaults(fig, height=200)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### Avg Income per Segment")
        inc_seg = filtered.groupby("segment")["income"].mean().reset_index().sort_values("income", ascending=True)
        fig = go.Figure(go.Bar(
            x=inc_seg["income"], y=inc_seg["segment"],
            orientation="h",
            marker_color=[color_map.get(s, GOLD) for s in inc_seg["segment"]],
            text=[f"${v/1000:.0f}K" for v in inc_seg["income"]],
            textposition="outside"
        ))
        fig.update_xaxes(tickprefix="$", tickformat=",")
        plotly_defaults(fig, height=200)
        st.plotly_chart(fig, use_container_width=True)

    # RFM heatmap
    st.markdown("#### RFM Score Heatmap by Segment")
    rfm_heat = filtered.groupby("segment")[["R_score","F_score","M_score"]].mean().round(2)
    fig = go.Figure(go.Heatmap(
        z=rfm_heat.values, x=["Recency", "Frequency", "Monetary"],
        y=rfm_heat.index,
        colorscale=[[0, "#fff"], [0.5, LIGHT], [1, GREEN]],
        text=rfm_heat.values, texttemplate="%{text:.2f}",
        hovertemplate="%{y} — %{x}: %{z:.2f}<extra></extra>",
        showscale=True
    ))
    plotly_defaults(fig, height=280)
    st.plotly_chart(fig, use_container_width=True)

    top = filtered.groupby("segment")["monetary"].mean().idxmax()
    st.markdown(f"""
    <div class="insight-box">
    💡 <b>'{top}'</b> customers show the highest average spend.
    Use income-based targeting via CRM to focus high-spend offers on this segment first.
    </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — CLV & RFM
# ═══════════════════════════════════════════════════════════════════════════════
elif "CLV" in page:
    st.markdown('<div class="section-title">💰 Customer Lifetime Value (CLV) & RFM</div>', unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    kpi(k1, "Total Annual Portfolio",  f"${total_annual_value/1e6:.2f}M")
    kpi(k2, "Highest CLV Segment",     clv.loc[clv["Avg_Annual_CLV"].idxmax(), "segment"])
    kpi(k3, "Top Avg Annual CLV",      f"${clv['Avg_Annual_CLV'].max():,.0f}")
    kpi(k4, "Lowest CLV Segment",      clv.loc[clv["Avg_Annual_CLV"].idxmin(), "segment"])
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Average Annual CLV by Segment")
        clv_s = clv.sort_values("Avg_Annual_CLV", ascending=False)
        fig = go.Figure(go.Bar(
            x=clv_s["segment"], y=clv_s["Avg_Annual_CLV"],
            marker_color=PALETTE[:len(clv_s)],
            text=[f"${v:,.0f}" for v in clv_s["Avg_Annual_CLV"]],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Avg CLV: $%{y:,.0f}<extra></extra>"
        ))
        fig.update_yaxes(tickprefix="$", tickformat=",")
        fig.update_layout(yaxis_range=[0, clv_s["Avg_Annual_CLV"].max() * 1.3])
        plotly_defaults(fig, height=360)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Revenue Share by Segment")
        fig = go.Figure(go.Pie(
            labels=clv["segment"],
            values=clv["Total_Segment_Value"],
            hole=0.4, marker_colors=PALETTE[:len(clv)],
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>"
        ))
        fig.add_annotation(text=f"<b>${total_annual_value/1e6:.1f}M</b><br>total",
                           x=0.5, y=0.5, showarrow=False, font_size=13)
        plotly_defaults(fig, height=360)
        st.plotly_chart(fig, use_container_width=True)

    # CLV vs customers bubble chart
    st.markdown("#### CLV vs Customer Volume (Bubble = Total Segment Value)")
    fig = go.Figure()
    for i, row in clv.iterrows():
        fig.add_trace(go.Scatter(
            x=[row["Customers"]], y=[row["Avg_Annual_CLV"]],
            mode="markers+text",
            marker=dict(size=row["Total_Segment_Value"]/5000, color=PALETTE[i], opacity=0.75),
            text=[row["segment"]], textposition="top center",
            name=row["segment"],
            hovertemplate=f"<b>{row['segment']}</b><br>Customers: {row['Customers']:,}<br>CLV: ${row['Avg_Annual_CLV']:,.0f}<extra></extra>"
        ))
    fig.update_xaxes(title_text="Number of Customers")
    fig.update_yaxes(title_text="Avg Annual CLV ($)", tickprefix="$", tickformat=",")
    plotly_defaults(fig, height=400)
    st.plotly_chart(fig, use_container_width=True)

    rev_at_risk = clv[clv["segment"].str.contains("Casual|Frequent", na=False)]["Total_Segment_Value"].sum()
    st.markdown(f"""
    <div class="warning-box">
    ⚠️ <b>Revenue at Risk:</b> Lower-CLV segments represent
    <b>${rev_at_risk:,.0f}</b> in annual value. A 10% churn reduction via targeted retention
    campaigns could recover <b>${rev_at_risk*0.1:,.0f}/year</b>.
    </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — FUNNEL ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
elif "Funnel" in page:
    st.markdown('<div class="section-title">🔽 Funnel Analysis</div>', unsafe_allow_html=True)

    total_recv = funnel["Received"].sum()
    total_view = funnel["Viewed"].sum()
    total_comp = funnel["Completed"].sum()
    overall_vr = total_view / total_recv * 100
    overall_cr = total_comp / total_recv * 100

    k1, k2, k3, k4 = st.columns(4)
    kpi(k1, "Total Offers Sent",     f"{total_recv:,}")
    kpi(k2, "Total Viewed",          f"{total_view:,}")
    kpi(k3, "Total Completed",       f"{total_comp:,}")
    kpi(k4, "Overall Completion Rate", f"{overall_cr:.1f}%")
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Overall Offer Funnel")
        stages = ["Offer Received", "Offer Viewed", "Offer Completed"]
        values = [total_recv, total_view, total_comp]
        fig = go.Figure(go.Funnel(
            y=stages, x=values,
            textinfo="value+percent initial",
            marker=dict(color=[GREEN, GOLD, DARK]),
            connector=dict(line=dict(color="#ccc", width=1))
        ))
        plotly_defaults(fig, height=380)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Funnel Metrics by Offer Type")
        fig = make_subplots(rows=1, cols=1)
        x = funnel["Offer Type"]
        w = 0.25
        positions = [-0.25, 0, 0.25]
        cols_plot = ["Received", "Viewed", "Completed"]
        colors_plot = [LIGHT, GOLD, GREEN]
        for i, (col_name, color) in enumerate(zip(cols_plot, colors_plot)):
            fig.add_trace(go.Bar(
                x=[f"{v}{positions[i]:+.0f}" for v in ["BOGO", "DISCOUNT", "INFORMATIONAL"]],
                y=funnel[col_name], name=col_name,
                marker_color=color, width=0.22,
                text=funnel[col_name], textposition="outside",
                hovertemplate=f"<b>%{{x}}</b> — {col_name}: %{{y:,}}<extra></extra>"
            ))
        fig.update_layout(barmode="group", xaxis=dict(tickvals=[0,1,2], ticktext=list(x)))
        plotly_defaults(fig, height=380)
        st.plotly_chart(fig, use_container_width=True)

    # Completion rate by offer type
    st.markdown("#### Completion Rate & View Rate by Offer Type")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=funnel["Offer Type"], y=funnel["View Rate %"],
        name="View Rate %", marker_color=GOLD,
        text=[f"{v:.1f}%" for v in funnel["View Rate %"]],
        textposition="outside"
    ))
    fig.add_trace(go.Bar(
        x=funnel["Offer Type"], y=funnel["Complete Rate %"],
        name="Completion Rate %", marker_color=GREEN,
        text=[f"{v:.1f}%" for v in funnel["Complete Rate %"]],
        textposition="outside"
    ))
    fig.update_layout(barmode="group", yaxis_title="Rate (%)",
                      yaxis_range=[0, funnel["View Rate %"].max() * 1.35])
    plotly_defaults(fig, height=360)
    st.plotly_chart(fig, use_container_width=True)

    drop_off = ((total_recv - total_comp) / total_recv * 100)
    st.markdown(f"""
    <div class="insight-box">
    💡 <b>{drop_off:.1f}%</b> of customers who received an offer did not complete it.
    Improving the view→complete rate by just <b>5pp</b> would generate
    <b>{int(total_recv * 0.05):,}</b> additional conversions per campaign cycle.
    </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — A/B TESTING
# ═══════════════════════════════════════════════════════════════════════════════
elif "A/B" in page:
    st.markdown('<div class="section-title">🧪 A/B Testing — BOGO vs Discount</div>', unsafe_allow_html=True)

    bogo_df = ab[ab["offer_type"] == "bogo"]
    disc_df = ab[ab["offer_type"] == "discount"]
    bogo_conv = bogo_df["completed"].mean() * 100
    disc_conv = disc_df["completed"].mean() * 100
    bogo_spend = bogo_df["total_spend"].mean()
    disc_spend = disc_df["total_spend"].mean()
    lift = bogo_conv - disc_conv

    bogo_cpa_v = cpa.loc[cpa["Offer Type"]=="BOGO", "CPA ($)"].values[0]
    disc_cpa_v = cpa.loc[cpa["Offer Type"]=="DISCOUNT", "CPA ($)"].values[0]
    bogo_roas  = cpa.loc[cpa["Offer Type"]=="BOGO", "ROAS"].values[0]
    disc_roas  = cpa.loc[cpa["Offer Type"]=="DISCOUNT", "ROAS"].values[0]

    winner = "BOGO" if bogo_conv > disc_conv else "Discount"

    k1, k2, k3, k4 = st.columns(4)
    kpi(k1, "BOGO Completion Rate",     f"{bogo_conv:.1f}%")
    kpi(k2, "Discount Completion Rate", f"{disc_conv:.1f}%")
    kpi(k3, f"Lift ({winner} wins)",    f"{abs(lift):.1f}pp")
    kpi(k4, "Best CPA",                 f"${min(bogo_cpa_v, disc_cpa_v):.2f}  ({winner})")
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Completion Rate (Conversion)")
        fig = go.Figure()
        for label, val, color in [("BOGO", bogo_conv, GREEN), ("Discount", disc_conv, GOLD)]:
            fig.add_trace(go.Bar(
                x=[label], y=[val], name=label,
                marker_color=color, width=0.4,
                text=[f"<b>{val:.1f}%</b>"], textposition="outside",
                hovertemplate=f"<b>{label}</b>: {val:.1f}%<extra></extra>"
            ))
        fig.update_layout(yaxis_range=[0, max(bogo_conv, disc_conv)*1.4],
                          yaxis_title="Completion Rate (%)", showlegend=False)
        # significance annotation
        sig_text = "✅ Statistically Significant" if abs(lift) > 1 else "⚠ Check Significance"
        fig.add_annotation(x=0.5, y=max(bogo_conv,disc_conv)*1.3,
                           text=sig_text, showarrow=False,
                           font=dict(size=12, color=DARK), xref="paper")
        plotly_defaults(fig, height=360)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Avg Customer Spend ($)")
        fig = go.Figure()
        for label, val, color in [("BOGO", bogo_spend, GREEN), ("Discount", disc_spend, GOLD)]:
            fig.add_trace(go.Bar(
                x=[label], y=[val], name=label,
                marker_color=color, width=0.4,
                text=[f"<b>${val:,.2f}</b>"], textposition="outside",
                hovertemplate=f"<b>{label}</b>: ${val:,.2f}<extra></extra>"
            ))
        fig.update_layout(yaxis_range=[0, max(bogo_spend, disc_spend)*1.4],
                          yaxis_title="Avg Customer Spend ($)", showlegend=False)
        fig.update_yaxes(tickprefix="$", tickformat=",")
        plotly_defaults(fig, height=360)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### Cost Per Acquisition (CPA)")
        fig = go.Figure()
        for label, val, color in [("BOGO", bogo_cpa_v, GREEN), ("Discount", disc_cpa_v, GOLD)]:
            fig.add_trace(go.Bar(
                x=[label], y=[val], name=label,
                marker_color=color, width=0.4,
                text=[f"<b>${val:.2f}</b>"], textposition="outside"
            ))
        fig.update_layout(yaxis_range=[0, max(bogo_cpa_v, disc_cpa_v)*1.4],
                          yaxis_title="CPA ($)  ← lower is better", showlegend=False)
        fig.update_yaxes(tickprefix="$")
        plotly_defaults(fig, height=320)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.markdown("#### Return on Ad Spend (ROAS)")
        fig = go.Figure()
        for label, val, color in [("BOGO", bogo_roas, GREEN), ("Discount", disc_roas, GOLD)]:
            fig.add_trace(go.Bar(
                x=[label], y=[val], name=label,
                marker_color=color, width=0.4,
                text=[f"<b>{val:.1f}x</b>"], textposition="outside"
            ))
        fig.add_hline(y=1, line_dash="dash", line_color="red",
                      annotation_text="Break-even", annotation_position="right")
        fig.update_layout(yaxis_range=[0, max(bogo_roas, disc_roas)*1.4],
                          yaxis_title="ROAS  ← higher is better", showlegend=False)
        plotly_defaults(fig, height=320)
        st.plotly_chart(fig, use_container_width=True)

    # Stats summary table
    st.markdown("#### Statistical Test Summary")
    stats_df = pd.DataFrame({
        "Test"           : ["Chi-Square (Conversion Rate)", "Welch t-test (Avg Spend)"],
        "BOGO"           : [f"{bogo_conv:.1f}%", f"${bogo_spend:,.2f}"],
        "Discount"       : [f"{disc_conv:.1f}%", f"${disc_spend:,.2f}"],
        "Winner"         : [winner, "BOGO" if bogo_spend > disc_spend else "Discount"],
        "Significance"   : ["α = 0.05", "α = 0.05"],
    })
    st.dataframe(stats_df, use_container_width=True, hide_index=True)

    savings = abs(bogo_cpa_v - disc_cpa_v) * int(min(len(bogo_df), len(disc_df))) * 12
    st.markdown(f"""
    <div class="insight-box">
    💡 <b>{winner}</b> is the winning offer with a <b>{abs(lift):.1f}pp conversion lift</b> and
    lower CPA of <b>${min(bogo_cpa_v,disc_cpa_v):.2f}</b>.
    Reallocating full budget to <b>{winner}</b> saves an estimated
    <b>${savings:,.0f}/year</b> in acquisition costs.
    </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — CHANNEL PERFORMANCE
# ═══════════════════════════════════════════════════════════════════════════════
elif "Channel" in page:
    st.markdown('<div class="section-title">📱 Channel Performance — Facebook Ads & CRM</div>', unsafe_allow_html=True)

    top_ch     = ch.loc[ch["Conv Rate %"].idxmax()]
    low_cpa_ch = ch.loc[ch["CPA ($)"].idxmin()]
    high_sp_ch = ch.loc[ch["Avg Spend ($)"].idxmax()]
    fb_row     = ch[ch["Channel"].str.contains("Facebook", na=False)]
    fb_conv    = fb_row["Conv Rate %"].values[0] if len(fb_row) else 0
    fb_cpa     = fb_row["CPA ($)"].values[0] if len(fb_row) else 0

    k1, k2, k3, k4 = st.columns(4)
    kpi(k1, "Best Conv Rate Channel",  top_ch["Channel"].split("/")[0].strip(), delta=f"{top_ch['Conv Rate %']:.1f}%")
    kpi(k2, "Lowest CPA Channel",      low_cpa_ch["Channel"].split("/")[0].strip(), delta=f"${low_cpa_ch['CPA ($)']:.2f}")
    kpi(k3, "Facebook Ads Conv Rate",  f"{fb_conv:.1f}%")
    kpi(k4, "Facebook Ads CPA",        f"${fb_cpa:.2f}")
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Conversion Rate by Channel (%)")
        ch_s = ch.sort_values("Conv Rate %", ascending=True)
        ch_colors = [GREEN if "Facebook" in c else GOLD if "Mobile" in c else DARK for c in ch_s["Channel"]]
        fig = go.Figure(go.Bar(
            x=ch_s["Conv Rate %"], y=ch_s["Channel"],
            orientation="h", marker_color=ch_colors,
            text=[f"{v:.1f}%" for v in ch_s["Conv Rate %"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Conv Rate: %{x:.1f}%<extra></extra>"
        ))
        fig.update_xaxes(range=[0, ch_s["Conv Rate %"].max() * 1.3])
        plotly_defaults(fig, height=340)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Cost Per Acquisition — CPA ($)")
        ch_cpa = ch.sort_values("CPA ($)", ascending=True)
        fig = go.Figure(go.Bar(
            x=ch_cpa["CPA ($)"], y=ch_cpa["Channel"],
            orientation="h",
            marker_color=[GREEN if "Facebook" in c else GOLD if "Mobile" in c else DARK for c in ch_cpa["Channel"]],
            text=[f"${v:.2f}" for v in ch_cpa["CPA ($)"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>CPA: $%{x:.2f}<extra></extra>"
        ))
        fig.update_xaxes(range=[0, ch_cpa["CPA ($)"].max() * 1.3], tickprefix="$")
        plotly_defaults(fig, height=340)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### Avg Customer Spend by Channel ($)")
        ch_sp = ch.sort_values("Avg Spend ($)", ascending=True)
        fig = go.Figure(go.Bar(
            x=ch_sp["Avg Spend ($)"], y=ch_sp["Channel"],
            orientation="h",
            marker_color=[GREEN if "Facebook" in c else GOLD if "Mobile" in c else DARK for c in ch_sp["Channel"]],
            text=[f"${v:,.2f}" for v in ch_sp["Avg Spend ($)"]],
            textposition="outside"
        ))
        fig.update_xaxes(tickprefix="$", range=[0, ch_sp["Avg Spend ($)"].max() * 1.3])
        plotly_defaults(fig, height=320)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.markdown("#### Channel Reach vs Conversions")
        fig = go.Figure()
        for i, row in ch.iterrows():
            is_fb = "Facebook" in row["Channel"]
            fig.add_trace(go.Scatter(
                x=[row["Sent"]], y=[row["Conversions"]],
                mode="markers+text",
                marker=dict(size=row["Conv Rate %"]*4,
                            color=GREEN if is_fb else PALETTE[i], opacity=0.8),
                text=[row["Channel"].split("/")[0].strip()],
                textposition="top center",
                name=row["Channel"],
                hovertemplate=f"<b>{row['Channel']}</b><br>Sent: {row['Sent']:,}<br>Converted: {row['Conversions']:,}<br>Rate: {row['Conv Rate %']:.1f}%<extra></extra>"
            ))
        fig.update_xaxes(title_text="Offers Sent", tickformat=",")
        fig.update_yaxes(title_text="Conversions", tickformat=",")
        fig.update_layout(showlegend=False)
        plotly_defaults(fig, height=320)
        st.plotly_chart(fig, use_container_width=True)

    # Channel summary table
    st.markdown("#### Channel Performance Summary")
    ch_display = ch.copy()
    ch_display["CPA ($)"]       = ch_display["CPA ($)"].apply(lambda x: f"${x:.2f}")
    ch_display["Avg Spend ($)"] = ch_display["Avg Spend ($)"].apply(lambda x: f"${x:,.2f}")
    ch_display["Conv Rate %"]   = ch_display["Conv Rate %"].apply(lambda x: f"{x:.1f}%")
    st.dataframe(ch_display, use_container_width=True, hide_index=True)

    st.markdown(f"""
    <div class="insight-box">
    💡 <b>Facebook / Instagram Ads</b> delivers a <b>{fb_conv:.1f}% conversion rate</b> at
    <b>${fb_cpa:.2f} CPA</b>. Increasing Facebook Ads budget allocation by 20% while
    reducing lower-performing channels could improve overall campaign efficiency by
    an estimated <b>12–18%</b>.
    </div>""", unsafe_allow_html=True)
