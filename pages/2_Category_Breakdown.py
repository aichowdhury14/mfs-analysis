import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.data_loader import CATEGORY_LABELS, category_with_shares, load_category_breakdown
from src.theme import CATEGORY_PALETTE, COLORS, apply_plotly_template, inject_css, page_header, sidebar_brand, style_fig

st.set_page_config(page_title="Category Breakdown", page_icon="🧭", layout="wide")
inject_css()
apply_plotly_template()
sidebar_brand()

page_header("Transaction Composition", "🧭 What people actually use MFS for", "Cash-in, cash-out and P2P still dominate, but the mix is shifting year over year.")

category = load_category_breakdown()
shares = category_with_shares()

tab1, tab2, tab3 = st.tabs(["Category mix", "Cash In vs Out", "Fastest growing"])

with tab1:
    plot_df = shares.melt(
        id_vars="year",
        value_vars=[f"{c}_share_pct" for c in CATEGORY_LABELS],
        var_name="category", value_name="share_pct",
    )
    plot_df["category"] = plot_df["category"].str.replace("_share_pct", "", regex=False).map(CATEGORY_LABELS)

    fig = px.bar(plot_df, x="year", y="share_pct", color="category", barmode="stack", color_discrete_sequence=CATEGORY_PALETTE)
    fig.update_layout(yaxis_title="% of total value", xaxis_title="", legend_title="")
    st.plotly_chart(style_fig(fig, height=480, hovermode="x"), use_container_width=True)

    st.caption(
        "Cash-in, cash-out and P2P together made up 87% of transaction value in 2023 and still dominate — "
        "people mostly use MFS as a cash-transfer rail, not yet for merchant payments at scale."
    )

    view = st.toggle("Show as table")
    if view:
        st.dataframe(category.rename(columns=CATEGORY_LABELS), use_container_width=True, hide_index=True)
        st.download_button("Download category data CSV", category.to_csv(index=False), "mfs_category_breakdown.csv", "text/csv")

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Cash-in vs cash-out over time")
        st.caption("2024 was the first year cash-out overtook cash-in nationally.")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=category["year"], y=category["cash_in"], mode="lines+markers", name="Cash In",
                                    line=dict(width=3, color=COLORS["accent"]), marker=dict(size=9)))
        fig2.add_trace(go.Scatter(x=category["year"], y=category["cash_out"], mode="lines+markers", name="Cash Out",
                                    line=dict(width=3, color=COLORS["amber"]), marker=dict(size=9)))
        fig2.update_layout(yaxis_title="Billion BDT", xaxis_title="")
        fig2.update_xaxes(tickmode="array", tickvals=category["year"], range=[category["year"].min() - 0.3, category["year"].max() + 0.3])
        st.plotly_chart(style_fig(fig2, height=400, hovermode="x unified"), use_container_width=True)

    with col2:
        year_pick = st.select_slider("Year", options=sorted(category["year"].unique()), value=int(category["year"].max()))
        st.markdown(f"##### Category mix, {year_pick}")
        latest = category[category["year"] == year_pick].iloc[0]
        pie_data = {CATEGORY_LABELS[c]: latest[c] for c in CATEGORY_LABELS}
        fig3 = px.pie(names=list(pie_data.keys()), values=list(pie_data.values()), hole=0.5,
                      color_discrete_sequence=CATEGORY_PALETTE)
        fig3.update_traces(textinfo="percent", textfont_size=11)
        st.plotly_chart(style_fig(fig3, height=400, hovermode="closest"), use_container_width=True)

with tab3:
    years_available = sorted(category["year"].unique())
    if len(years_available) >= 2:
        y1, y2 = st.select_slider(
            "Compare", options=years_available, value=(years_available[-2], years_available[-1]),
        )
        growth = (category.set_index("year")[list(CATEGORY_LABELS.keys())].loc[y2]
                  / category.set_index("year")[list(CATEGORY_LABELS.keys())].loc[y1] - 1) * 100
        growth_df = growth.sort_values(ascending=False).reset_index()
        growth_df.columns = ["category", "growth_pct"]
        growth_df["category"] = growth_df["category"].map(CATEGORY_LABELS)
        fig4 = go.Figure(go.Bar(
            x=growth_df["growth_pct"], y=growth_df["category"], orientation="h",
            marker_color=[COLORS["good"] if v >= 0 else COLORS["bad"] for v in growth_df["growth_pct"]],
            text=growth_df["growth_pct"].round(1), texttemplate="%{text}%", textposition="outside",
        ))
        fig4.update_layout(xaxis_title=f"Growth {y1} → {y2} (%)", yaxis_title="")
        pad = max(abs(growth_df["growth_pct"].min()), abs(growth_df["growth_pct"].max())) * 0.25
        fig4.update_xaxes(range=[growth_df["growth_pct"].min() - pad, growth_df["growth_pct"].max() + pad])
        st.plotly_chart(style_fig(fig4, height=420, hovermode="y"), use_container_width=True)
