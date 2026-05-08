import pandas as pd

from app.config import (

    POSITIONS_PATH,

    INITIAL_BALANCE,

    TP1_PERCENT,

    TP2_PERCENT,

    SL_PERCENT
)

from app.telegram_reports import (

    send_partial_close,

    send_trailing_update,

    send_position_closed
)


# =========================
# LOAD POSITIONS
# =========================

def load_positions():

    try:

        df = pd.read_csv(
            POSITIONS_PATH
        )

        if df.empty:

            return pd.DataFrame()

        return df

    except:

        return pd.DataFrame()


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

    entry
):

    positions = load_positions()

    tp1 = (

        entry * (1 + TP1_PERCENT)

        if side == "BUY"

        else

        entry * (1 - TP1_PERCENT)
    )

    tp2 = (

        entry * (1 + TP2_PERCENT)

        if side == "BUY"

        else

        entry * (1 - TP2_PERCENT)
    )

    sl = (

        entry * (1 - SL_PERCENT)

        if side == "BUY"

        else

        entry * (1 + SL_PERCENT)
    )

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

        entry = row["entry"]

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

        positions.loc[idx, "pnl"] = pnl

        # =========================
        # PARTIAL CLOSE
        # =========================

        if (

            not row["partial_taken"]

            and

            (
                (
                    side == "BUY"

                    and

                    current_price >= row["tp1"]
                )

                or

                (
                    side == "SELL"

                    and

                    current_price <= row["tp1"]
                )
            )
        ):

            positions.loc[
                idx,
                "partial_taken"
            ] = True

            send_partial_close(

                stock,

                pnl
            )

        # =========================
        # TRAILING STOP
        # =========================

        if side == "BUY":

            new_sl = max(

                row["sl"],

                current_price * 0.99
            )

        else:

            new_sl = min(

                row["sl"],

                current_price * 1.01
            )

        if new_sl != row["sl"]:

            positions.loc[
                idx,
                "sl"
            ] = new_sl

            send_trailing_update(

                stock,

                new_sl
            )

        # =========================
        # TP2 CLOSE
        # =========================

        tp_hit = (

            (
                side == "BUY"

                and

                current_price >= row["tp2"]
            )

            or

            (
                side == "SELL"

                and

                current_price <= row["tp2"]
            )
        )

        # =========================
        # SL CLOSE
        # =========================

        sl_hit = (

            (
                side == "BUY"

                and

                current_price <= row["sl"]
            )

            or

            (
                side == "SELL"

                and

                current_price >= row["sl"]
            )
        )

        if tp_hit or sl_hit:

            positions.loc[
                idx,
                "status"
            ] = "CLOSED"

            reason = (

                "TP HIT"

                if tp_hit

                else

                "SL HIT"
            )

            send_position_closed(

                stock,

                reason,

                pnl,

                get_live_equity()
            )

    save_positions(
        positions
    )
