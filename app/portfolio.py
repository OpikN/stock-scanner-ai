import os
import pandas as pd
from datetime import datetime

from app.config import (
    INITIAL_BALANCE,
    RISK_PERCENT,
    MAX_LOT,
    BREAK_EVEN_RR,
    TRAILING_START_RR,
    TRAILING_STEP,
)

POSITIONS_PATH = "data/positions.csv"


# =========================
# LOAD & SAVE
# =========================
def _load():
    if os.path.exists(POSITIONS_PATH):
        try:
            return pd.read_csv(POSITIONS_PATH)
        except:
            return pd.DataFrame()
    return pd.DataFrame(columns=[
        "time","stock","side","entry","tp","sl","qty",
        "status","exit_price","exit_time","pnl"
    ])


def _save(df):
    os.makedirs("data", exist_ok=True)
    df.to_csv(POSITIONS_PATH, index=False)


# =========================
# EQUITY
# =========================
def get_equity():
    df = _load()

    if df.empty:
        return INITIAL_BALANCE

    closed = df[df["status"] == "CLOSED"]

    if closed.empty:
        return INITIAL_BALANCE

    return INITIAL_BALANCE + closed["pnl"].sum()


# =========================
# LOT CALCULATION
# =========================
def calculate_lot(entry, sl):
    equity = get_equity()
    risk_amount = equity * RISK_PERCENT
    risk_per_unit = abs(entry - sl)

    if risk_per_unit == 0:
        return 0

    qty = risk_amount / risk_per_unit
    return min(int(qty), MAX_LOT)


# =========================
# OPEN POSITION
# =========================
def open_position(stock, side, entry, tp, sl):
    df = _load()

    # hindari posisi dobel
    if not df[(df["stock"] == stock) & (df["status"] == "OPEN")].empty:
        return

    qty = calculate_lot(entry, sl)

    new = {
        "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "stock": stock,
        "side": side,
        "entry": round(entry, 2),
        "tp": round(tp, 2),
        "sl": round(sl, 2),
        "qty": qty,
        "status": "OPEN",
        "exit_price": "",
        "exit_time": "",
        "pnl": 0
    }

    df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
    _save(df)


# =========================
# UPDATE POSITIONS (TP / SL / BE / TRAILING)
# =========================
def update_positions(latest_price_map):
    df = _load()

    if df.empty:
        return

    updated = False

    for i, row in df.iterrows():
        if row["status"] != "OPEN":
            continue

        stock = row["stock"]

        if stock not in latest_price_map:
            continue

        price = latest_price_map[stock]
        side = row["side"]

        entry = float(row["entry"])
        tp = float(row["tp"])
        sl = float(row["sl"])
        qty = float(row["qty"])

        risk = abs(entry - sl)
        if risk == 0:
            continue

        # =========================
        # CLOSE TP / SL
        # =========================
        hit_tp = (side == "BUY" and price >= tp) or (side == "SELL" and price <= tp)
        hit_sl = (side == "BUY" and price <= sl) or (side == "SELL" and price >= sl)

        if hit_tp or hit_sl:
            exit_price = price

            pnl = (exit_price - entry) * qty if side == "BUY" else (entry - exit_price) * qty

            df.at[i, "status"] = "CLOSED"
            df.at[i, "exit_price"] = round(exit_price, 2)
            df.at[i, "exit_time"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            df.at[i, "pnl"] = round(pnl, 2)

            updated = True
            continue

        # =========================
        # RR CALCULATION
        # =========================
        rr = (price - entry) / risk if side == "BUY" else (entry - price) / risk

        # =========================
        # BREAK EVEN
        # =========================
        if rr >= BREAK_EVEN_RR:
            if side == "BUY" and sl < entry:
                df.at[i, "sl"] = entry
                updated = True

            elif side == "SELL" and sl > entry:
                df.at[i, "sl"] = entry
                updated = True

        # =========================
        # TRAILING STOP
        # =========================
        if rr >= TRAILING_START_RR:
            if side == "BUY":
                new_sl = price - (risk * TRAILING_STEP)
                if new_sl > sl:
                    df.at[i, "sl"] = round(new_sl, 2)
                    updated = True
            else:
                new_sl = price + (risk * TRAILING_STEP)
                if new_sl < sl:
                    df.at[i, "sl"] = round(new_sl, 2)
                    updated = True

    if updated:
        _save(df)


# =========================
# STATS
# =========================
def get_stats():
    df = _load()

    if df.empty:
        return {"trades": 0, "winrate": 0, "total_pnl": 0, "equity": INITIAL_BALANCE}

    closed = df[df["status"] == "CLOSED"]

    if closed.empty:
        return {"trades": 0, "winrate": 0, "total_pnl": 0, "equity": INITIAL_BALANCE}

    wins = closed[closed["pnl"] > 0]

    winrate = (len(wins) / len(closed)) * 100
    total_pnl = closed["pnl"].sum()
    equity = INITIAL_BALANCE + total_pnl

    return {
        "trades": len(closed),
        "winrate": round(winrate, 2),
        "total_pnl": round(total_pnl, 2),
        "equity": round(equity, 2)
    }
