import plotly.express as px
import streamlit as st

from src.data_loader import load_provider_shares

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
