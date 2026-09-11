import streamlit as st

st.set_page_config(page_title="Sources & Methodology", page_icon="📚", layout="wide")
st.title("📚 Sources & Methodology")

st.subheader("Data sources")
st.markdown(
    """
| Dataset | Source | Coverage | Reliability |
|---|---|---|---|
| Annual industry stats (agents, accounts, transactions) | Bangladesh Bank Financial Stability Reports 2022, 2023, 2024 (official PDFs, Appendix tables) | 2020–2024, annual | Official |
| Annual category breakdown (cash-in, P2P, merchant, etc.) | Same reports, Table 7.2 each year | 2021–2024, annual | Official |
| Monthly transaction totals | The Business Standard, Future Startup — both cite Bangladesh Bank's monthly releases | Jun 2024 – Jan 2025, partial | Secondary (press-reported) |
| Provider market share (bKash, Nagad, Rocket...) | The Financial Express, Future Startup | Dec 2022, Jan 2025 snapshots | **Estimate** — not published by Bangladesh Bank |
    """
)

st.divider()

st.subheader("Why not Bangladesh Bank's live monthly data page directly?")
st.markdown(
    """
Bangladesh Bank publishes a month-by-month comparative statement at
[bb.org.bd/en/index.php/financialactivity/mfsdata](https://www.bb.org.bd/en/index.php/financialactivity/mfsdata),
which would be the richest possible source — full category breakdown, agent counts, and
month-over-month % change, for any month back to 2022.

In practice the page sits behind bot-protection (a JavaScript challenge) that blocks
automated, repeated requests after the first one or two. Rather than repeatedly hammer
their infrastructure to work around it, this project instead cross-references Bangladesh
Bank's own **annual** publications (the Financial Stability Report PDFs, which the same
protection did allow after a normal browser load) plus **press coverage** that already
cites BB's monthly figures. If you'd like to extend the monthly series yourself, you can
manually pull additional months from that page and add rows to
`data/mfs_monthly_totals.csv`.
    """
)

st.divider()

st.subheader("Modeling notes")
st.markdown(
    """
- **Forecasting** (`src/forecasting.py`): annual volume uses Holt's damped exponential
  smoothing — appropriate for a short trended series with no seasonality to model at
  yearly granularity. Monthly volume uses OLS on a log scale, which captures compounding
  growth better than a raw linear fit. Both confidence bands widen with the forecast
  horizon, and both are intentionally simple: with 4–7 data points, a more complex model
  (full ARIMA, ML regressors) would fit noise, not signal.
- **Anomaly detection** (`src/anomaly.py`): flags years whose growth is more than 1
  standard deviation from the mean growth rate. That threshold is loose on purpose — with
  5 data points this is a pointer for a human to look closer, not a statistically
  rigorous outlier test.
- **Correlation & growth-curve fitting** (`src/correlation.py`): category correlation is
  computed on only 4 annual points, so treat it as describing "did these categories grow
  together during this specific growth era," not a robust long-run relationship.
    """
)

st.divider()
st.caption("Compiled September 2026. Figures will drift out of date — check Bangladesh Bank's page linked above for the latest official release.")
