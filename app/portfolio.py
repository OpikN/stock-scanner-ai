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

    try:

        df.to_csv(
            POSITIONS_PATH,
            index=False
        )

    except Exception as e:

        print(
            f"SAVE ERROR: {e}"
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

    try:

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

    except Exception as e:

        print(
            f"OPEN POSITION ERROR: {e}"
        )

# =========================
# UPDATE POSITIONS
# =========================

def update_positions(

    stock,

    current_price
):

    try:

        positions = load_positions()

        if positions.empty:

            return

        for idx, row in positions.iterrows():

            if row["status"] != "OPEN":

                continue

            if row["stock"] != stock:

                continue

            side = str(
                row["side"]
            )

            entry = float(
                row["entry"]
            )

            pnl = 0

            # =========================
            # BUY
            # =========================

            if side == "BUY":

                pnl = (
                    current_price - entry
                ) * 100

            # =========================
            # SELL
            # =========================

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

    except Exception as e:

        print(
            f"UPDATE POSITION ERROR: {e}"
        )

# =========================
# GET OPEN POSITIONS
# =========================

def get_open_positions():

    try:

        df = load_positions()

        if df.empty:

            return pd.DataFrame()

        return df[
            df["status"] == "OPEN"
        ]

    except Exception:

        return pd.DataFrame()

# =========================
# GET CLOSED POSITIONS
# =========================

def get_closed_positions():

    try:

        df = load_positions()

        if df.empty:

            return pd.DataFrame()

        return df[
            df["status"] == "CLOSED"
        ]

    except Exception:

        return pd.DataFrame()

# =========================
# CLOSED EQUITY
# =========================

def get_closed_equity():

    try:

        closed = get_closed_positions()

        if closed.empty:

            return INITIAL_BALANCE

        pnl = closed["pnl"].sum()

        return INITIAL_BALANCE + pnl

    except Exception:

        return INITIAL_BALANCE

# =========================
# LIVE EQUITY
# =========================

def get_live_equity():

    try:

        open_df = get_open_positions()

        closed_equity = get_closed_equity()

        if open_df.empty:

            return closed_equity

        floating = open_df["pnl"].sum()

        return closed_equity + floating

    except Exception:

        return INITIAL_BALANCE

# =========================
# BALANCE
# =========================

def get_balance():

    try:

        return get_closed_equity()

    except Exception:

        return INITIAL_BALANCE

# =========================
# TOTAL PNL
# =========================

def get_total_pnl():

    try:

        closed = get_closed_positions()

        if closed.empty:

            return 0

        return closed["pnl"].sum()

    except Exception:

        return 0
