import pandas as pd
import os

from app.config import (
    INITIAL_BALANCE,
    RISK_SAFE,
    RISK_AGGRESSIVE,
    SL_PERCENT,
    TP_PERCENT,
    TP1_PERCENT,
    TP2_PERCENT,
    BREAK_EVEN_TRIGGER,
    TRAILING_PERCENT,
    PARTIAL_CLOSE_RATIO
)

from app.adaptive import load_state

POSITIONS_PATH = "data/positions.csv"


# =========================
# LOAD / SAVE
# =========================
def load_positions():
    if os.path.exists(POSITIONS_PATH):
        try:
            return pd.read_csv(POSITIONS_PATH)
        except:
            return pd.DataFrame()
    return pd.DataFrame()


def save_positions(df):
    df.to_csv(POSITIONS_PATH, index=False)


# =========================
# EQUITY
# =========================
def get_equity():
    df = load_positions()

    if df.empty:
        return INITIAL_BALANCE

    closed = df[df["status"] == "CLOSED"]

    if closed.empty:
        return INITIAL_BALANCE

    pnl = closed["pnl"].sum()
    return INITIAL_BALANCE + pnl


# =========================
# POSITION SIZE
# =========================
def calculate_position(entry_price):
    state = load_state()
    mode = state.get("mode", "SAFE")

    equity = get_equity()

    risk_pct = RISK_AGGRESSIVE if mode == "AGGRESSIVE" else RISK_SAFE

    risk_amount = equity * risk_pct

    sl_price = entry_price * (1 - SL_PERCENT)

    risk_per_share = abs(entry_price - sl_price)

    if risk_per_share <= 0:
        return 0, sl_price

    qty = int(risk_amount / risk_per_share)

    return qty, sl_price


# =========================
# OPEN POSITION
# =========================
def open_position(symbol, signal, price):
    df = load_positions()

    qty, sl = calculate_position(price)

    if qty <= 0:
        return

    tp = price * (1 + TP_PERCENT) if signal == "BUY" else price * (1 - TP_PERCENT)

    trade = {
        "stock": symbol,
        "signal": signal,
        "entry": price,
        "sl": sl,
        "tp": tp,
        "qty": qty,
        "status": "OPEN",
        "pnl": 0,
        "partial_done": False
    }

    df = pd.concat([df, pd.DataFrame([trade])], ignore_index=True)
    save_positions(df)


# =========================
# UPDATE POSITIONS 🔥
# =========================
def update_positions(price_map):
    df = load_positions()

    if df.empty:
        return

    for i, row in df.iterrows():
        if row["status"] != "OPEN":
            continue

        symbol = row["stock"]
        if symbol not in price_map:
            continue

        price = price_map[symbol]

        entry = row["entry"]
        sl = row["sl"]
        qty = row["qty"]

        # =========================
        # BUY LOGIC
        # =========================
        if row["signal"] == "BUY":

            tp1 = entry * (1 + TP1_PERCENT)
            tp2 = entry * (1 + TP2_PERCENT)

            # STOP LOSS
            if price <= sl:
                pnl = (sl - entry) * qty
                df.at[i, "status"] = "CLOSED"
                df.at[i, "pnl"] += pnl
                continue

            # PARTIAL CLOSE
            if price >= tp1 and not bool(row.get("partial_done", False)):
                close_qty = int(qty * PARTIAL_CLOSE_RATIO)
                pnl = (price - entry) * close_qty

                df.at[i, "qty"] = qty - close_qty
                df.at[i, "pnl"] += pnl
                df.at[i, "partial_done"] = True

            # BREAK EVEN
            if price >= entry * (1 + BREAK_EVEN_TRIGGER):
                df.at[i, "sl"] = entry

            # TRAILING STOP
            new_sl = price * (1 - TRAILING_PERCENT)
            if new_sl > df.at[i, "sl"]:
                df.at[i, "sl"] = new_sl

            # FINAL TP
            if price >= tp2:
                pnl = (price - entry) * df.at[i, "qty"]
                df.at[i, "status"] = "CLOSED"
                df.at[i, "pnl"] += pnl

        # =========================
        # SELL LOGIC
        # =========================
        elif row["signal"] == "SELL":

            tp1 = entry * (1 - TP1_PERCENT)
            tp2 = entry * (1 - TP2_PERCENT)

            # STOP LOSS
            if price >= sl:
                pnl = (entry - sl) * qty
                df.at[i, "status"] = "CLOSED"
                df.at[i, "pnl"] += pnl
                continue

            # PARTIAL CLOSE
            if price <= tp1 and not bool(row.get("partial_done", False)):
                close_qty = int(qty * PARTIAL_CLOSE_RATIO)
                pnl = (entry - price) * close_qty

                df.at[i, "qty"] = qty - close_qty
                df.at[i, "pnl"] += pnl
                df.at[i, "partial_done"] = True

            # BREAK EVEN
            if price <= entry * (1 - BREAK_EVEN_TRIGGER):
                df.at[i, "sl"] = entry

            # TRAILING STOP
            new_sl = price * (1 + TRAILING_PERCENT)
            if new_sl < df.at[i, "sl"]:
                df.at[i, "sl"] = new_sl

            # FINAL TP
            if price <= tp2:
                pnl = (entry - price) * df.at[i, "qty"]
                df.at[i, "status"] = "CLOSED"
                df.at[i, "pnl"] += pnl

    save_positions(df)
