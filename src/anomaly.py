"""Detect years/months where growth deviated sharply from the underlying trend."""
from __future__ import annotations

import numpy as np
import pandas as pd


def flag_growth_anomalies(df: pd.DataFrame, value_col: str, label_col: str, z_thresh: float = 1.0) -> pd.DataFrame:
    """Flag periods whose YoY/MoM growth is more than `z_thresh` std devs from the mean growth.

    With only a handful of points, a z-score threshold of 1.0 (not the usual 2-3)
    is intentional - it surfaces "notably different" periods for a human to look
    at, not statistically rigorous outliers. Labelled clearly in the UI as such.
    """
    d = df.copy()
    d["growth_pct"] = d[value_col].pct_change() * 100
    mean_g, std_g = d["growth_pct"].mean(), d["growth_pct"].std()
    d["z_score"] = (d["growth_pct"] - mean_g) / std_g
    d["is_notable"] = d["z_score"].abs() >= z_thresh
    return d[[label_col, value_col, "growth_pct", "z_score", "is_notable"]]


def cash_flow_direction(category_df: pd.DataFrame) -> pd.DataFrame:
    """Track whether cash is net flowing into or out of the MFS system each year."""
    d = category_df.copy()
    d["cash_gap_billion_bdt"] = d["cash_in"] - d["cash_out"]
    d["direction"] = np.where(d["cash_gap_billion_bdt"] >= 0, "Net cash-in", "Net cash-out")
    return d[["year", "cash_in", "cash_out", "cash_gap_billion_bdt", "direction"]]
