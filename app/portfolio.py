import pandas as pd
import os
import time

from app.config import (
    INITIAL_BALANCE,
    RISK_SAFE,
    RISK_AGGRESSIVE,
    TP1_PERCENT,
    TP2_PERCENT,
    BREAK_EVEN_TRIGGER,
    TRAILING_PERCENT,
    PARTIAL_CLOSE_RATIO
)

# =========================
# FILE
# =========================
POSITIONS_FILE = "data/positions.csv"

# =========================
# CREATE FILE
# =========================
def ensure_file():

    os.makedirs("data", exist_ok=True)

    if not os.path.exists(POSITIONS_FILE):

        df = pd.DataFrame(columns=[
            "time",
            "stock",
            "side",
            "entry",
            "size",
            "tp1",
            "tp2",
            "sl",
            "status",
            "partial",
            "exit_price",
            "pnl"
        ])

        df.to_csv(POSITIONS_FILE, index=False)

# =========================
# LOAD POSITIONS
# =========================
def load_positions():

    ensure_file()

    try:
        return pd.read_csv(POSITIONS_FILE)
    except:
        return pd.DataFrame()

# =========================
# SAVE POSITIONS
# =========================
def save_positions(df):

    ensure_file()

    df.to_csv(POSITIONS_FILE, index=False)

# =========================
# GET EQUITY
# =========================
def get_equity():

    df = load_positions()

    if df.empty:
        return INITIAL_BALANCE

    try:

        closed = df[df["status"] == "CLOSED"]

        if closed.empty:
            return INITIAL_BALANCE

        total_pnl = closed["pnl"].astype(float).sum()

        return round(INITIAL_BALANCE + total_pnl, 2)

    except:
        return INITIAL_BALANCE

# =========================
# POSITION SIZE
# =========================
def calculate_size(price, sl_percent, mode="SAFE"):

    equity = get_equity()

    if mode == "AGGRESSIVE":
        risk = equity * RISK_AGGRESSIVE
    else:
        risk = equity * RISK_SAFE

    sl_distance = price * sl_percent

    if sl_distance <= 0:
        return 0

    qty = risk / sl_distance

    return round(qty, 4)

# =========================
# OPEN POSITION
# =========================
def open_position(stock, side, entry, tp=None, sl=None, mode="SAFE"):

    df = load_positions()

    # =========================
    # AVOID DUPLICATE OPEN
    # =========================
    if not df.empty:

        active = df[
            (df["stock"] == stock) &
            (df["status"] == "OPEN")
        ]

        if len(active) > 0:
            print(f"SKIP DUPLICATE: {stock}")
            return False

    # =========================
    # TP SL
    # =========================
    tp1 = entry * (1 + TP1_PERCENT)
    tp2 = entry * (1 + TP2_PERCENT)

    if sl is None:
        sl = entry * 0.98

    # =========================
    # POSITION SIZE
    # =========================
    size = calculate_size(
        entry,
        abs(entry - sl) / entry,
        mode
    )

    # =========================
    # CREATE ROW
    # =========================
    row = {
        "time": time.time(),
        "stock": stock,
        "side": side,
        "entry": entry,
        "size": size,
        "tp1": tp1,
        "tp2": tp2,
        "sl": sl,
        "status": "OPEN",
        "partial": False,
        "exit_price": 0,
        "pnl": 0
    }

    df = pd.concat([
        df,
        pd.DataFrame([row])
    ], ignore_index=True)

    save_positions(df)

    print(f"OPEN POSITION: {stock} {side} {entry}")

    return True

# =========================
# CLOSE POSITION
# =========================
def close_position(df, idx, price):

    row = df.loc[idx]

    entry = float(row["entry"])
    size = float(row["size"])

    pnl = (price - entry) * size

    df.at[idx, "status"] = "CLOSED"
    df.at[idx, "exit_price"] = price
    df.at[idx, "pnl"] = round(pnl, 2)

    print(f"CLOSE: {row['stock']} PNL={pnl}")

# =========================
# UPDATE POSITIONS
# =========================
def update_positions(latest_prices):

    df = load_positions()

    if df.empty:
        return

    changed = False

    for idx, row in df.iterrows():

        try:

            if row["status"] != "OPEN":
                continue

            stock = row["stock"]

            if stock not in latest_prices:
                continue

            price = float(latest_prices[stock])

            entry = float(row["entry"])
            tp1 = float(row["tp1"])
            tp2 = float(row["tp2"])
            sl = float(row["sl"])

            partial = str(row["partial"]) == "True"

            # =========================
            # BREAK EVEN
            # =========================
            if price >= entry * (1 + BREAK_EVEN_TRIGGER):

                if sl < entry:

                    df.at[idx, "sl"] = entry

                    print(f"BREAK EVEN: {stock}")

                    changed = True

            # =========================
            # TRAILING STOP
            # =========================
            new_sl = price * (1 - TRAILING_PERCENT)

            if new_sl > sl:

                df.at[idx, "sl"] = round(new_sl, 2)

                print(f"TRAILING SL: {stock}")

                changed = True

            # =========================
            # PARTIAL CLOSE
            # =========================
            if price >= tp1 and not partial:

                size = float(row["size"])

                remaining = size * (1 - PARTIAL_CLOSE_RATIO)

                df.at[idx, "size"] = remaining
                df.at[idx, "partial"] = True

                print(f"PARTIAL CLOSE: {stock}")

                changed = True

            # =========================
            # FINAL TP
            # =========================
            if price >= tp2:

                close_position(df, idx, price)

                changed = True

                continue

            # =========================
            # STOP LOSS
            # =========================
            current_sl = float(df.loc[idx, "sl"])

            if price <= current_sl:

                close_position(df, idx, price)

                changed = True

        except Exception as e:

            print(f"UPDATE ERROR: {e}")

    # =========================
    # SAVE
    # =========================
    if changed:

        save_positions(df)
