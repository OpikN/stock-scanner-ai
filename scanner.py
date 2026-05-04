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
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": msg
        })
    except:
        pass


# =========================
# 🔥 AUTO RISK SCALING
# =========================
def get_dynamic_risk(trades):
    if len(trades) < 3:
        return 0.02

    last = trades[-3:]

    loss_count = sum(1 for t in last if float(t["PnL"]) < 0)

    if loss_count >= 2:
        return 0.01  # turun risk

    return 0.02


# =========================
# 🔥 TRAILING STOP SIMULATION
# =========================
def simulate_trailing(df, signal, entry):
    trail_pct = 0.02

    best_price = entry
    stop = entry

    for i in range(-10, 0):
        price = df.iloc[i]["Close"]

        if signal == "BUY":
            if price > best_price:
                best_price = price
                stop = best_price * (1 - trail_pct)

            if price <= stop:
                return stop

        elif signal == "SELL":
            if price < best_price:
                best_price = price
                stop = best_price * (1 + trail_pct)

            if price >= stop:
                return stop

    return df.iloc[-1]["Close"]


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

        if r["adx"] < 15:
            continue

        score = int(r["adx"] / 10)

        if market == "BEAR" and sig == "SELL":
            score += 3
        elif market == "BULL" and sig == "BUY":
            score += 3

        # RR BASE
        if sig == "SELL":
            sl = price * (1 + risk_pct)
        else:
            sl = price * (1 - risk_pct)

        candidates.append({
            "stock": s,
            "signal": sig,
            "price": price,
            "sl": sl,
            "score": score,
            "df": df
        })

    # =========================
    # 🔥 PILIH TOP 2 TRADE
    # =========================
    candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)[:2]

    if not candidates:
        send(f"📊 MARKET: {market}\n\n⚠️ Tidak ada sinyal hari ini\n\n💰 EQUITY: {int(equity)}")
        return

    results = []

    for trade in candidates:
        s = trade["stock"]
        sig = trade["signal"]
        price = trade["price"]
        sl = trade["sl"]
        df = trade["df"]

        # =========================
        # 🔥 LOT (SAFE)
        # =========================
        risk_amount = equity * risk_pct
        lot = int(risk_amount / abs(price - sl))

        if lot > 20:
            lot = 20
        if lot < 1:
            lot = 1

        # =========================
        # 🔥 TRAILING EXIT
        # =========================
        exit_price = simulate_trailing(df, sig, price)

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
            f"{s} → {sig} @ {round(price,2)} | Exit {round(exit_price,2)} | Lot {lot} | PnL {round(pnl,2)}"
        )

    save_log([{"Stock": r.split()[0]} for r in results])

    stats = get_stats()
    equity = get_equity()
    perf = get_performance()
    exp = get_expectancy(load_trades(), last_n=20)

    msg = f"📊 MARKET: {market}\n\n🔥 MULTI TRADE 🔥\n\n"
    msg += "\n".join(results)
    msg += f"\n\n📊 STATS:\n{stats}"
    msg += f"\n\n💰 EQUITY: {int(equity)}"
    msg += f"\n📈 PERFORMANCE:\n{perf}"
    msg += f"\n📊 EXPECTANCY: {exp}"

    send(msg)


if __name__ == "__main__":
    run()
