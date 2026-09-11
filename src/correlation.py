"""Correlation and growth-pattern analysis across MFS transaction categories."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from src.data_loader import CATEGORY_COLUMNS


def category_correlation(category_df: pd.DataFrame) -> pd.DataFrame:
    """Correlation matrix of category levels across years.

    Only 4 years of annual data means this describes co-movement in the
    growth era so far, not a statistically robust long-run relationship -
    every category has grown together, so expect high positive correlation
    almost everywhere; the useful signal is which pairs deviate from that.
    """
    return category_df[CATEGORY_COLUMNS].corr()


def fit_growth_curve(industry_df: pd.DataFrame, value_col: str) -> dict:
    """Fit linear and exponential (log-linear) models to a metric over years,
    returning both R^2 so the better-fitting growth shape is visible.
    """
    years = industry_df["year"].values.reshape(-1, 1)
    y = industry_df[value_col].values

    lin_model = LinearRegression().fit(years, y)
    lin_r2 = lin_model.score(years, y)

    log_y = np.log(y)
    exp_model = LinearRegression().fit(years, log_y)
    exp_r2 = exp_model.score(years, log_y)

    implied_annual_growth_pct = (np.exp(exp_model.coef_[0]) - 1) * 100

    return {
        "linear_r2": lin_r2,
        "linear_slope": lin_model.coef_[0],
        "exponential_r2": exp_r2,
        "implied_annual_growth_pct": implied_annual_growth_pct,
        "better_fit": "exponential" if exp_r2 > lin_r2 else "linear",
    }
