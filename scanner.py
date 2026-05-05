import os
import requests
import traceback

from core import *
from logger import save_log, get_stats
from portfolio import (
    save_trade,
    calculate_pnl,
    get_equity,
    get_performance,
    get_expectancy,
    load_trades
)


def send(msg):
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    CHAT_ID   = os.getenv("CHAT_ID")

    if not BOT_TOKEN or not CHAT_ID:
        print("❌ ENV NOT FOUND")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    try:
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": msg
        })
    except Exception as e:
        print("ERROR TELEGRAM:", e)


# =========================
# 🔥 SMART RISK + COMPOUNDING
# =========================
def get_dynamic_risk(trades):
    base = 0.02

    if len(trades) < 5:
        return base

    last = trades[-5:]
    wins = sum(1 for t in last if float(t["PnL"]) > 0)
    losses = sum(1 for t in last if float(t["PnL"]) < 0)

    if wins >= 3:
        return 0.03
    if losses >= 3:
        return 0.01

    return base


def run():
    equity = get_equity()
    trades = load_trades()

    if equity <= 0:
        send("❌ SYSTEM STOP - Equity habis")
        return

    risk_pct = get_dynamic_risk(trades)

    ihsg = compute(get_data(IHSG))
    market = get_market_regime(ihsg)

    candidates = []

    for s in STOCKS:
        df = compute(get_data(s))
        if df is None:
            continue

        sig, price = signal(df)
        if sig == "HOLD":
            continue

        r = df.iloc[-1]
        prev = df.iloc[-2]

        # =========================
        # 🔥 FILTER
        # =========================
        if r["adx"] < 15:
            continue

        if abs(r["ema20"] - r["ema50"]) / r["ema50"] < 0.001:
            continue

        # =========================
        # 🔥 PULLBACK
        # =========================
        if sig == "SELL":
            if price > r["ema20"]:
                continue
            if (r["ema20"] - price) / r["ema20"] > 0.03:
                continue

        elif sig == "BUY":
            if price < r["ema20"]:
                continue
            if (price - r["ema20"]) / r["ema20"] > 0.03:
                continue

        # =========================
        # 🔥 RSI + CANDLE
        # =========================
        if sig == "SELL":
            if not (prev["rsi"] > r["rsi"] and 40 < r["rsi"] < 60):
                continue
            if r["Close"] >= r["Open"]:
                continue

        elif sig == "BUY":
            if not (prev["rsi"] < r["rsi"] and 40 < r["rsi"] < 60):
                continue
            if r["Close"] <= r["Open"]:
                continue

        # =========================
        # 🔥 RR 1:2
        # =========================
        if sig == "SELL":
            sl = price * 1.02
            tp = price * 0.96
        else:
            sl = price * 0.98
            tp = price * 1.04

        score = int(r["adx"] / 10)

        if market == "BEAR" and sig == "SELL":
            score += 3
        elif market == "BULL" and sig == "BUY":
            score += 3

        candidates.append({
            "stock": s,
            "signal": sig,
            "price": price,
            "sl": sl,
            "tp": tp,
            "score": score
        })

    # =========================
    # 🔥 ADAPTIVE FALLBACK
    # =========================
    if not candidates:
        send(f"📊 MARKET: {market}\n\n⚠️ Tidak ada sinyal berkualitas hari ini\n\n💰 EQUITY: {int(equity)}")
        return

    candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)[:2]

    results = []
    log_data = []

    for trade in candidates:
        s = trade["stock"]
        sig = trade["signal"]
        price = trade["price"]
        sl = trade["sl"]
        tp = trade["tp"]

        risk_amount = equity * risk_pct
        lot = int(risk_amount / abs(price - sl))

        if lot > 20:
            lot = 20
        if lot < 1:
            lot = 1

        exit_price = tp
        pnl = calculate_pnl(price, exit_price, sig, lot)

        trade_data = {
            "Stock": s,
            "Signal": sig,
            "Entry": round(price, 2),
            "Exit": round(exit_price, 2),
            "Lot": lot,
            "PnL": round(pnl, 2)
        }

        save_trade(trade_data)

        # =========================
        # 🔥 MONITORING LOG
        # =========================
        print(f"[LOG] {s} | {sig} | Entry {price} | TP {tp} | SL {sl} | Lot {lot} | PnL {pnl}")

        results.append(
            f"{s} → {sig} @ {round(price,2)} | TP {round(tp,2)} | SL {round(sl,2)} | Lot {lot} | PnL {round(pnl,2)}"
        )

        log_data.append({
            "Stock": s,
            "Signal": sig,
            "Entry": round(price, 2)
        })

    save_log(log_data)

    stats = get_stats()
    equity = get_equity()
    perf = get_performance()
    exp = get_expectancy(load_trades(), last_n=20)

    msg = f"📊 MARKET: {market}\n\n🔥 ADAPTIVE MULTI TRADE 🔥\n\n"
    msg += "\n".join(results)
    msg += f"\n\n📊 STATS:\n{stats}"
    msg += f"\n\n💰 EQUITY: {int(equity)}"
    msg += f"\n📈 PERFORMANCE:\n{perf}"
    msg += f"\n📊 EXPECTANCY: {exp}"

    # =========================
    # 🔥 RISK MODE INFO
    # =========================
    msg += f"\n⚙️ RISK MODE: {risk_pct*100}%"

    send(msg)


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print("ERROR:", e)
        print(traceback.format_exc())
        send(f"❌ ERROR:\n{e}")
