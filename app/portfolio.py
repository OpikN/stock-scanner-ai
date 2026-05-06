import os
import pandas as pd
from datetime import datetime

from app.config import INITIAL_BALANCE, RISK_PERCENT, MAX_LOT

POSITIONS_PATH = "data/positions.csv"


def _load():
    if os.path.exists(POSITIONS_PATH):
        return pd.read_csv(POSITIONS_PATH)
    return pd.DataFrame(columns=[
        "time","stock","side","entry","tp","sl","qty",
        "status","exit_price","exit_time","pnl"
    ])


def _save(df):
    os.makedirs("data", exist_ok=True)
    df.to_csv(POSITIONS_PATH, index=False)


def get_equity():
    df = _load()

    if df.empty:
        return INITIAL_BALANCE

    closed = df[df.status == "CLOSED"]

    if closed.empty:
        return INITIAL_BALANCE

    total_pnl = closed.pnl.sum()
    return INITIAL_BALANCE + total_pnl


def calculate_lot(entry, sl):
    equity = get_equity()

    risk_amount = equity * RISK_PERCENT
    risk_per_unit = abs(entry - sl)

    if risk_per_unit == 0:
        return 0

    qty = risk_amount / risk_per_unit

    return min(int(qty), MAX_LOT)


def open_position(stock, side, entry, tp, sl):
    df = _load()

    # hindari dobel posisi
    if not df[(df.stock == stock) & (df.status == "OPEN")].empty:
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

    if updated:
        _save(df)


def get_stats():
    df = _load()

    if df.empty:
        return {"trades": 0, "winrate": 0, "total_pnl": 0, "equity": INITIAL_BALANCE}

    closed = df[df.status == "CLOSED"]

    if closed.empty:
        return {"trades": 0, "winrate": 0, "total_pnl": 0, "equity": INITIAL_BALANCE}

    wins = closed[closed.pnl > 0]

    winrate = (len(wins) / len(closed)) * 100
    total_pnl = closed.pnl.sum()
    equity = INITIAL_BALANCE + total_pnl

    return {
        "trades": len(closed),
        "winrate": round(winrate, 2),
        "total_pnl": round(total_pnl, 2),
        "equity": round(equity, 2)
    }
