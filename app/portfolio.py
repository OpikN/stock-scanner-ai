import pandas as pd
import os
import time

from app.config import (
    POSITIONS_PATH,
    INITIAL_BALANCE,
    SL_PERCENT,
    TP1_PERCENT,
    TP2_PERCENT,
    TRAILING_PERCENT,
    RISK_SAFE,
    RISK_AGGRESSIVE,
    MAX_OPEN_POSITIONS
)

from app.telegram import (
    send_telegram
)

# =========================
# LOAD POSITIONS
# =========================
def load_positions():

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
# SAVE POSITIONS
# =========================
def save_positions(df):

    df.to_csv(
        POSITIONS_PATH,
        index=False
    )

# =========================
# LIVE EQUITY
# =========================
def get_live_equity():

    df = load_positions()

    if df.empty:

        return INITIAL_BALANCE

    pnl = df["pnl"].sum()

    equity = (
        INITIAL_BALANCE + pnl
    )

    if equity < 0:

        equity = INITIAL_BALANCE

    return round(
        equity,
        0
    )

# =========================
# POSITION SIZE
# =========================
def calculate_position_size(
    entry,
    aggressive=True
):

    equity = get_live_equity()

    risk = (
        RISK_AGGRESSIVE
        if aggressive
        else RISK_SAFE
    )

    risk_amount = (
        equity * risk
    )

    sl_distance = (
        entry * SL_PERCENT
    )

    size = (
        risk_amount /
        sl_distance
    )

    max_position_value = (
        equity * 0.2
    )

    max_size = (
        max_position_value /
        entry
    )

    if size > max_size:

        size = max_size

    return round(
        size,
        4
    )

# =========================
# OPEN POSITION
# =========================
def open_position(
    stock,
    side,
    entry
):

    df = load_positions()

    if not df.empty:

        open_count = len(

            df[
                df["status"]
                == "OPEN"
            ]
        )

        if (
            open_count
            >=
            MAX_OPEN_POSITIONS
        ):

            return

    size = calculate_position_size(
        entry
    )

    if side == "BUY":

        sl = (
            entry *
            (1 - SL_PERCENT)
        )

        tp1 = (
            entry *
            (1 + TP1_PERCENT)
        )

        tp2 = (
            entry *
            (1 + TP2_PERCENT)
        )

    else:

        sl = (
            entry *
            (1 + SL_PERCENT)
        )

        tp1 = (
            entry *
            (1 - TP1_PERCENT)
        )

        tp2 = (
            entry *
            (1 - TP2_PERCENT)
        )

    new_position = {

        "time":
            time.time(),

        "stock":
            stock,

        "side":
            side,

        "entry":
            entry,

        "size":
            size,

        "tp1":
            tp1,

        "tp2":
            tp2,

        "sl":
            sl,

        "status":
            "OPEN",

        "partial":
            False,

        "pnl":
            0
    }

    new_df = pd.DataFrame(
        [new_position]
    )

    if df.empty:

        df = new_df

    else:

        df = pd.concat(

            [df, new_df],

            ignore_index=True
        )

    save_positions(df)

    send_telegram(

        f"🚀 NEW POSITION\n\n"

        f"{stock}\n"

        f"{side}\n\n"

        f"Entry: {entry:.2f}\n"

        f"TP1: {tp1:.2f}\n"

        f"TP2: {tp2:.2f}\n"

        f"SL: {sl:.2f}\n\n"

        f"💰 Equity: "
        f"{get_live_equity():,.0f}"
    )

