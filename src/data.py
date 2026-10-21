"""Data loading and business logic for the sales dashboard.

This module has no Streamlit dependency so it can be tested with pytest.
"""

from datetime import date
from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "sales.csv"


def load_sales(path: Path | str = DATA_PATH) -> pd.DataFrame:
    """Read the sales CSV and parse dates."""
    return pd.read_csv(path, parse_dates=["order_date"])


def filter_sales(
    df: pd.DataFrame,
    start: date,
    end: date,
    regions: list[str] | None = None,
    categories: list[str] | None = None,
    channels: list[str] | None = None,
) -> pd.DataFrame:
    """Filter by date range and optional dimensions (empty list = all)."""
    mask = (df["order_date"].dt.date >= start) & (df["order_date"].dt.date <= end)
    if regions:
        mask &= df["region"].isin(regions)
    if categories:
        mask &= df["category"].isin(categories)
    if channels:
        mask &= df["channel"].isin(channels)
    return df.loc[mask]


def compute_kpis(df: pd.DataFrame) -> dict:
    """Headline metrics; safe for empty data frames."""
    revenue = float(df["revenue"].sum())
    profit = float(df["profit"].sum())
    orders = int(df["order_id"].nunique())
    return {
        "revenue": revenue,
        "profit": profit,
        "orders": orders,
        "avg_ticket": revenue / orders if orders else 0.0,
        "margin": profit / revenue if revenue else 0.0,
    }


def monthly_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Revenue and profit aggregated by calendar month."""
    out = (
        df.groupby(df["order_date"].dt.to_period("M"))[["revenue", "profit"]]
        .sum()
        .reset_index()
        .rename(columns={"order_date": "month"})
    )
    out["month"] = out["month"].dt.to_timestamp()
    return out


def breakdown(df: pd.DataFrame, by: str | list[str], value: str = "revenue") -> pd.DataFrame:
    """Sum of `value` grouped by one or more columns, sorted descending."""
    return (
        df.groupby(by)[value]
        .sum()
        .reset_index()
        .sort_values(value, ascending=False, ignore_index=True)
    )
