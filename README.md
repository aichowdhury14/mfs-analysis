# MFS Bangladesh — Mobile Financial Services Analysis

A data science project tracking Bangladesh's mobile financial services (MFS) industry —
bKash, Nagad, Rocket, Upay and every licensed operator, combined — using Bangladesh Bank's
official statistics. Runs entirely on classical pandas/statsmodels/scikit-learn: no LLM,
fast on a normal PC.

**Live dashboard (static, no install needed):** see `dashboard/index.html` — published as a
Claude Artifact for quick sharing.

**This app (full analysis, deployable):** a multi-page Streamlit app with time-series
forecasting, anomaly detection, category correlation, and a CSV-upload comparison tool.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`. Use the sidebar to navigate between pages.

## Project structure

```
bd-mfs-analysis/
├── app.py                          # Home page
├── pages/
│   ├── 1_Trends_and_Forecast.py    # Annual trends + Holt's exponential smoothing forecast
│   ├── 2_Category_Breakdown.py     # Cash-in/out, P2P, merchant, remittance mix over time
│   ├── 3_Anomaly_and_Patterns.py   # Growth outliers, cash-flow crossover, correlation
│   ├── 4_Provider_Landscape.py     # Estimated bKash/Nagad/Rocket market share
│   ├── 5_Compare_Your_Data.py      # Upload your own MFS CSV, benchmark vs national trend
│   └── 6_Sources_and_Methodology.py
├── src/
│   ├── data_loader.py              # CSV loading + derived columns (YoY growth, category shares)
│   ├── forecasting.py              # Holt's exponential smoothing (annual) + log-linear OLS (monthly)
│   ├── anomaly.py                  # Z-score growth-outlier flagging, cash-flow direction
│   └── correlation.py              # Category correlation matrix, linear vs exponential curve fit
├── data/                           # Source CSVs (see Sources & Methodology page for provenance)
├── analysis/                       # Standalone analysis script (analyze.py) — pandas only, no Streamlit
└── dashboard/                      # Static HTML dashboard (published as a Claude Artifact)
```

## Data sources

- **Bangladesh Bank Financial Stability Reports** (2022, 2023, 2024) — official annual industry
  stats and category-wise transaction breakdown.
- **Press coverage** (The Business Standard, Future Startup) — monthly 2024–25 figures citing
  Bangladesh Bank's releases.
- **Provider market share** — third-party estimates from trade press; Bangladesh Bank does not
  publish a per-operator breakdown. Clearly flagged in the app.

Full detail on the **Sources & Methodology** page inside the app.

## Deploying to Streamlit Community Cloud (free)

1. Push this repo to GitHub (see below).
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub.
3. Click **New app**, pick this repo, branch `main`, main file path `app.py`.
4. Click **Deploy**. Done — you get a public `*.streamlit.app` URL.

### Pushing to GitHub for the first time

```bash
git init
git add .
git commit -m "Initial commit: MFS Bangladesh analysis app"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

## Extending the data

The monthly series (`data/mfs_monthly_totals.csv`) is intentionally sparse — Bangladesh
Bank's live monthly comparative page sits behind bot-protection that blocks automated
scraping. To add more months, manually pull figures from
[bb.org.bd's MFS data page](https://www.bb.org.bd/en/index.php/financialactivity/mfsdata)
and append rows in the same format.
