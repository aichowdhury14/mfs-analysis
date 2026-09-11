import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.anomaly import cash_flow_direction, flag_growth_anomalies
from src.correlation import category_correlation, fit_growth_curve
from src.data_loader import CATEGORY_LABELS, load_category_breakdown, load_industry_stats
from src.theme import COLORS, apply_plotly_template, inject_css, page_header, sidebar_brand, style_fig

st.set_page_config(page_title="Anomaly & Patterns", page_icon="🔍", layout="wide")
inject_css()
apply_plotly_template()
sidebar_brand()

page_header("Statistical Read", "🔍 Anomaly & Pattern Detection", "Where the numbers deviate from trend, and what shape the industry's growth actually takes.")

industry = load_industry_stats()
category = load_category_breakdown()

tab1, tab2, tab3, tab4 = st.tabs(["Growth outliers", "Cash-flow crossover", "Category correlation", "Growth shape"])

with tab1:
    z_thresh = st.slider("Sensitivity (z-score threshold)", 0.5, 2.0, 1.0, 0.1,
                          help="Lower = flags more years as notable. With only 5 data points this is a pointer for a human to look closer, not a rigorous outlier test.")
    anomalies = flag_growth_anomalies(industry, "total_transaction_volume_billion_bdt", "year", z_thresh=z_thresh)

    fig = go.Figure()
    colors = [COLORS["bad"] if flag else COLORS["accent"] for flag in anomalies["is_notable"]]
    fig.add_trace(go.Bar(x=anomalies["year"], y=anomalies["growth_pct"], marker_color=colors,
                          text=anomalies["growth_pct"].round(1), texttemplate="%{text}%", textposition="outside"))
    fig.update_layout(yaxis_title="YoY growth %", xaxis_title="")
    st.plotly_chart(style_fig(fig, height=400, hovermode="x"), use_container_width=True)

    st.dataframe(anomalies.round(2), use_container_width=True, hide_index=True)
    st.caption("2021 grew unusually fast off a small pandemic-era base; 2024 growth, while still strong, was the slowest of the four years on record.")

with tab2:
    cash_flow = cash_flow_direction(category)
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=cash_flow["year"], y=cash_flow["cash_gap_billion_bdt"],
        marker_color=[COLORS["good"] if v >= 0 else COLORS["bad"] for v in cash_flow["cash_gap_billion_bdt"]],
        text=cash_flow["cash_gap_billion_bdt"].round(0), textposition="outside",
    ))
    fig2.add_hline(y=0, line_color=COLORS["line"], line_width=1.5)
    fig2.update_layout(yaxis_title="Cash In − Cash Out (billion BDT)", xaxis_title="")
    st.plotly_chart(style_fig(fig2, height=380, hovermode="x"), use_container_width=True)

    if cash_flow["cash_gap_billion_bdt"].iloc[-1] < 0:
        st.error("🔻 **2024 flipped negative** — more money is now leaving MFS wallets as cash-out than entering as cash-in.")
    st.caption(
        "Positive = more money entering MFS wallets (agent cash-in) than leaving (cash-out). "
        "The 2024 flip is consistent with MFS maturing from a remittance/cash-in channel toward a "
        "spending and withdrawal tool."
    )

with tab3:
    st.caption(
        "Correlation of category *levels* across the 4 years of annual data available. Nearly everything "
        "correlates strongly because the whole industry grew together — the useful read is which pair is "
        "relatively *less* correlated with the rest."
    )
    corr = category_correlation(category)
    corr.index = corr.index.map(CATEGORY_LABELS)
    corr.columns = corr.columns.map(CATEGORY_LABELS)
    fig3 = px.imshow(corr, color_continuous_scale=[[0, COLORS["bad"]], [0.5, "#F7F5EF"], [1, COLORS["good"]]],
                      zmin=-1, zmax=1, text_auto=".2f")
    fig3.update_layout(height=520)
    st.plotly_chart(fig3, use_container_width=True)

with tab4:
    metric_options = {
        "Transaction volume": "total_transaction_volume_billion_bdt",
        "Active accounts": "active_accounts_millions",
        "Registered clients": "registered_clients_millions",
    }
    choice = st.selectbox("Metric", list(metric_options.keys()))
    fit = fit_growth_curve(industry, metric_options[choice])
    col1, col2, col3 = st.columns(3)
    col1.metric("Linear fit R²", f"{fit['linear_r2']:.4f}")
    col2.metric("Exponential fit R²", f"{fit['exponential_r2']:.4f}")
    col3.metric("Implied annual growth", f"{fit['implied_annual_growth_pct']:.1f}%")
    st.info(f"**{fit['better_fit'].title()}** growth fits the data better — consistent with compounding adoption rather than a fixed number of new users added per year.")
