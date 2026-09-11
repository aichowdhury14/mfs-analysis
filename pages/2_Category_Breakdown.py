import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.data_loader import CATEGORY_LABELS, category_with_shares, load_category_breakdown

st.set_page_config(page_title="Category Breakdown", page_icon="🧭", layout="wide")
st.title("🧭 What people actually use MFS for")

category = load_category_breakdown()
shares = category_with_shares()

st.subheader("Category share of total transaction value")
plot_df = shares.melt(
    id_vars="year",
    value_vars=[f"{c}_share_pct" for c in CATEGORY_LABELS],
    var_name="category",
    value_name="share_pct",
)
plot_df["category"] = plot_df["category"].str.replace("_share_pct", "", regex=False).map(CATEGORY_LABELS)

fig = px.bar(plot_df, x="year", y="share_pct", color="category", barmode="stack")
fig.update_layout(height=480, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="% of total value", xaxis_title="Year", legend_title="")
st.plotly_chart(fig, use_container_width=True)

st.caption(
    "Cash-in, cash-out and P2P together made up 87% of transaction value in 2023 and still dominate — "
    "people mostly use MFS as a cash-transfer rail, not yet for merchant payments at scale."
)

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Cash-in vs cash-out")
    st.caption("2024 was the first year cash-out overtook cash-in nationally.")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=category["year"], y=category["cash_in"], mode="lines+markers", name="Cash In", line=dict(width=3)))
    fig2.add_trace(go.Scatter(x=category["year"], y=category["cash_out"], mode="lines+markers", name="Cash Out", line=dict(width=3)))
    fig2.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="Billion BDT")
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader(f"Category mix, {int(category['year'].max())}")
    latest = category[category["year"] == category["year"].max()].iloc[0]
    pie_data = {CATEGORY_LABELS[c]: latest[c] for c in CATEGORY_LABELS}
    fig3 = px.pie(names=list(pie_data.keys()), values=list(pie_data.values()), hole=0.45)
    fig3.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig3, use_container_width=True)

st.divider()
st.subheader("Fastest-growing categories, 2023 → 2024")
growth = category.set_index("year")[list(CATEGORY_LABELS.keys())].pct_change().loc[2024].sort_values(ascending=False) * 100
growth_df = growth.reset_index()
growth_df.columns = ["category", "growth_pct"]
growth_df["category"] = growth_df["category"].map(CATEGORY_LABELS)
fig4 = px.bar(growth_df, x="growth_pct", y="category", orientation="h")
fig4.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10), xaxis_title="YoY growth %", yaxis_title="")
st.plotly_chart(fig4, use_container_width=True)

with st.expander("Full data table (billion BDT)"):
    st.dataframe(category.rename(columns=CATEGORY_LABELS), use_container_width=True, hide_index=True)
