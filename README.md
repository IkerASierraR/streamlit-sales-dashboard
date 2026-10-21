# 📊 Streamlit Sales Dashboard

Interactive sales dashboard built with **Streamlit** and **Plotly**, tested with **pytest** and deployed automatically to **Streamlit Community Cloud** through **GitHub Actions**.

🔗 **Live app:** https://iker-sales-dashboard.streamlit.app
📝 **Article:** [Building and Deploying an Interactive Sales Dashboard with Streamlit, GitHub Actions and Streamlit Community Cloud](https://dev.to/ikers/building-and-deploying-an-interactive-sales-dashboard-with-streamlit-github-actions-and-streamlit-5fim)

## Features

- 5 KPIs: revenue, profit, orders, average ticket and margin
- Filters: date range, region, category and channel
- Charts: monthly trend, revenue by category, revenue by region, online vs. store, category × region heatmap
- Table of filtered orders with CSV download
- Synthetic, reproducible dataset (6,000 orders, 2024-2025, 5 Peruvian regions)

## Project structure

```
.
├── app.py                     # Streamlit UI + charts
├── src/data.py                # Data logic (no Streamlit → testable)
├── data/sales.csv             # Synthetic dataset (6,000 orders 2024-2025)
├── scripts/generate_data.py   # Reproducible dataset generator
├── tests/                     # Unit tests + app smoke test
├── .streamlit/config.toml     # Theme
├── .github/workflows/ci-cd.yml
├── requirements.txt
└── requirements-dev.txt
```

## Run locally

```bash
pip install -r requirements-dev.txt
streamlit run app.py
```

Regenerate the dataset (always identical thanks to `seed=42`):

```bash
python scripts/generate_data.py
```

Run lint and tests:

```bash
ruff check .
pytest -v
```

## CI/CD

```
push to main ──► GitHub Actions: ruff + pytest
                     │ (only if everything passes ✅)
                     ▼
         promote the commit to the `production` branch
                     │
                     ▼
  Streamlit Community Cloud detects the change ──► redeploy
                     │
                     ▼
     Actions checks that the public URL returns HTTP 200
```

Streamlit Community Cloud is connected to the **`production`** branch, which only the workflow updates, so broken code never reaches the live app.

Setup:

1. On [share.streamlit.io](https://share.streamlit.io): **Create app** → repository `IkerASierraR/streamlit-sales-dashboard`, branch `production`, main file `app.py`.
2. In GitHub: **Settings → Secrets and variables → Actions → Variables** → add `APP_URL` = `https://iker-sales-dashboard.streamlit.app`.

## Tech stack

Python 3.12 · Streamlit · pandas · NumPy · Plotly · pytest · ruff · GitHub Actions
