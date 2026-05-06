import pandas as pd
import os
from app.config import INITIAL_BALANCE, RISK_SAFE, RISK_AGGRESSIVE, SL_PERCENT, TP_PERCENT
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
# POSITION SIZE 🔥
# =========================
def calculate_position(entry_price):
    state = load_state()
    mode = state.get("mode", "SAFE")

    equity = get_equity()

    if mode == "AGGRESSIVE":
        risk_pct = RISK_AGGRESSIVE
    else:
        risk_pct = RISK_SAFE

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
        "pnl": 0
    }

    df = pd.concat([df, pd.DataFrame([trade])], ignore_index=True)
    save_positions(df)


# =========================
# UPDATE POSITIONS (TP/SL HIT)
# =========================
def update_positions(df_price):
    df = load_positions()

    if df.empty:
        return

    for i, row in df.iterrows():
        if row["status"] != "OPEN":
            continue

        symbol = row["stock"]

        if symbol not in df_price:
            continue

        price = df_price[symbol]

        entry = row["entry"]
        sl = row["sl"]
        tp = row["tp"]
        qty = row["qty"]

        # BUY
        if row["signal"] == "BUY":
            if price <= sl:
                pnl = (sl - entry) * qty
                df.at[i, "status"] = "CLOSED"
                df.at[i, "pnl"] = pnl

            elif price >= tp:
                pnl = (tp - entry) * qty
                df.at[i, "status"] = "CLOSED"
                df.at[i, "pnl"] = pnl

        # SELL
        elif row["signal"] == "SELL":
            if price >= sl:
                pnl = (entry - sl) * qty
                df.at[i, "status"] = "CLOSED"
                df.at[i, "pnl"] = pnl

            elif price <= tp:
                pnl = (entry - tp) * qty
                df.at[i, "status"] = "CLOSED"
                df.at[i, "pnl"] = pnl

    save_positions(df)
