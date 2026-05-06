import pandas as pd
import os
import time
from app.config import (
    INITIAL_BALANCE,
    RISK_SAFE,
    RISK_AGGRESSIVE,
    SL_PERCENT,
    TP1_PERCENT,
    TP2_PERCENT,
    BREAK_EVEN_TRIGGER,
    TRAILING_PERCENT,
    PARTIAL_CLOSE_RATIO,
    MAX_OPEN_POSITIONS,
    MIN_TRADE_SIZE
)

DATA_PATH = "data/positions.csv"


# =========================
# LOAD / SAVE
# =========================
def load_positions():
    if os.path.exists(DATA_PATH):
        try:
            return pd.read_csv(DATA_PATH)
        except:
            return pd.DataFrame()
    return pd.DataFrame()


def save_positions(df):
    os.makedirs("data", exist_ok=True)
    df.to_csv(DATA_PATH, index=False)


# =========================
# EQUITY (COMPOUNDING 🔥)
# =========================
def get_equity():
    df = load_positions()

    if df.empty or "pnl" not in df.columns:
        return INITIAL_BALANCE

    return INITIAL_BALANCE + df["pnl"].sum()


# =========================
# POSITION SIZING 🔥
# =========================
def calculate_size(price, mode="SAFE"):
    equity = get_equity()

    risk_pct = RISK_SAFE if mode == "SAFE" else RISK_AGGRESSIVE

    risk_amount = equity * risk_pct

    size = risk_amount / (price * SL_PERCENT)

    size_value = size * price

    if size_value < MIN_TRADE_SIZE:
        size = MIN_TRADE_SIZE / price

    return round(size, 4)


# =========================
# OPEN POSITION
# =========================
def open_position(stock, side, price, tp, sl, mode="SAFE"):
    df = load_positions()

    # limit posisi
    open_count = len(df[df["status"] == "OPEN"]) if not df.empty else 0
    if open_count >= MAX_OPEN_POSITIONS:
        return False

    # hindari duplicate
    if not df.empty:
        if ((df["stock"] == stock) & (df["status"] == "OPEN")).any():
            return False

    size = calculate_size(price, mode)

    new = {
        "time": time.time(),
        "stock": stock,
        "side": side,
        "entry": price,
        "size": size,
        "tp1": price * (1 + TP1_PERCENT) if side == "BUY" else price * (1 - TP1_PERCENT),
        "tp2": price * (1 + TP2_PERCENT) if side == "BUY" else price * (1 - TP2_PERCENT),
        "sl": price * (1 - SL_PERCENT) if side == "BUY" else price * (1 + SL_PERCENT),
        "status": "OPEN",
        "partial": False,
        "pnl": 0
    }

    df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
    save_positions(df)

    return True


# =========================
# UPDATE POSITIONS 🔥
# =========================
def update_positions(latest_prices):
    df = load_positions()

    if df.empty:
        return

    for i in range(len(df)):
        row = df.iloc[i]

        if row["status"] != "OPEN":
            continue

        stock = row["stock"]
        price = latest_prices.get(stock)

        if not price:
            continue

        entry = row["entry"]
        size = row["size"]
        side = row["side"]

        pnl = (price - entry) * size if side == "BUY" else (entry - price) * size

        df.at[i, "pnl"] = pnl

        # =========================
        # PARTIAL CLOSE (TP1)
        # =========================
        if not row["partial"]:
            if (side == "BUY" and price >= row["tp1"]) or (side == "SELL" and price <= row["tp1"]):
                df.at[i, "size"] = size * (1 - PARTIAL_CLOSE_RATIO)
                df.at[i, "partial"] = True

        # =========================
        # BREAK EVEN
        # =========================
        if row["partial"]:
            if (side == "BUY" and price > entry * (1 + BREAK_EVEN_TRIGGER)) or \
               (side == "SELL" and price < entry * (1 - BREAK_EVEN_TRIGGER)):
                df.at[i, "sl"] = entry

        # =========================
        # TRAILING STOP
        # =========================
        if side == "BUY":
            new_sl = price * (1 - TRAILING_PERCENT)
            if new_sl > row["sl"]:
                df.at[i, "sl"] = new_sl
        else:
            new_sl = price * (1 + TRAILING_PERCENT)
            if new_sl < row["sl"]:
                df.at[i, "sl"] = new_sl

        # =========================
        # CLOSE POSITION
        # =========================
        if (side == "BUY" and (price <= df.at[i, "sl"] or price >= row["tp2"])) or \
           (side == "SELL" and (price >= df.at[i, "sl"] or price <= row["tp2"])):

            df.at[i, "status"] = "CLOSED"

    save_positions(df)
