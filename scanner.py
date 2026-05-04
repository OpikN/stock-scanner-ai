import os
import requests

from core import *
from logger import save_log, get_stats
from portfolio import save_trade, calculate_pnl, get_equity, get_performance
from backtest import run_backtest


BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID   = os.getenv("CHAT_ID")


# ===== TELEGRAM =====
def send(msg):
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ BOT_TOKEN / CHAT_ID tidak terbaca")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


# ===== MAIN =====
def run():
    print("🚀 START SCANNER")

    # ===== MARKET CHECK =====
    ihsg = get_data(IHSG)
    if ihsg is None:
        send("❌ Gagal ambil data IHSG")
        return

    ihsg = compute(ihsg)
    market = get_market_regime(ihsg)

    print("MARKET:", market)

    results = []
    log_data = []
    trade_count = 0

    # ===== SCAN STOCK =====
    for s in STOCKS:
        print("SCAN:", s)

        df = get_data(s)
        if df is None:
            print("❌ DATA KOSONG:", s)
            continue

        df = compute(df)
        if df is None or df.empty:
            continue

        sig, price = signal(df)

        print("SIGNAL:", sig, "PRICE:", price)

        # ===== VALIDASI PRICE =====
        if price is None or price == 0:
            print("❌ PRICE INVALID:", s)
            continue

        # ===== FILTER MARKET =====
        if market == "BULL" and sig == "SELL":
            continue
        if market == "BEAR" and sig == "BUY":
            continue
        # SIDEWAYS tetap allow supaya ada data

        if sig == "HOLD":
            continue

        # ===== BACKTEST REAL =====
        exit_price, result = run_backtest(df, sig, price)

        if exit_price is None:
            print("❌ BACKTEST GAGAL:", s)
            continue

        lot = 1

        pnl = calculate_pnl(price, exit_price, sig, lot)

        # ===== SAVE TRADE =====
        trade_data = {
            "Stock": s,
            "Signal": sig,
            "Entry": round(float(price), 2),
            "Exit": round(float(exit_price), 2),
            "Lot": int(lot),
            "PnL": round(float(pnl), 2)
        }

        print("SAVE:", trade_data)

        save_trade(trade_data)

        results.append(
            f"{s} → {sig} @ {round(price,2)} | Exit {round(exit_price,2)} | PnL {round(pnl,2)}"
        )

        log_data.append({
            "Stock": s,
            "Signal": sig,
            "Entry": round(price, 2)
        })

        trade_count += 1

    # ===== FALLBACK (AGAR DASHBOARD TIDAK KOSONG) =====
    if trade_count == 0:
        print("⚠️ TIDAK ADA TRADE → BUAT DUMMY")

        dummy = {
            "Stock": "BBCA.JK",
            "Signal": "BUY",
            "Entry": 100,
            "Exit": 98,
            "Lot": 1,
            "PnL": -200
        }

        save_trade(dummy)

        send(f"⚠️ MARKET: {market}\nTidak ada sinyal, dummy dibuat")
        return

    # ===== SAVE LOG =====
    save_log(log_data)

    # ===== STATS =====
    stats = get_stats()
    equity = get_equity()
    perf = get_performance()

    # ===== TELEGRAM MESSAGE =====
    msg = f"📊 MARKET: {market}\n\n🔥 SIGNAL 🔥\n\n"
    msg += "\n".join(results)

    msg += f"\n\n📊 STATS:\n{stats}"
    msg += f"\n\n💰 EQUITY: {int(equity)}"
    msg += f"\n📈 PERFORMANCE:\n{perf}"

    send(msg)


if __name__ == "__main__":
    run()
