"""Time-series forecasting for MFS transaction volume.

Two models, kept deliberately simple because the underlying series are short
(5 annual points, ~7 monthly points) - a heavy model would overfit noise.

- Annual volume  -> Holt's linear trend (statsmodels ExponentialSmoothing,
  trend='add', no seasonality: nothing seasonal to capture at annual granularity).
- Monthly volume -> linear regression on a log scale (captures the compounding
  growth pattern visible in the 2024-25 press figures) with a naive
  extrapolation confidence band, since 7 points is too few for ARIMA's usual
  minimum (~2 full seasonal cycles).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing


def forecast_annual_volume(df: pd.DataFrame, periods: int = 3) -> pd.DataFrame:
    """Forecast total_transaction_volume_billion_bdt for `periods` years ahead.

    Returns a DataFrame with year, forecast, ci_lower, ci_upper (80% band).
    """
    series = df.set_index("year")["total_transaction_volume_billion_bdt"]
    model = ExponentialSmoothing(series, trend="add", damped_trend=True).fit()
    forecast = model.forecast(periods)

    resid_std = np.std(model.resid, ddof=1)
    z80 = 1.2816
    last_year = int(series.index.max())
    years = [last_year + i + 1 for i in range(periods)]

    # widen the band with horizon since compounding uncertainty grows
    widths = [resid_std * z80 * np.sqrt(h + 1) for h in range(periods)]

    return pd.DataFrame(
        {
            "year": years,
            "forecast_billion_bdt": forecast.values,
            "ci_lower": forecast.values - widths,
            "ci_upper": forecast.values + widths,
        }
    )


def forecast_monthly_volume(df: pd.DataFrame, periods: int = 6) -> pd.DataFrame:
    """Forecast total_transaction_value_crore_bdt for `periods` months ahead.

    Fits log(value) ~ elapsed_months by OLS (captures multiplicative growth),
    then exponentiates back. Confidence band from residual std on the log scale.

    Uses actual elapsed months since the first observation, not row position -
    the underlying press-reported series has real gaps (e.g. no confirmed figure
    between March and August 2025), and treating each row as one equal time-step
    would silently understate the true month-over-month growth rate.
    """
    d = df.dropna(subset=["total_transaction_value_crore_bdt"]).copy()
    first_date = d["date"].min()
    d["t"] = (d["date"] - first_date).dt.days / 30.4375  # elapsed months, fractional
    y_log = np.log(d["total_transaction_value_crore_bdt"])

    coeffs = np.polyfit(d["t"], y_log, 1)
    slope, intercept = coeffs
    fitted = slope * d["t"] + intercept
    resid_std = np.std(y_log - fitted, ddof=2)

    last_date = d["date"].max()
    future_dates = pd.date_range(last_date, periods=periods + 1, freq="MS")[1:]
    future_t = (future_dates - first_date).days / 30.4375
    future_log = slope * future_t + intercept

    z80 = 1.2816
    horizon_steps = np.arange(1, periods + 1)
    widths = resid_std * z80 * np.sqrt(1 + horizon_steps / len(d))

    return pd.DataFrame(
        {
            "date": future_dates,
            "forecast_crore_bdt": np.exp(future_log),
            "ci_lower": np.exp(future_log - widths),
            "ci_upper": np.exp(future_log + widths),
        }
    )


def monthly_growth_rate(df: pd.DataFrame) -> float:
    """Implied average month-over-month compound growth rate, as a percentage.

    Computed from the log-linear slope over actual elapsed time (see
    forecast_monthly_volume) rather than a plain pct_change().mean(), because
    the series has real gaps between confirmed months.
    """
    d = df.dropna(subset=["total_transaction_value_crore_bdt"]).copy()
    first_date = d["date"].min()
    t = (d["date"] - first_date).dt.days / 30.4375
    y_log = np.log(d["total_transaction_value_crore_bdt"])
    slope, _ = np.polyfit(t, y_log, 1)
    return (np.exp(slope) - 1) * 100
