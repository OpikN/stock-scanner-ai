import os
import requests

from core import *
from ai_strategy import choose_strategy
from logger import save_log, get_stats
from portfolio import (
    save_trade,
    calculate_pnl,
    get_equity,
    get_performance,
    calculate_lot,
    get_expectancy,
    load_trades
)
from backtest import run_backtest


BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID   = os.getenv("CHAT_ID")


def send(msg):
    if not BOT_TOKEN or not CHAT_ID:
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


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
        # 🔥 QUALITY FILTER
        # =========================
        if r["adx"] < 20:
            continue

        distance = abs(price - r["ema20"]) / price
        if distance < 0.01:
            continue

        # =========================
        # 🔥 SCORING SYSTEM
        # =========================
        score = 0

        if market == "BEAR" and sig == "SELL":
            score += 3
        elif market == "BULL" and sig == "BUY":
            score += 3
        else:
            score += 1

        # tambahan nilai dari ADX (trend strength)
        score += int(r["adx"] / 10)

        if score > best_score:
            exit_price, _ = run_backtest(df, sig, price)
            if exit_price is None:
                continue

            best_score = score

            best_trade = {
                "stock": s,
                "signal": sig,
                "price": price,
                "exit": exit_price,
                "adx": r["adx"]
            }

    # =========================
    # 🚫 NO TRADE
    # =========================
    if best_trade is None:
        send(f"⚠️ MARKET: {market}\nTidak ada sinyal berkualitas hari ini")
        return

    # =========================
    # 💰 EXECUTE BEST TRADE
    # =========================
    s = best_trade["stock"]
    sig = best_trade["signal"]
    price = best_trade["price"]
    exit_price = best_trade["exit"]

    sl = price * (1.03 if sig == "SELL" else 0.97)
    lot = calculate_lot(price, sl, equity)

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
        f"{s} → {sig} @ {round(price,2)} | Exit {round(exit_price,2)} | Lot {lot} | PnL {round(pnl,2)} | Score {best_score}"
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
