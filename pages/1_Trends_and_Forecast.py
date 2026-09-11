import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.data_loader import industry_with_growth, load_monthly_totals
from src.forecasting import forecast_annual_volume, forecast_monthly_volume, monthly_growth_rate

st.set_page_config(page_title="Trends & Forecast", page_icon="📈", layout="wide")
st.title("📈 Trends & Forecast")

industry = industry_with_growth()
monthly = load_monthly_totals()

metric_options = {
    "Active accounts (millions)": "active_accounts_millions",
    "Registered clients (millions)": "registered_clients_millions",
    "Agents (millions)": "agents_millions",
    "Transaction volume (billion BDT)": "total_transaction_volume_billion_bdt",
    "Total transactions (millions)": "total_transactions_millions",
}
choice = st.selectbox("Metric", list(metric_options.keys()), index=3)
col = metric_options[choice]

st.subheader(f"{choice}, 2020–2024")
fig = go.Figure()
fig.add_trace(go.Scatter(x=industry["year"], y=industry[col], mode="lines+markers", name=choice, line=dict(width=3)))
fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10), yaxis_title=choice, xaxis_title="Year")
st.plotly_chart(fig, use_container_width=True)

with st.expander("Year-over-year growth"):
    growth_col = f"{col}_yoy_pct"
    st.dataframe(
        industry[["year", col, growth_col]].rename(columns={growth_col: "YoY %"}),
        use_container_width=True,
        hide_index=True,
    )

st.divider()

st.subheader("Forecast: transaction volume, next 3 years")
st.caption(
    "Holt's damped exponential smoothing fit on 5 annual data points. With this little history the "
    "80% confidence band is wide by construction — read this as a trend projection, not a precise prediction."
)
forecast = forecast_annual_volume(industry)
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=industry["year"], y=industry["total_transaction_volume_billion_bdt"], mode="lines+markers", name="Actual", line=dict(width=3)))
fig2.add_trace(go.Scatter(x=forecast["year"], y=forecast["forecast_billion_bdt"], mode="lines+markers", name="Forecast", line=dict(width=3, dash="dash")))
fig2.add_trace(go.Scatter(
    x=pd.concat([forecast["year"], forecast["year"][::-1]]),
    y=pd.concat([forecast["ci_upper"], forecast["ci_lower"][::-1]]),
    fill="toself", fillcolor="rgba(31,174,132,0.15)", line=dict(width=0), name="80% CI", showlegend=True,
))
fig2.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="Billion BDT", xaxis_title="Year")
st.plotly_chart(fig2, use_container_width=True)
st.dataframe(forecast.round(1), use_container_width=True, hide_index=True)

st.divider()

st.subheader("Monthly view (2024–25, press-reported)")
st.caption(
    "Sparser and less official than the annual series — filled in as more months are confirmed from "
    "Bangladesh Bank releases. Growth fit on a log scale to capture the compounding pattern."
)
avg_growth = monthly_growth_rate(monthly)
st.metric("Average month-over-month growth", f"{avg_growth:.1f}%")

monthly_forecast = forecast_monthly_volume(monthly, periods=6)
fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=monthly["date"], y=monthly["total_transaction_value_crore_bdt"], mode="lines+markers", name="Actual", line=dict(width=3)))
fig3.add_trace(go.Scatter(x=monthly_forecast["date"], y=monthly_forecast["forecast_crore_bdt"], mode="lines+markers", name="Forecast", line=dict(width=3, dash="dash")))
fig3.add_trace(go.Scatter(
    x=pd.concat([monthly_forecast["date"], monthly_forecast["date"][::-1]]),
    y=pd.concat([monthly_forecast["ci_upper"], monthly_forecast["ci_lower"][::-1]]),
    fill="toself", fillcolor="rgba(224,145,61,0.15)", line=dict(width=0), name="80% CI",
))
fig3.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="Crore BDT", xaxis_title="Month")
st.plotly_chart(fig3, use_container_width=True)
