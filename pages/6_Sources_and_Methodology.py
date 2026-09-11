import streamlit as st

from src.theme import apply_plotly_template, inject_css, page_header, sidebar_brand

st.set_page_config(page_title="Sources & Methodology", page_icon="📚", layout="wide")
inject_css()
apply_plotly_template()
sidebar_brand()

page_header("Provenance", "📚 Sources & Methodology", "Every figure in this app, where it came from, and what's still open.")

tab1, tab2, tab3 = st.tabs(["Data sources", "Known gaps", "Modeling notes"])

with tab1:
    st.markdown(
        """
| Dataset | Source | Coverage | Reliability |
|---|---|---|---|
| Annual industry stats (agents, accounts, transactions) | Bangladesh Bank Financial Stability Reports 2022, 2023, 2024 (official PDFs, Appendix tables) | 2020–2024, annual | 🟢 Official |
| Annual category breakdown (cash-in, P2P, merchant, etc.) | Same reports, Table 7.2 each year | 2021–2024, annual | 🟢 Official |
| Monthly transaction totals | The Business Standard, The Financial Express, Future Startup — all cite Bangladesh Bank's monthly releases | Jun 2024 – Aug 2025, partial | 🟡 Secondary (press-reported) |
| MFS remittance totals | The Daily Star (8 Mar 2026), citing BB data | 2019, 2024, 2025 | 🟡 Secondary (press-reported) |
| Provider market share (bKash, Nagad, Rocket...) | The Financial Express, Future Startup | Dec 2022, Jan 2025 snapshots | 🟠 Estimate — not published by Bangladesh Bank |
        """
    )
    st.caption("🟢 Official Bangladesh Bank publication · 🟡 Press coverage citing BB data · 🟠 Third-party estimate")

with tab2:
    st.markdown("##### No confirmed 2025 annual total")
    st.markdown(
        """
The annual industry-stats series (Trends & Forecast page) stops at 2024 on purpose. A Daily Star
article (8 March 2026) reported 2025's total MFS transaction value at **Tk 18.73 lakh crore** —
but that implies only **7.3% YoY growth**, sharply down from the 29–37% growth seen in every prior
year, and inconsistent with the strong monthly 2025 figures this project *did* confirm (January
alone was already +32% YoY; March hit an all-time high ahead of Eid).

Rather than add a number that contradicts the corroborating evidence, this project leaves 2025 out
of the annual series until a consistent figure turns up — most likely once Bangladesh Bank's 2025
Financial Stability Report is published. The confirmed monthly 2025 data points (January, March,
August) are included in the monthly series instead, each with its own source.
        """
    )
    st.warning("This is a genuine open discrepancy, not resolved — see the app's commit history for the research trail.")

    st.markdown("##### Why not Bangladesh Bank's live monthly data page directly?")
    st.markdown(
        """
Bangladesh Bank publishes a month-by-month comparative statement at
[bb.org.bd/en/index.php/financialactivity/mfsdata](https://www.bb.org.bd/en/index.php/financialactivity/mfsdata),
which would be the richest possible source — full category breakdown, agent counts, and
month-over-month % change, for any month back to 2022.

In practice the page sits behind bot-protection (a JavaScript challenge) that blocks automated,
repeated requests after the first one or two. Rather than repeatedly hammer their infrastructure to
work around it, this project instead cross-references Bangladesh Bank's own **annual** publications
plus **press coverage** that already cites BB's monthly figures. To extend the monthly series
yourself, manually pull additional months from that page and add rows to
`data/mfs_monthly_totals.csv`.
        """
    )

with tab3:
    st.markdown(
        """
- **Forecasting** (`src/forecasting.py`): annual volume uses Holt's damped exponential smoothing —
  appropriate for a short trended series with no seasonality to model at yearly granularity. Monthly
  volume uses OLS on a log scale against *actual elapsed time* (not row position, since some months
  are missing from press coverage), which captures compounding growth better than a raw linear fit.
  Both confidence bands widen with the forecast horizon, and both are intentionally simple: with
  4–9 data points, a more complex model (full ARIMA, ML regressors) would fit noise, not signal.
- **Anomaly detection** (`src/anomaly.py`): flags years whose growth is more than 1 standard
  deviation from the mean growth rate by default (adjustable in the Anomaly & Patterns page). That
  threshold is loose on purpose — with 5 data points this is a pointer for a human to look closer,
  not a statistically rigorous outlier test.
- **Correlation & growth-curve fitting** (`src/correlation.py`): category correlation is computed
  on only 4 annual points, so treat it as describing "did these categories grow together during
  this specific growth era," not a robust long-run relationship.
        """
    )

st.divider()
st.caption("Compiled September 2026, updated with 2025 monthly and remittance data. Figures will drift out of date — check Bangladesh Bank's page for the latest official release.")
