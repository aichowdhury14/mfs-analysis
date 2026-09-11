import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.data_loader import load_monthly_totals
from src.theme import COLORS, apply_plotly_template, inject_css, page_header, sidebar_brand, style_fig

st.set_page_config(page_title="Compare Your Data", page_icon="📤", layout="wide")
inject_css()
apply_plotly_template()
sidebar_brand()

page_header(
    "Your Data, Benchmarked", "📤 Compare Your Own MFS Data",
    "Have a business's MFS transaction log? Upload it to benchmark against the national monthly trend. "
    "Processing happens in this session only — nothing is written to disk or shared.",
)

UNIT_TO_CRORE = {"Crore BDT": 1, "Lakh BDT": 1 / 100, "Taka (BDT)": 1 / 10_000_000}

col_a, col_b = st.columns([2, 1])
with col_a:
    uploaded = st.file_uploader("Upload CSV (columns: `month` as YYYY-MM, `value`)", type="csv")
with col_b:
    unit = st.selectbox("Your value column is in", list(UNIT_TO_CRORE.keys()))

st.download_button(
    "⬇ Download a sample template",
    data="month,value\n2024-06,850\n2024-08,910\n2024-09,940\n2025-01,1050\n2025-03,1180\n",
    file_name="mfs_sample_template.csv",
    mime="text/csv",
)

if uploaded is not None:
    try:
        user_df = pd.read_csv(uploaded)
        user_df.columns = [c.strip().lower() for c in user_df.columns]
        if "month" not in user_df.columns or "value" not in user_df.columns:
            st.error("CSV must have a `month` column (YYYY-MM) and a `value` column.")
        else:
            user_df["date"] = pd.to_datetime(user_df["month"], format="%Y-%m", errors="coerce")
            user_df = user_df.dropna(subset=["date"])
            user_df["value_crore"] = pd.to_numeric(user_df["value"], errors="coerce") * UNIT_TO_CRORE[unit]
            user_df = user_df.dropna(subset=["value_crore"]).sort_values("date")

            if user_df.empty:
                st.error("No valid rows found after parsing. Check the date format (YYYY-MM) and that values are numeric.")
            else:
                st.success(f"✅ Loaded {len(user_df)} rows, {user_df['date'].min():%b %Y} – {user_df['date'].max():%b %Y}.")

                national = load_monthly_totals()

                merged = pd.merge(
                    user_df[["date", "value_crore"]], national[["date", "total_transaction_value_crore_bdt"]],
                    on="date", how="inner",
                )
                m1, m2, m3 = st.columns(3)
                m1.metric("Your total (matched months)", f"৳{user_df['value_crore'].sum():,.0f} cr")
                if len(user_df) >= 2:
                    growth = (user_df["value_crore"].iloc[-1] / user_df["value_crore"].iloc[0] - 1) * 100
                    m2.metric("Change, first → last month", f"{growth:+.1f}%")
                if len(merged) >= 3:
                    corr = np.corrcoef(merged["value_crore"], merged["total_transaction_value_crore_bdt"])[0, 1]
                    m3.metric("Correlation with national trend", f"{corr:.2f}")
                else:
                    m3.metric("Correlation with national trend", "need ≥3 overlapping months")

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=national["date"], y=national["total_transaction_value_crore_bdt"] / 100000,
                    mode="lines+markers", name="National (lakh crore BDT)",
                    line=dict(width=3, color=COLORS["accent"]), marker=dict(size=8),
                    yaxis="y1",
                ))
                fig.add_trace(go.Scatter(
                    x=user_df["date"], y=user_df["value_crore"],
                    mode="lines+markers", name="Your data (crore BDT)",
                    line=dict(width=3, dash="dot", color=COLORS["rose"]), marker=dict(size=8),
                    yaxis="y2",
                ))
                fig.update_layout(
                    height=460,
                    yaxis=dict(title="National — lakh crore BDT"),
                    yaxis2=dict(title="Your data — crore BDT", overlaying="y", side="right", showgrid=False),
                    hovermode="x unified",
                )
                st.plotly_chart(fig, use_container_width=True)
                st.caption(
                    "Two independent scales shown together (national in lakh crore, yours in crore) so shape "
                    "and timing are comparable even though the absolute sizes differ enormously — this is not "
                    "a claim that your series shares units with the national one."
                )

                tab1, tab2 = st.tabs(["Your parsed data", "Raw upload preview"])
                with tab1:
                    st.dataframe(user_df[["month", "value", "value_crore"]], use_container_width=True, hide_index=True)
                with tab2:
                    st.dataframe(pd.read_csv(uploaded), use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Couldn't parse that file: {e}")
else:
    st.info("👆 Upload a CSV to see your data plotted against the national trend, or try the sample template above.")
