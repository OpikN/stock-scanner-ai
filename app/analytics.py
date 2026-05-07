import pandas as pd
import os

from app.config import (
    POSITIONS_PATH
)

# =========================
# LOAD DATA
# =========================
def load_data():

    try:

        if os.path.exists(
            POSITIONS_PATH
        ):

            return pd.read_csv(
                POSITIONS_PATH
            )

        return pd.DataFrame()

    except:

        return pd.DataFrame()

# =========================
# TOTAL TRADES
# =========================
def total_trades():

    df = load_data()

    if df.empty:

        return 0

    closed = df[
        df["status"] == "CLOSED"
    ]

    return len(closed)

# =========================
# WINRATE
# =========================
def winrate():

    df = load_data()

    if df.empty:

        return 0

    closed = df[
        df["status"] == "CLOSED"
    ]

    if closed.empty:

        return 0

    wins = closed[
        closed["pnl"] > 0
    ]

    rate = (
        len(wins)
        /
        len(closed)
    ) * 100

    return round(
        rate,
        2
    )

# =========================
# TOTAL PNL
# =========================
def total_pnl():

    df = load_data()

    if df.empty:

        return 0

    closed = df[
        df["status"] == "CLOSED"
    ]

    if closed.empty:

        return 0

    return round(
        closed["pnl"].sum(),
        0
    )

# =========================
# BEST STOCK
# =========================
def best_stock():

    df = load_data()

    if df.empty:

        return "-"

    closed = df[
        df["status"] == "CLOSED"
    ]

    if closed.empty:

        return "-"

    grouped = closed.groupby(
        "stock"
    )["pnl"].sum()

    return grouped.idxmax()

# =========================
# WORST STOCK
# =========================
def worst_stock():

    df = load_data()

    if df.empty:

        return "-"

    closed = df[
        df["status"] == "CLOSED"
    ]

    if closed.empty:

        return "-"

    grouped = closed.groupby(
        "stock"
    )["pnl"].sum()

    return grouped.idxmin()

# =========================
# AVG PNL
# =========================
def avg_pnl():

    df = load_data()

    if df.empty:

        return 0

    closed = df[
        df["status"] == "CLOSED"
    ]

    if closed.empty:

        return 0

    return round(
        closed["pnl"].mean(),
        0
    )
