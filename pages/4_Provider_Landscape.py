import plotly.express as px
import streamlit as st

from src.data_loader import load_provider_shares, load_remittance_annual

st.set_page_config(page_title="Provider Landscape", page_icon="🏢", layout="wide")
st.title("🏢 Provider Landscape")
st.warning(
    "⚠️ **Estimate, not official data.** Bangladesh Bank does not publish a per-operator transaction "
    "breakdown — the figures below are compiled from trade-press reporting (The Financial Express, "
    "Future Startup) and should be read as directional, not precise."
)

shares = load_provider_shares()
periods = sorted(shares["period"].unique())
period = st.selectbox("Snapshot", periods, index=len(periods) - 1)

snap = shares[shares["period"] == period].sort_values("market_share_percent", ascending=False)

col1, col2 = st.columns([1, 1])
with col1:
    fig = px.bar(snap, x="market_share_percent", y="provider", orientation="h", text="market_share_percent")
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10), xaxis_title="Market share %", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig2 = px.pie(snap, names="provider", values="market_share_percent", hole=0.45)
    fig2.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig2, use_container_width=True)

st.divider()
st.subheader("Shift between snapshots")
if len(periods) >= 2:
    pivot = shares.pivot_table(index="provider", columns="period", values="market_share_percent")
    st.dataframe(pivot.round(1), use_container_width=True)
    st.caption("Nagad's share nearly grew fastest of the tracked operators between the two snapshots; bKash has held its lead.")

with st.expander("Sources for these figures"):
    st.dataframe(shares, use_container_width=True, hide_index=True)

st.divider()

st.subheader("bKash's remittance lead, 2025")
st.caption(
    "Bangladesh Bank data (via The Daily Star, 8 March 2026) shows MFS-channelled remittances "
    "excluding Nagad — bKash's own reporting puts it at the top of that channel."
)
remit = load_remittance_annual()
fig3 = px.bar(remit, x="year", y="remittance_via_mfs_crore_bdt", text="remittance_via_mfs_crore_bdt")
fig3.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
fig3.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="Crore BDT", xaxis_title="Year")
st.plotly_chart(fig3, use_container_width=True)

col1, col2 = st.columns(2)
col1.metric("2025 MFS remittance (ex-Nagad)", "৳20,236 crore", "+87.6% YoY")
col2.metric("bKash's share of that", "≈ ৳20,000 crore", "nearly all of it")

st.info(
    "**Note on Nagad:** Bangladesh Bank placed Nagad under administrator management in August 2024 "
    "over governance concerns, which is part of why BB's remittance figures above exclude it — not a "
    "reflection of Nagad's underlying transaction volume, which is still substantial in P2P and "
    "cash-in/out."
)
