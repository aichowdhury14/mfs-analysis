import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.anomaly import cash_flow_direction, flag_growth_anomalies
from src.correlation import category_correlation, fit_growth_curve
from src.data_loader import CATEGORY_LABELS, load_category_breakdown, load_industry_stats

st.set_page_config(page_title="Anomaly & Patterns", page_icon="🔍", layout="wide")
st.title("🔍 Anomaly & Pattern Detection")

industry = load_industry_stats()
category = load_category_breakdown()

st.subheader("Notable growth years")
st.caption(
    "Years whose YoY growth sits more than 1 standard deviation from the industry's average growth rate. "
    "With only 5 data points this flags *notable* deviations for a human to interpret, not statistically "
    "rigorous outliers — treat it as a pointer, not a verdict."
)
anomalies = flag_growth_anomalies(industry, "total_transaction_volume_billion_bdt", "year")
fig = go.Figure()
colors = ["#B23A2A" if flag else "#0C8A68" for flag in anomalies["is_notable"]]
fig.add_trace(go.Bar(x=anomalies["year"], y=anomalies["growth_pct"], marker_color=colors))
fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="YoY growth %", xaxis_title="Year")
st.plotly_chart(fig, use_container_width=True)
st.dataframe(anomalies.round(2), use_container_width=True, hide_index=True)
st.caption("2021 grew unusually fast off a small pandemic-era base; 2024 growth, while still strong, was the slowest of the four years on record.")

st.divider()

st.subheader("The 2024 cash-flow crossover")
cash_flow = cash_flow_direction(category)
fig2 = go.Figure()
fig2.add_trace(go.Bar(x=cash_flow["year"], y=cash_flow["cash_gap_billion_bdt"],
                       marker_color=["#0C8A68" if v >= 0 else "#B23A2A" for v in cash_flow["cash_gap_billion_bdt"]]))
fig2.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="Cash In − Cash Out (billion BDT)", xaxis_title="Year")
st.plotly_chart(fig2, use_container_width=True)
st.caption(
    "Positive = more money entering MFS wallets (agent cash-in) than leaving (cash-out). "
    "2024 flipped negative for the first time — consistent with MFS maturing from a remittance/cash-in "
    "channel toward a spending and withdrawal tool."
)

st.divider()

st.subheader("Category correlation")
st.caption(
    "Correlation of category *levels* across the 4 years of annual data available. Nearly everything "
    "correlates strongly because the whole industry grew together — the useful read is which pair is "
    "relatively *less* correlated with the rest."
)
corr = category_correlation(category)
corr.index = corr.index.map(CATEGORY_LABELS)
corr.columns = corr.columns.map(CATEGORY_LABELS)
fig3 = px.imshow(corr, color_continuous_scale="RdYlGn", zmin=-1, zmax=1, text_auto=".2f")
fig3.update_layout(height=520, margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig3, use_container_width=True)

st.divider()

st.subheader("Which growth shape fits best?")
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
