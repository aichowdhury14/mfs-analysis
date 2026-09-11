"""
MFS Bangladesh — Home
Entry point for the Streamlit multi-page app.
"""
import plotly.graph_objects as go
import streamlit as st

from src.data_loader import industry_with_growth, load_category_breakdown
from src.theme import COLORS, apply_plotly_template, inject_css, page_header, sidebar_brand, style_fig

st.set_page_config(page_title="MFS Bangladesh", page_icon="📱", layout="wide")
inject_css()
apply_plotly_template()
sidebar_brand()

industry = industry_with_growth()
category = load_category_breakdown()
last, prev = industry.iloc[-1], industry.iloc[-2]

page_header(
    "Bangladesh · Payment Systems",
    "Mobile Financial Services, tracked",
    "Industry-wide bKash, Nagad, Rocket, Upay and every licensed MFS operator, combined — "
    "built on Bangladesh Bank's official statistics, 2020–2025.",
)

col1, col2, col3, col4 = st.columns(4)
col1.metric(
    "Total transaction value",
    f"৳{last['total_transaction_volume_billion_bdt']/1000:.1f}T",
    f"{last['total_transaction_volume_billion_bdt_yoy_pct']:.1f}% YoY",
)
col2.metric(
    "Active accounts",
    f"{last['active_accounts_millions']:.1f}M",
    f"{last['active_accounts_millions_yoy_pct']:.1f}% YoY",
)
col3.metric(
    "Registered clients",
    f"{last['registered_clients_millions']:.1f}M",
    f"{last['registered_clients_millions_yoy_pct']:.1f}% YoY",
)
col4.metric(
    "Total transactions",
    f"{last['total_transactions_millions']/1000:.2f}B",
    f"{last['total_transactions_millions_yoy_pct']:.1f}% YoY",
)

st.write("")

left, right = st.columns([1.4, 1])

with left:
    st.markdown("##### Growth since 2020")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=industry["year"], y=industry["total_transaction_volume_billion_bdt"],
        mode="lines+markers", name="Transaction value", fill="tozeroy",
        fillcolor="rgba(12,138,104,0.08)", line=dict(width=3, color=COLORS["accent"]),
        marker=dict(size=8),
    ))
    fig.update_layout(yaxis_title="Billion BDT", xaxis_title="")
    fig.update_xaxes(tickmode="array", tickvals=industry["year"], range=[industry["year"].min() - 0.3, industry["year"].max() + 0.3])
    st.plotly_chart(style_fig(fig, height=320, hovermode="x"), use_container_width=True)

with right:
    st.markdown("##### 2024 category mix")
    latest_cat = category[category["year"] == category["year"].max()].iloc[0]
    labels = ["Cash In", "Cash Out", "P2P", "Merchant", "Salary", "Utility", "Govt.", "Remit.", "Others"]
    values = [latest_cat[c] for c in ["cash_in", "cash_out", "p2p", "merchant_payment", "salary_disbursement_b2p",
                                       "utility_bill_p2b", "government_payment", "inward_remittance", "others"]]
    fig2 = go.Figure(go.Pie(labels=labels, values=values, hole=0.55, textinfo="label+percent",
                              textfont_size=11, showlegend=False))
    st.plotly_chart(style_fig(fig2, height=320, hovermode="closest"), use_container_width=True)

st.write("")
st.divider()

st.markdown("### What's in this app")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("**📈 Trends & Forecast**")
    st.caption("Annual growth 2020–2025, plus a statistical forecast (Holt's exponential smoothing) for the next 3 years and a short-term monthly projection.")
    st.markdown("**🧭 Category Breakdown**")
    st.caption("What people actually use MFS for — cash-in/out, P2P, merchant payments, remittance, salary, government payment — and how the mix has shifted.")
with c2:
    st.markdown("**🔍 Anomaly & Patterns**")
    st.caption("Years that grew notably faster or slower than trend, the 2024 cash-in/cash-out crossover, and category correlation.")
    st.markdown("**🏢 Provider Landscape**")
    st.caption("Estimated market share by operator (bKash, Nagad, Rocket...) and MFS's growing role in remittances — clearly marked where figures are estimates.")
with c3:
    st.markdown("**📤 Compare Your Data**")
    st.caption("Upload your own business's MFS transaction log (CSV) and benchmark it against the national trend, entirely in your browser session.")
    st.markdown("**📚 Sources & Methodology**")
    st.caption("Full provenance for every figure, and an honest account of what couldn't be confirmed.")

st.divider()
st.caption(
    "Sources: Bangladesh Bank Financial Stability Reports (2022–2024), The Business Standard, The Financial "
    "Express, The Daily Star, Future Startup. Provider market-share figures are third-party estimates, not "
    "official BB data. See **Sources & Methodology** for full detail."
)
