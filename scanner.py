import os
import requests

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
        r = requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": msg
        })
        print("STATUS:", r.status_code)
        print("RESP:", r.text)

    except Exception as e:
        print("ERROR TELEGRAM:", e)


def run():
    equity = get_equity()

    if equity <= 0:
        send("❌ SYSTEM STOP - Equity habis")
        return

    ihsg = compute(get_data(IHSG))
    market = get_market_regime(ihsg)

    best_trade = None
    best_score = -999

    results = []
    log_data = []

    for s in STOCKS:
        df = compute(get_data(s))
        if df is None:
            continue

        sig, price = signal(df)

        if sig == "HOLD":
            continue

        r = df.iloc[-1]

        # =========================
        # 🔥 FILTER
        # =========================
        if r["adx"] < 15:
            continue

        distance = abs(price - r["ema20"]) / price
        if distance < 0.005:
            continue

        # =========================
        # 🔥 SCORING
        # =========================
        score = 0

        if market == "BEAR" and sig == "SELL":
            score += 3
        elif market == "BULL" and sig == "BUY":
            score += 3
        else:
            score += 1

        score += int(r["adx"] / 10)

        # =========================
        # 🔥 RISK MANAGEMENT (RR 1:2)
        # =========================
        risk_pct = 0.02
        reward_pct = 0.04

        if sig == "SELL":
            sl = price * (1 + risk_pct)
            tp = price * (1 - reward_pct)
        else:
            sl = price * (1 - risk_pct)
            tp = price * (1 + reward_pct)

        # =========================
        # 🔥 SELECT BEST
        # =========================
        if score > best_score:
            best_score = score
            best_trade = {
                "stock": s,
                "signal": sig,
                "price": price,
                "sl": sl,
                "tp": tp
            }

    # =========================
    # ❌ NO SIGNAL
    # =========================
    if best_trade is None:
        msg = f"📊 MARKET: {market}\n\n⚠️ Tidak ada sinyal hari ini\n\n💰 EQUITY: {int(equity)}"
        send(msg)
        return

    # =========================
    # 💰 EXECUTE TRADE
    # =========================
    s = best_trade["stock"]
    sig = best_trade["signal"]
    price = best_trade["price"]
    sl = best_trade["sl"]
    tp = best_trade["tp"]

    # 🔥 POSITION SIZING (REALISTIC)
    risk_amount = equity * 0.02
    lot = int(risk_amount / abs(price - sl))

    # BATAS LOT BIAR TIDAK NGACO
    max_lot = 20

    if lot > max_lot:
        lot = max_lot

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

    results.append(
        f"{s} → {sig} @ {round(price,2)} | TP {round(tp,2)} | SL {round(sl,2)} | Lot {lot} | PnL {round(pnl,2)} | Score {best_score}"
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
    exp = get_expectancy(load_trades())

    msg = f"📊 MARKET: {market}\n\n🔥 BEST TRADE 🔥\n\n"
    msg += "\n".join(results)
    msg += f"\n\n📊 STATS:\n{stats}"
    msg += f"\n\n💰 EQUITY: {int(equity)}"
    msg += f"\n📈 PERFORMANCE:\n{perf}"
    msg += f"\n📊 EXPECTANCY: {exp}"

    send(msg)


if __name__ == "__main__":
    run()
