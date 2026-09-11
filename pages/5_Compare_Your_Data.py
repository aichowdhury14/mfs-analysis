import io

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.data_loader import load_monthly_totals

st.set_page_config(page_title="Compare Your Data", page_icon="📤", layout="wide")
st.title("📤 Compare Your Own MFS Data")
st.caption(
    "Have a business's MFS transaction log? Upload it to benchmark against the national monthly trend. "
    "Processing happens in this session only — nothing is written to disk or shared."
)

UNIT_TO_CRORE = {"Crore BDT": 1, "Lakh BDT": 1 / 100, "Taka (BDT)": 1 / 10_000_000}

unit = st.selectbox("Your value column is in", list(UNIT_TO_CRORE.keys()))
uploaded = st.file_uploader("Upload CSV (columns: `month` as YYYY-MM, `value`)", type="csv")

st.download_button(
    "Download a sample template",
    data="month,value\n2024-06,850\n2024-08,910\n2024-09,940\n",
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
                st.success(f"Loaded {len(user_df)} rows.")

                national = load_monthly_totals()

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=national["date"], y=national["total_transaction_value_crore_bdt"] / 100000,
                    mode="lines+markers", name="National (lakh crore BDT)", line=dict(width=3),
                    yaxis="y1",
                ))
                fig.add_trace(go.Scatter(
                    x=user_df["date"], y=user_df["value_crore"],
                    mode="lines+markers", name="Your data (crore BDT)", line=dict(width=3, dash="dot"),
                    yaxis="y2",
                ))
                fig.update_layout(
                    height=460,
                    margin=dict(l=10, r=10, t=30, b=10),
                    yaxis=dict(title="National — lakh crore BDT"),
                    yaxis2=dict(title="Your data — crore BDT", overlaying="y", side="right"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02),
                )
                st.plotly_chart(fig, use_container_width=True)
                st.caption(
                    "Two independent scales shown together (national in lakh crore, yours in crore) so shape "
                    "and timing are comparable even though the absolute sizes differ enormously — this is not "
                    "a claim that your series shares units with the national one."
                )

                with st.expander("Your parsed data"):
                    st.dataframe(user_df[["month", "value", "value_crore"]], use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Couldn't parse that file: {e}")
else:
    st.info("Upload a CSV to see your data plotted against the national trend, or try the sample template above.")
