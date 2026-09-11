"""
MFS Bangladesh — Home
Entry point for the Streamlit multi-page app.
"""
import streamlit as st

from src.data_loader import load_industry_stats, load_category_breakdown

st.set_page_config(
    page_title="MFS Bangladesh",
    page_icon="📱",
    layout="wide",
)

st.title("📱 Mobile Financial Services — Bangladesh")
st.caption(
    "Industry-wide bKash, Nagad, Rocket, Upay and every licensed MFS operator, combined. "
    "Built on Bangladesh Bank's official statistics."
)

industry = load_industry_stats()
category = load_category_breakdown()
last, prev = industry.iloc[-1], industry.iloc[-2]

col1, col2, col3, col4 = st.columns(4)
col1.metric(
    "Total transaction value",
    f"৳{last['total_transaction_volume_billion_bdt']/1000:.1f}T",
    f"{(last['total_transaction_volume_billion_bdt']/prev['total_transaction_volume_billion_bdt']-1)*100:.1f}% YoY",
)
col2.metric(
    "Active accounts",
    f"{last['active_accounts_millions']:.1f}M",
    f"{(last['active_accounts_millions']/prev['active_accounts_millions']-1)*100:.1f}% YoY",
)
col3.metric(
    "Registered clients",
    f"{last['registered_clients_millions']:.1f}M",
    f"{(last['registered_clients_millions']/prev['registered_clients_millions']-1)*100:.1f}% YoY",
)
col4.metric(
    "Total transactions",
    f"{last['total_transactions_millions']/1000:.2f}B",
    f"{(last['total_transactions_millions']/prev['total_transactions_millions']-1)*100:.1f}% YoY",
)

st.divider()

st.subheader("What's in this app")
st.markdown(
    """
- **📈 Trends & Forecast** — annual growth 2020-2024, plus a statistical forecast (Holt's exponential
  smoothing) for the next 3 years and a short-term monthly projection.
- **🧭 Category Breakdown** — what people actually use MFS for: cash-in/out, P2P, merchant payments,
  remittance, salary disbursement, government payment — and how that mix has shifted.
- **🔍 Anomaly & Pattern Detection** — years that grew notably faster or slower than trend, the 2024
  cash-in/cash-out crossover, and category correlation.
- **🏢 Provider Landscape** — estimated market share by operator (bKash, Nagad, Rocket...), clearly
  marked as an estimate since Bangladesh Bank doesn't publish a per-operator split.
- **📤 Compare Your Data** — upload your own business's MFS transaction log (CSV) and benchmark it
  against the national trend.

Use the sidebar to navigate between pages.
    """
)

st.divider()
st.caption(
    "Sources: Bangladesh Bank Financial Stability Reports (2022–2024), The Business Standard, "
    "Future Startup. Provider market-share figures are third-party estimates, not official BB data. "
    "See the **Sources & Methodology** page for full detail."
)
