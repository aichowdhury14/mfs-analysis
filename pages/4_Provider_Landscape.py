import plotly.express as px
import streamlit as st

from src.data_loader import load_provider_shares, load_remittance_annual
from src.theme import CATEGORY_PALETTE, COLORS, apply_plotly_template, inject_css, page_header, sidebar_brand, style_fig

st.set_page_config(page_title="Provider Landscape", page_icon="🏢", layout="wide")
inject_css()
apply_plotly_template()
sidebar_brand()

page_header(
    "By Operator", "🏢 Provider Landscape",
    "bKash, Nagad, Rocket and the rest — how the market splits, where Bangladesh Bank doesn't publish the breakdown itself.",
)
st.markdown('<span class="badge badge-estimate">⚠ Estimate, not official data</span>', unsafe_allow_html=True)
st.caption(
    "Bangladesh Bank does not publish a per-operator transaction breakdown — the figures below are "
    "compiled from trade-press reporting (The Financial Express, Future Startup) and should be read as "
    "directional, not precise."
)
st.write("")

shares = load_provider_shares()
periods = sorted(shares["period"].unique())
period = st.select_slider("Snapshot", options=periods, value=periods[-1])

snap = shares[shares["period"] == period].sort_values("market_share_percent", ascending=False)

col1, col2 = st.columns([1, 1])
with col1:
    fig = px.bar(snap, x="market_share_percent", y="provider", orientation="h", text="market_share_percent",
                 color="provider", color_discrete_sequence=CATEGORY_PALETTE)
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(xaxis_title="Market share %", yaxis_title="", showlegend=False)
    fig.update_xaxes(range=[0, snap["market_share_percent"].max() * 1.18])
    st.plotly_chart(style_fig(fig, height=380, hovermode="y"), use_container_width=True)

with col2:
    fig2 = px.pie(snap, names="provider", values="market_share_percent", hole=0.5,
                  color_discrete_sequence=CATEGORY_PALETTE)
    fig2.update_traces(textinfo="percent+label", textfont_size=12)
    st.plotly_chart(style_fig(fig2, height=380, hovermode="closest"), use_container_width=True)

st.divider()
st.markdown("##### Shift between snapshots")
if len(periods) >= 2:
    pivot = shares.pivot_table(index="provider", columns="period", values="market_share_percent")
    st.dataframe(pivot.round(1), use_container_width=True)
    st.caption("Nagad's share grew fastest of the tracked operators between the two snapshots; bKash has held its lead.")

with st.expander("Sources for these figures"):
    st.dataframe(shares, use_container_width=True, hide_index=True)

st.divider()

st.markdown("##### bKash's remittance lead, 2025")
st.caption(
    "Bangladesh Bank data (via The Daily Star, 8 March 2026) shows MFS-channelled remittances "
    "excluding Nagad — bKash's own reporting puts it at the top of that channel."
)
remit = load_remittance_annual()
fig3 = px.bar(remit, x="year", y="remittance_via_mfs_crore_bdt", text="remittance_via_mfs_crore_bdt",
              color_discrete_sequence=[COLORS["accent"]])
fig3.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
fig3.update_layout(yaxis_title="Crore BDT", xaxis_title="")
st.plotly_chart(style_fig(fig3, height=360, hovermode="x"), use_container_width=True)

col1, col2 = st.columns(2)
col1.metric("2025 MFS remittance (ex-Nagad)", "৳20,236 crore", "+87.6% YoY")
col2.metric("bKash's share of that", "≈ ৳20,000 crore", "nearly all of it")

st.info(
    "**Note on Nagad:** Bangladesh Bank placed Nagad under administrator management in August 2024 "
    "over governance concerns, which is part of why BB's remittance figures above exclude it — not a "
    "reflection of Nagad's underlying transaction volume, which is still substantial in P2P and "
    "cash-in/out."
)