# =========================
# UPDATE POSITIONS
# =========================
def update_positions(
    latest_prices
):

    df = load_positions()

    if df.empty:
        return

    for idx, row in df.iterrows():

        try:

            if row["status"] != "OPEN":
                continue

            stock = row["stock"]

            side = row["side"]

            entry = float(
                row["entry"]
            )

            size = float(
                row["size"]
            )

            tp1 = float(
                row["tp1"]
            )

            tp2 = float(
                row["tp2"]
            )

            sl = float(
                row["sl"]
            )

            partial = bool(
                row["partial"]
            )

            current = latest_prices.get(
                stock,
                entry
            )

            # =========================
            # CALCULATE PNL
            # =========================
            if side == "BUY":

                pnl = (
                    current - entry
                ) * size

            else:

                pnl = (
                    entry - current
                ) * size

            df.at[idx, "pnl"] = pnl

            # =========================
            # PRICE CHANGE DETECTOR
            # =========================
            price_change = round(
                current - entry,
                2
            )

            if side == "SELL":

                price_change = round(
                    entry - current,
                    2
                )

            if (
                abs(price_change) >= 5
                and
                abs(pnl) >= 100000
            ):

                send_telegram(

                    f"📈 PRICE UPDATE\n\n"

                    f"{stock}\n\n"

                    f"{entry:.2f} "
                    f"→ "
                    f"{current:.2f}\n\n"

                    f"PnL:\n"

                    f"{pnl:,.0f}"
                )

            # =========================
            # LIVE POSITION
            # =========================
            if abs(pnl) > 100000:

                send_telegram(

                    f"📊 LIVE POSITION\n\n"

                    f"{stock}\n"

                    f"{side}\n\n"

                    f"Entry: "
                    f"{entry:.2f}\n"

                    f"Current: "
                    f"{current:.2f}\n\n"

                    f"PnL:\n"

                    f"{pnl:,.0f}\n\n"

                    f"SL:\n"

                    f"{sl:.2f}\n\n"

                    f"TP1:\n"

                    f"{tp1:.2f}"
                )

            # =========================
            # BUY LOGIC
            # =========================
            if side == "BUY":

                if (
                    current >= tp1
                    and
                    not partial
                ):

                    df.at[
                        idx,
                        "partial"
                    ] = True

                    send_telegram(

                        f"💰 PARTIAL CLOSE\n\n"

                        f"{stock}\n"

                        f"PnL: {pnl:,.0f}"
                    )

                trailing_sl = (
                    current *
                    (
                        1 -
                        TRAILING_PERCENT
                    )
                )

                if trailing_sl > sl:

                    df.at[
                        idx,
                        "sl"
                    ] = trailing_sl

                    send_telegram(

                        f"📈 TRAILING UPDATE\n\n"

                        f"{stock}\n"

                        f"New SL: "
                        f"{trailing_sl:.2f}"
                    )

                if (
                    current >= tp2
                    or
                    current <= sl
                ):

                    df.at[
                        idx,
                        "status"
                    ] = "CLOSED"

                    result = (
                        "TP HIT"
                        if pnl > 0
                        else "SL HIT"
                    )

                    send_telegram(

                        f"🔥 POSITION CLOSED\n\n"

                        f"{stock}\n"

                        f"{result}\n\n"

                        f"PnL: "
                        f"{pnl:,.0f}\n\n"

                        f"💰 Equity: "
                        f"{get_live_equity():,.0f}"
                    )

            # =========================
            # SELL LOGIC
            # =========================
            else:

                if (
                    current <= tp1
                    and
                    not partial
                ):

                    df.at[
                        idx,
                        "partial"
                    ] = True

                    send_telegram(

                        f"💰 PARTIAL CLOSE\n\n"

                        f"{stock}\n"

                        f"PnL: {pnl:,.0f}"
                    )

                trailing_sl = (
                    current *
                    (
                        1 +
                        TRAILING_PERCENT
                    )
                )

                if trailing_sl < sl:

                    df.at[
                        idx,
                        "sl"
                    ] = trailing_sl

                    send_telegram(

                        f"📈 TRAILING UPDATE\n\n"

                        f"{stock}\n"

                        f"New SL: "
                        f"{trailing_sl:.2f}"
                    )

                if (
                    current <= tp2
                    or
                    current >= sl
                ):

                    df.at[
                        idx,
                        "status"
                    ] = "CLOSED"

                    result = (
                        "TP HIT"
                        if pnl > 0
                        else "SL HIT"
                    )

                    send_telegram(

                        f"🔥 POSITION CLOSED\n\n"

                        f"{stock}\n"

                        f"{result}\n\n"

                        f"PnL: "
                        f"{pnl:,.0f}\n\n"

                        f"💰 Equity: "
                        f"{get_live_equity():,.0f}"
                    )

        except Exception as e:

            print(
                f"UPDATE ERROR: {e}"
            )

    save_positions(df)
