"""Load and lightly transform the Bangladesh MFS datasets."""
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

CATEGORY_LABELS = {
    "inward_remittance": "Inward Remittance",
    "cash_in": "Cash In",
    "cash_out": "Cash Out",
    "p2p": "P2P Transfer",
    "salary_disbursement_b2p": "Salary Disbursement (B2P)",
    "utility_bill_p2b": "Utility Bill Payment (P2B)",
    "merchant_payment": "Merchant Payment",
    "government_payment": "Government Payment",
    "others": "Others",
}

CATEGORY_COLUMNS = list(CATEGORY_LABELS.keys())


def load_industry_stats() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "mfs_annual_industry_stats.csv")
    return df.sort_values("year").reset_index(drop=True)


def load_category_breakdown() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "mfs_annual_category_breakdown_billion_bdt.csv")
    return df.sort_values("year").reset_index(drop=True)


def load_monthly_totals() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "mfs_monthly_totals.csv")
    df["date"] = pd.to_datetime(df["year_month"], format="%Y-%m")
    return df.sort_values("date").reset_index(drop=True)


def load_provider_shares() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "mfs_provider_market_share_estimates.csv")
    return df


def load_remittance_annual() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "mfs_remittance_annual.csv")
    return df.sort_values("year").reset_index(drop=True)


def industry_with_growth() -> pd.DataFrame:
    """Industry stats with year-over-year percent change columns added."""
    df = load_industry_stats().set_index("year")
    numeric_cols = [
        "agents_millions",
        "registered_clients_millions",
        "active_accounts_millions",
        "total_transactions_millions",
        "total_transaction_volume_billion_bdt",
    ]
    growth = df[numeric_cols].pct_change() * 100
    growth.columns = [f"{c}_yoy_pct" for c in growth.columns]
    return df.join(growth).reset_index()


def category_with_shares() -> pd.DataFrame:
    """Category breakdown with each category expressed as % of that year's total."""
    df = load_category_breakdown().set_index("year")
    numeric = df[CATEGORY_COLUMNS]
    shares = numeric.div(df["total"], axis=0) * 100
    shares.columns = [f"{c}_share_pct" for c in shares.columns]
    return df.join(shares).reset_index()
