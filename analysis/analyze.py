import pandas as pd
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"

industry = pd.read_csv(DATA / "mfs_annual_industry_stats.csv")
category = pd.read_csv(DATA / "mfs_annual_category_breakdown_billion_bdt.csv")
monthly = pd.read_csv(DATA / "mfs_monthly_totals.csv")
shares = pd.read_csv(DATA / "mfs_provider_market_share_estimates.csv")

pd.set_option("display.width", 120)

print("=== Industry YoY growth (%) ===")
ind = industry.set_index("year")
yoy = ind[["agents_millions", "registered_clients_millions", "active_accounts_millions",
           "total_transactions_millions", "total_transaction_volume_billion_bdt"]].pct_change() * 100
print(yoy.round(2))

print("\n=== Category share of total transaction value (%) ===")
cat = category.set_index("year").drop(columns=["source"])
cat_share = cat.drop(columns=["total"]).div(cat["total"], axis=0) * 100
print(cat_share.round(2))

print("\n=== Category YoY growth (%) ===")
cat_growth = cat.pct_change() * 100
print(cat_growth.round(2))

print("\n=== Cash-in vs Cash-out gap (billion BDT) — net float direction ===")
cat["cash_gap"] = cat["cash_in"] - cat["cash_out"]
print(cat[["cash_in", "cash_out", "cash_gap"]])

print("\n=== Monthly totals (2024-2025 partial) ===")
print(monthly)

print("\n=== CAGR 2020-2024 (industry) ===")
years = industry["year"].max() - industry["year"].min()
for col in ["agents_millions", "registered_clients_millions", "active_accounts_millions",
            "total_transactions_millions", "total_transaction_volume_billion_bdt"]:
    start, end = industry[col].iloc[0], industry[col].iloc[-1]
    cagr = ((end / start) ** (1 / years) - 1) * 100
    print(f"{col}: {cagr:.2f}% CAGR")

print("\n=== Provider market share snapshots ===")
print(shares)
