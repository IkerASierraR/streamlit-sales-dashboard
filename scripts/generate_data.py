"""Generate a reproducible synthetic sales dataset (2024-2025).

Usage:
    python scripts/generate_data.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
N_ORDERS = 6000
OUTPUT = Path(__file__).resolve().parents[1] / "data" / "sales.csv"

REGIONS = ["Lima", "Arequipa", "Trujillo", "Cusco", "Piura"]
REGION_WEIGHTS = [0.45, 0.18, 0.14, 0.12, 0.11]

CHANNELS = ["Online", "Store"]
CHANNEL_WEIGHTS = [0.45, 0.55]

# category -> (min unit price, max unit price, cost ratio)
CATEGORIES = {
    "Electronics": (150, 2500, 0.78),
    "Home": (30, 600, 0.62),
    "Sports": (25, 450, 0.60),
    "Clothing": (20, 250, 0.50),
    "Beauty": (10, 150, 0.45),
}
CATEGORY_WEIGHTS = [0.18, 0.22, 0.18, 0.25, 0.17]


def generate(seed: int = SEED, n_orders: int = N_ORDERS) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    dates = pd.date_range("2024-01-01", "2025-12-31", freq="D")
    weights = np.ones(len(dates))
    weights[dates.month.isin([7])] *= 1.4        # Fiestas Patrias
    weights[dates.month.isin([11, 12])] *= 1.8   # Campaña navideña
    weights[dates.year == 2025] *= 1.2           # Crecimiento anual
    weights /= weights.sum()

    order_dates = rng.choice(dates, size=n_orders, p=weights)

    categories = rng.choice(list(CATEGORIES), size=n_orders, p=CATEGORY_WEIGHTS)
    low = np.array([CATEGORIES[c][0] for c in categories])
    high = np.array([CATEGORIES[c][1] for c in categories])
    cost_ratio = np.array([CATEGORIES[c][2] for c in categories])

    unit_price = np.round(rng.uniform(low, high), 2)
    quantity = rng.integers(1, 6, size=n_orders)
    discount = rng.choice([0.0, 0.05, 0.10, 0.15], size=n_orders, p=[0.6, 0.2, 0.15, 0.05])
    revenue = np.round(unit_price * quantity * (1 - discount), 2)
    cost = np.round(unit_price * quantity * cost_ratio * rng.uniform(0.95, 1.05, n_orders), 2)

    df = pd.DataFrame(
        {
            "order_id": [f"ORD-{i:05d}" for i in range(1, n_orders + 1)],
            "order_date": pd.to_datetime(order_dates),
            "region": rng.choice(REGIONS, size=n_orders, p=REGION_WEIGHTS),
            "category": categories,
            "channel": rng.choice(CHANNELS, size=n_orders, p=CHANNEL_WEIGHTS),
            "quantity": quantity,
            "unit_price": unit_price,
            "discount": discount,
            "revenue": revenue,
            "cost": cost,
            "profit": np.round(revenue - cost, 2),
        }
    )
    df = df.sort_values("order_date").reset_index(drop=True)
    df["order_id"] = [f"ORD-{i:05d}" for i in range(1, n_orders + 1)]
    return df


def main() -> None:
    df = generate()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False, date_format="%Y-%m-%d")
    print(f"Saved {len(df):,} orders to {OUTPUT}")


if __name__ == "__main__":
    main()
