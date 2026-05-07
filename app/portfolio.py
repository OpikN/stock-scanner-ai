import pandas as pd
import os
import time
import yfinance as yf

from app.config import (
    POSITIONS_PATH,
    INITIAL_BALANCE,
    SL_PERCENT,
    TP1_PERCENT,
    TP2_PERCENT,
    BREAK_EVEN_TRIGGER,
    TRAILING_PERCENT,
    PARTIAL_CLOSE_RATIO,
    RISK_SAFE,
    RISK_AGGRESSIVE,
    MAX_OPEN_POSITIONS
)

from app.learning import (
    save_learning,
    get_ai_learning_score
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

    try:

        df.to_csv(

            POSITIONS_PATH,

            index=False
        )

    except Exception as e:

        print(
            f"SAVE POSITION ERROR: {e}"
        )

# =========================
# LIVE PRICE
# =========================
def get_live_price(stock):

    try:

        df = yf.download(

            stock,

            period="1d",

            interval="1d",

            auto_adjust=True,

            progress=False
        )

        if df.empty:

            return 0

        close = df["Close"]

        if isinstance(
            close,
            pd.DataFrame
        ):

            close = close.iloc[:, 0]

        return float(
            close.iloc[-1]
        )

    except:

        return 0

# =========================
# CLOSED EQUITY
# =========================
def get_closed_equity():

    df = load_positions()

    if df.empty:

        return INITIAL_BALANCE

    try:

        closed = df[
            df["status"] == "CLOSED"
        ]

        pnl = closed["pnl"].sum()

        equity = (
            INITIAL_BALANCE + pnl
        )

        return round(
            max(equity, 0),
            0
        )

    except:

        return INITIAL_BALANCE

# =========================
# FLOATING PNL
# =========================
def get_floating_pnl():

    df = load_positions()

    if df.empty:

        return 0

    total = 0

    try:

        open_df = df[
            df["status"] == "OPEN"
        ]

        for _, row in open_df.iterrows():

            stock = row["stock"]

            side = row["side"]

            entry = float(
                row["entry"]
            )

            size = float(
                row["size"]
            )

            current = get_live_price(
                stock
            )

            if current <= 0:

                continue

            # =========================
            # BUY
            # =========================
            if side == "BUY":

                pnl = (
                    current - entry
                ) * size

            # =========================
            # SELL
            # =========================
            else:

                pnl = (
                    entry - current
                ) * size

            total += pnl

        return round(total, 0)

    except Exception as e:

        print(
            f"FLOATING ERROR: {e}"
        )

        return 0

# =========================
# LIVE EQUITY
# =========================
def get_live_equity():

    equity = (

        get_closed_equity()

        +

        get_floating_pnl()
    )

    return round(
        max(equity, 0),
        0
    )

# =========================
# POSITION SIZE
# =========================
def calculate_position_size(
    entry,
    aggressive=False
):

    equity = get_live_equity()

    ai_score = (
        get_ai_learning_score()
    )

    # =========================
    # AI BOOST
    # =========================
    if ai_score >= 70:

        aggressive = True

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

    if sl_distance <= 0:

        return 0

    # =========================
    # RAW SIZE
    # =========================
    size = (
        risk_amount /
        sl_distance
    )

    # =========================
    # MAX POSITION LIMIT
    # =========================
    max_position_value = (
        equity * 0.2
    )

    max_size = (
        max_position_value /
        entry
    )

    if size > max_size:

        size = max_size

    return round(size, 4)

# =========================
# OPEN POSITION
# =========================
def open_position(
    stock,
    side,
    entry
):

    try:

        df = load_positions()

        # =========================
        # MAX OPEN
        # =========================
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

        # =========================
        # SIZE
        # =========================
        size = calculate_position_size(

            entry,

            aggressive=True
        )

        if size <= 0:

            return

        # =========================
        # TP / SL
        # =========================
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
                0.0
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

        print(
            f"OPENED: "
            f"{stock} "
            f"{side}"
        )

    except Exception as e:

        print(
            f"OPEN ERROR: {e}"
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

            current_price = (
                latest_prices.get(
                    stock,
                    entry
                )
            )

            # =========================
            # BUY PNL
            # =========================
            if side == "BUY":

                pnl = (
                    current_price
                    -
                    entry
                ) * size

            else:

                pnl = (
                    entry
                    -
                    current_price
                ) * size

            # =========================
            # BREAK EVEN
            # =========================
            if (
                current_price
                >=
                entry
                *
                (
                    1
                    +
                    BREAK_EVEN_TRIGGER
                )
            ):

                df.at[idx, "sl"] = entry

            # =========================
            # TRAILING STOP
            # =========================
            trailing_sl = (

                current_price
                *
                (
                    1
                    -
                    TRAILING_PERCENT
                )
            )

            if trailing_sl > sl:

                df.at[idx, "sl"] = (
                    trailing_sl
                )

            # =========================
            # PARTIAL CLOSE
            # =========================
            if (

                current_price
                >=
                tp1

                and

                not partial
            ):

                df.at[idx, "size"] = (

                    size
                    *
                    (
                        1
                        -
                        PARTIAL_CLOSE_RATIO
                    )
                )

                df.at[idx, "partial"] = True

            # =========================
            # FULL CLOSE
            # =========================
            if (

                current_price
                >=
                tp2

                or

                current_price
                <=
                df.at[idx, "sl"]
            ):

                df.at[idx, "status"] = (
                    "CLOSED"
                )

                df.at[idx, "pnl"] = pnl

                # =========================
                # SAVE LEARNING
                # =========================
                save_learning({

                    "stock":
                        stock,

                    "side":
                        side,

                    "entry":
                        entry,

                    "exit":
                        current_price,

                    "pnl":
                        pnl,

                    "regime":
                        "LIVE",

                    "confidence":
                        0
                })

            # =========================
            # UPDATE PNL
            # =========================
            df.at[idx, "pnl"] = pnl

        except Exception as e:

            print(
                f"UPDATE ERROR: {e}"
            )

    save_positions(df)
