import os
import requests
from core import *
from logger import save_log, get_stats
from portfolio import save_trade, calculate_pnl, get_equity, get_performance

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID   = os.getenv("CHAT_ID")


def send(msg):
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Secret tidak terbaca")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


def run():
    # ===== MARKET CHECK =====
    ihsg = get_data(IHSG)
    if ihsg is None:
        send("❌ Gagal ambil data IHSG")
        return

    ihsg = compute(ihsg)
    market = get_market_regime(ihsg)

    results = []
    log_data = []
    trade_count = 0

    # ===== SCAN STOCK =====
    for s in STOCKS:
        df = get_data(s)
        if df is None:
            continue

        df = compute(df)
        sig, price = signal(df)

        # ===== FILTER MARKET =====
        if market == "BULL" and sig == "SELL":
            continue
        if market == "BEAR" and sig == "BUY":
            continue
        if market == "SIDEWAYS":
            continue

        results.append(f"{s} → {sig} @ {round(price,2)}")

        log_data.append({
            "Stock": s,
            "Signal": sig,
            "Entry": round(price,2)
        })

        # ===== SIMULASI TRADE =====
        lot = 1

        # exit dummy (biar selalu ada PnL)
        exit_price = price * (1.02 if sig == "BUY" else 0.98)

        pnl = calculate_pnl(price, exit_price, sig, lot)

        save_trade({
            "Stock": s,
            "Signal": sig,
            "Entry": round(price,2),
            "Exit": round(exit_price,2),
            "Lot": lot,
            "PnL": round(pnl,2)
        })

        trade_count += 1

    # ===== JIKA TIDAK ADA SINYAL =====
    if trade_count == 0:
        # tetap buat file supaya dashboard hidup
        save_trade({
            "Stock": "NONE",
            "Signal": "NONE",
            "Entry": 0,
            "Exit": 0,
            "Lot": 0,
            "PnL": 0
        })

        send(f"⚠️ MARKET: {market}\nTidak ada sinyal hari ini")
        return

    # ===== SAVE LOG =====
    save_log(log_data)

    # ===== MESSAGE =====
    msg = f"📊 MARKET: {market}\n\n🔥 SIGNAL 🔥\n\n"
    msg += "\n".join(results)

    stats = get_stats()
    equity = get_equity()
    perf = get_performance()

    msg += f"\n\n📊 STATS:\n{stats}"
    msg += f"\n\n💰 EQUITY: {int(equity)}"
    msg += f"\n📈 PERFORMANCE:\n{perf}"

    # ===== SEND TELEGRAM =====
    send(msg)


if __name__ == "__main__":
    run()
