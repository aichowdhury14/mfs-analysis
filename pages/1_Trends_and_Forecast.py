import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.data_loader import industry_with_growth, load_monthly_totals
from src.forecasting import forecast_annual_volume, forecast_monthly_volume, monthly_growth_rate
from src.theme import COLORS, apply_plotly_template, inject_css, page_header, sidebar_brand, style_fig

st.set_page_config(page_title="Trends & Forecast", page_icon="📈", layout="wide")
inject_css()
apply_plotly_template()
sidebar_brand()

page_header("Annual & Monthly Series", "📈 Trends & Forecast", "Where the industry has been, and a statistical read on where it's headed.")

industry = industry_with_growth()
monthly = load_monthly_totals()

tab1, tab2 = st.tabs(["Annual trend & forecast", "Monthly (2024–25)"])

with tab1:
    metric_options = {
        "Transaction volume (billion BDT)": "total_transaction_volume_billion_bdt",
        "Active accounts (millions)": "active_accounts_millions",
        "Registered clients (millions)": "registered_clients_millions",
        "Agents (millions)": "agents_millions",
        "Total transactions (millions)": "total_transactions_millions",
    }
    choice = st.radio("Metric", list(metric_options.keys()), horizontal=True, label_visibility="collapsed")
    col = metric_options[choice]

    c1, c2 = st.columns([2.2, 1])
    with c1:
        st.markdown(f"##### {choice}, 2020–2024")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=industry["year"], y=industry[col], mode="lines+markers", name=choice,
            line=dict(width=3, color=COLORS["accent"]), marker=dict(size=9),
            fill="tozeroy", fillcolor="rgba(12,138,104,0.08)",
        ))
        fig.update_layout(yaxis_title=choice, xaxis_title="")
        fig.update_xaxes(tickmode="array", tickvals=industry["year"], range=[industry["year"].min() - 0.3, industry["year"].max() + 0.3])
        st.plotly_chart(style_fig(fig, hovermode="x"), use_container_width=True)

    with c2:
        st.markdown("##### Year-over-year")
        growth_col = f"{col}_yoy_pct"
        disp = industry[["year", growth_col]].dropna().rename(columns={growth_col: "YoY %"})
        fig_bar = go.Figure(go.Bar(
            x=disp["year"], y=disp["YoY %"],
            marker_color=[COLORS["good"] if v >= 0 else COLORS["bad"] for v in disp["YoY %"]],
            text=disp["YoY %"].round(1), textposition="outside",
        ))
        fig_bar.update_layout(yaxis_title="%", xaxis_title="")
        st.plotly_chart(style_fig(fig_bar, height=420, hovermode="x"), use_container_width=True)

    st.divider()

    st.markdown("##### Forecast: transaction volume, next 3 years")
    st.caption(
        "Holt's damped exponential smoothing fit on 5 annual data points. With this little history the "
        "80% confidence band is wide by construction — read this as a trend projection, not a precise prediction."
    )
    horizon = st.slider("Forecast horizon (years)", 1, 5, 3)
    forecast = forecast_annual_volume(industry, periods=horizon)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=industry["year"], y=industry["total_transaction_volume_billion_bdt"],
        mode="lines+markers", name="Actual", line=dict(width=3, color=COLORS["accent"]), marker=dict(size=9),
    ))
    fig2.add_trace(go.Scatter(
        x=pd.concat([pd.Series([industry["year"].iloc[-1]]), forecast["year"]]),
        y=pd.concat([pd.Series([industry["total_transaction_volume_billion_bdt"].iloc[-1]]), forecast["forecast_billion_bdt"]]),
        mode="lines+markers", name="Forecast", line=dict(width=3, dash="dash", color=COLORS["amber"]), marker=dict(size=9),
    ))
    fig2.add_trace(go.Scatter(
        x=pd.concat([forecast["year"], forecast["year"][::-1]]),
        y=pd.concat([forecast["ci_upper"], forecast["ci_lower"][::-1]]),
        fill="toself", fillcolor="rgba(199,117,42,0.15)", line=dict(width=0), name="80% CI",
    ))
    fig2.update_layout(yaxis_title="Billion BDT", xaxis_title="")
    all_years = pd.concat([industry["year"], forecast["year"]])
    fig2.update_xaxes(tickmode="array", tickvals=all_years, range=[all_years.min() - 0.3, all_years.max() + 0.3])
    st.plotly_chart(style_fig(fig2, height=440, hovermode="x unified"), use_container_width=True)

    with st.expander("Forecast table"):
        st.dataframe(forecast.round(1), use_container_width=True, hide_index=True)
        st.download_button(
            "Download forecast CSV", forecast.to_csv(index=False), "mfs_annual_forecast.csv", "text/csv",
        )

with tab2:
    st.caption(
        "Sparser and less official than the annual series — filled in as more months are confirmed from "
        "Bangladesh Bank releases. Growth fit on a log scale, using actual elapsed time between confirmed "
        "months (some months are missing from press coverage)."
    )
    avg_growth = monthly_growth_rate(monthly)
    m1, m2, m3 = st.columns(3)
    m1.metric("Implied avg. monthly growth", f"{avg_growth:.1f}%")
    m2.metric("Latest confirmed month", monthly["year_month"].iloc[-1])
    m3.metric("Months on record", len(monthly))

    periods = st.slider("Months to forecast", 1, 12, 6)
    monthly_forecast = forecast_monthly_volume(monthly, periods=periods)

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=monthly["date"], y=monthly["total_transaction_value_crore_bdt"], mode="lines+markers", name="Actual",
        line=dict(width=3, color=COLORS["accent"]), marker=dict(size=8),
    ))
    fig3.add_trace(go.Scatter(
        x=monthly_forecast["date"], y=monthly_forecast["forecast_crore_bdt"], mode="lines+markers", name="Forecast",
        line=dict(width=3, dash="dash", color=COLORS["amber"]), marker=dict(size=8),
    ))
    fig3.add_trace(go.Scatter(
        x=pd.concat([monthly_forecast["date"], monthly_forecast["date"][::-1]]),
        y=pd.concat([monthly_forecast["ci_upper"], monthly_forecast["ci_lower"][::-1]]),
        fill="toself", fillcolor="rgba(199,117,42,0.15)", line=dict(width=0), name="80% CI",
    ))
    fig3.update_layout(yaxis_title="Crore BDT", xaxis_title="")
    fig3.update_xaxes(rangeslider_visible=True)
    st.plotly_chart(style_fig(fig3, height=460, hovermode="x unified"), use_container_width=True)

    with st.expander("Monthly data & forecast table"):
        st.dataframe(monthly[["year_month", "total_transaction_value_crore_bdt", "total_transactions_count", "notes", "source"]],
                     use_container_width=True, hide_index=True)
        st.dataframe(monthly_forecast.round(1), use_container_width=True, hide_index=True)
