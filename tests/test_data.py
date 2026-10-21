from datetime import date

import pytest

from src.data import breakdown, compute_kpis, filter_sales, load_sales, monthly_revenue


@pytest.fixture(scope="module")
def df():
    return load_sales()


def test_dataset_shape(df):
    assert len(df) == 6000
    assert df["order_id"].is_unique
    assert {"order_date", "region", "category", "channel", "revenue", "profit"} <= set(df.columns)


def test_filter_by_date(df):
    out = filter_sales(df, date(2025, 1, 1), date(2025, 12, 31))
    assert not out.empty
    assert (out["order_date"].dt.year == 2025).all()


def test_empty_filters_mean_all(df):
    start, end = df["order_date"].min().date(), df["order_date"].max().date()
    assert len(filter_sales(df, start, end, [], [], [])) == len(df)


def test_filter_by_dimensions(df):
    start, end = df["order_date"].min().date(), df["order_date"].max().date()
    out = filter_sales(df, start, end, regions=["Cusco"], channels=["Online"])
    assert set(out["region"]) == {"Cusco"}
    assert set(out["channel"]) == {"Online"}


def test_compute_kpis(df):
    k = compute_kpis(df)
    assert k["orders"] == len(df)
    assert k["revenue"] == pytest.approx(df["revenue"].sum())
    assert k["avg_ticket"] == pytest.approx(k["revenue"] / k["orders"])
    assert 0 < k["margin"] < 1


def test_compute_kpis_empty(df):
    k = compute_kpis(df.iloc[0:0])
    assert k == {"revenue": 0.0, "profit": 0.0, "orders": 0, "avg_ticket": 0.0, "margin": 0.0}


def test_monthly_revenue_totals_match(df):
    m = monthly_revenue(df)
    assert m["revenue"].sum() == pytest.approx(df["revenue"].sum())
    assert len(m) == 24  # ene-2024 .. dic-2025


def test_breakdown_sorted(df):
    b = breakdown(df, "category")
    assert list(b["revenue"]) == sorted(b["revenue"], reverse=True)
    assert b["revenue"].sum() == pytest.approx(df["revenue"].sum())


def test_seasonality_and_growth(df):
    by_month = df.groupby(df["order_date"].dt.month).size()
    assert by_month[12] > by_month[3]
    by_year = df.groupby(df["order_date"].dt.year)["revenue"].sum()
    assert by_year[2025] > by_year[2024]
