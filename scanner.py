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
        print("❌ BOT_TOKEN / CHAT_ID tidak terbaca")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


def run():
    print("🚀 START SCANNER")

    equity = get_equity()

    # 🔥 STOP SYSTEM kalau equity habis
    if equity <= 0:
        send("❌ SYSTEM STOP - Equity habis")
        return

    ihsg = compute(get_data(IHSG))
    market = get_market_regime(ihsg)

    results = []
    log_data = []
    trade_count = 0

    for s in STOCKS:
        df = compute(get_data(s))
        if df is None or df.empty:
            continue

        sig, price = signal(df)

        if sig == "HOLD" or price is None:
            continue

        strategy = choose_strategy(df)

        if market == "BULL" and sig == "SELL":
            continue
        if market == "BEAR" and sig == "BUY":
            continue

        exit_price, result = run_backtest(df, sig, price)
        if exit_price is None:
            continue

        # ===== SAFE RISK =====
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
            f"{s} [{strategy}] → {sig} @ {round(price,2)} | Exit {round(exit_price,2)} | Lot {lot} | PnL {round(pnl,2)}"
        )

        log_data.append({
            "Stock": s,
            "Signal": sig,
            "Entry": round(price, 2)
        })

        trade_count += 1

    if trade_count == 0:
        send(f"⚠️ MARKET: {market}\nTidak ada sinyal hari ini")
        return

    save_log(log_data)

    stats = get_stats()
    equity = get_equity()
    perf = get_performance()

    trades = load_trades()
    exp = get_expectancy(trades)

    msg = f"📊 MARKET: {market}\n\n🔥 SIGNAL 🔥\n\n"
    msg += "\n".join(results)
    msg += f"\n\n📊 STATS:\n{stats}"
    msg += f"\n\n💰 EQUITY: {int(equity)}"
    msg += f"\n📈 PERFORMANCE:\n{perf}"
    msg += f"\n📊 EXPECTANCY: {exp}"

    send(msg)


if __name__ == "__main__":
    run()
