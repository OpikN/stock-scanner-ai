import pandas as pd

from app.config import (
    POSITIONS_PATH,
    INITIAL_BALANCE
)

# =========================
# LOAD POSITIONS
# =========================

def load_positions():

    try:

        df = pd.read_csv(
            POSITIONS_PATH
        )

        return df

    except:

        columns = [

            "stock",
            "side",
            "entry",
            "tp1",
            "tp2",
            "sl",
            "status",
            "pnl",
            "partial_taken"
        ]

        return pd.DataFrame(
            columns=columns
        )

# =========================
# SAVE POSITIONS
# =========================

def save_positions(df):

    df.to_csv(
        POSITIONS_PATH,
        index=False
    )

# =========================
# OPEN POSITIONS
# =========================

def get_open_positions():

    df = load_positions()

    if df.empty:

        return df

    return df[
        df["status"] == "OPEN"
    ]

# =========================
# CLOSED POSITIONS
# =========================

def get_closed_positions():

    df = load_positions()

    if df.empty:

        return df

    return df[
        df["status"] == "CLOSED"
    ]

# =========================
# CLOSED EQUITY
# =========================

def get_closed_equity():

    closed = get_closed_positions()

    if closed.empty:

        return INITIAL_BALANCE

    pnl = closed["pnl"].sum()

    return INITIAL_BALANCE + pnl

# =========================
# LIVE EQUITY
# =========================

def get_live_equity():

    open_df = get_open_positions()

    closed_equity = get_closed_equity()

    if open_df.empty:

        return closed_equity

    floating = open_df["pnl"].sum()

    return closed_equity + floating

# =========================
# BALANCE
# =========================

def get_balance():

    return get_closed_equity()

# =========================
# TOTAL PNL
# =========================

def get_total_pnl():

    closed = get_closed_positions()

    if closed.empty:

        return 0

    return closed["pnl"].sum()
