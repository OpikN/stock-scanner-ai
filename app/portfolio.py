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

        return pd.read_csv(
            POSITIONS_PATH
        )

    except Exception:

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
# OPEN POSITION
# =========================

def open_position(

    stock,

    side,

    entry,

    tp1,

    tp2,

    sl
):

    positions = load_positions()

    new_row = {

        "stock": stock,

        "side": side,

        "entry": entry,

        "tp1": tp1,

        "tp2": tp2,

        "sl": sl,

        "status": "OPEN",

        "pnl": 0,

        "partial_taken": False
    }

    positions = pd.concat(

        [

            positions,

            pd.DataFrame([new_row])
        ],

        ignore_index=True
    )

    save_positions(
        positions
    )

# =========================
# UPDATE POSITIONS
# =========================

def update_positions(

    stock,

    current_price
):

    positions = load_positions()

    if positions.empty:

        return

    for idx, row in positions.iterrows():

        if row["status"] != "OPEN":

            continue

        if row["stock"] != stock:

            continue

        side = row["side"]

        entry = float(
            row["entry"]
        )

        pnl = 0

        if side == "BUY":

            pnl = (
                current_price - entry
            ) * 100

        else:

            pnl = (
                entry - current_price
            ) * 100

        positions.loc[
            idx,
            "pnl"
        ] = pnl

    save_positions(
        positions
    )

# =========================
# GET OPEN POSITIONS
# =========================

def get_open_positions():

    df = load_positions()

    if df.empty:

        return pd.DataFrame()

    return df[
        df["status"] == "OPEN"
    ]

# =========================
# GET CLOSED POSITIONS
# =========================

def get_closed_positions():

    df = load_positions()

    if df.empty:

        return pd.DataFrame()

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
# =========================
# CALCULATE EQUITY
# =========================

def calculate_equity():

    positions = get_open_positions()

    initial_balance = 100000000

    floating_pnl = 0

    if not positions.empty:

        floating_pnl = positions[
            "pnl"
        ].sum()

    live_equity = (

        initial_balance
        + floating_pnl

    )

    return {

        "live_equity": live_equity,

        "floating_pnl": floating_pnl

    }
