import os
import requests
from core import *
from logger import save_log, get_stats
from portfolio import save_trade, calculate_pnl, get_equity, get_performance

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID   = os.getenv("CHAT_ID")


def send(msg):
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ BOT_TOKEN / CHAT_ID tidak terbaca")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


def run():
    print("🚀 RUN SCANNER")

    # ===== MARKET =====
    ihsg = get_data(IHSG)
    if ihsg is None:
        send("❌ Gagal ambil IHSG")
        return

    ihsg = compute(ihsg)
    market = get_market_regime(ihsg)

    print("MARKET:", market)

    results = []
    log_data = []
    trade_count = 0

    # ===== SCAN =====
    for s in STOCKS:
        print("SCAN:", s)

        df = get_data(s)
        if df is None:
            print("❌ DATA KOSONG:", s)
            continue

        df = compute(df)
        sig, price = signal(df)

        print("SIGNAL:", sig, "PRICE:", price)

        # ===== FILTER MARKET =====
        if market == "BULL" and sig == "SELL":
            continue
        if market == "BEAR" and sig == "BUY":
            continue

        # ❗ SIDEWAYS tetap diizinkan supaya ada data
        # if market == "SIDEWAYS": continue  ← DIHAPUS

        # ===== VALIDASI =====
        if price is None or price == 0:
            continue

        # ===== TRADE SIMULATION =====
        lot = 1

        if sig == "BUY":
            exit_price = price * 1.02
        elif sig == "SELL":
            exit_price = price * 0.98
        else:
            continue

        pnl = calculate_pnl(price, exit_price, sig, lot)

        # ===== SAVE TRADE (WAJIB LENGKAP) =====
        trade_data = {
            "Stock": s,
            "Signal": sig,
            "Entry": round(float(price), 2),
            "Exit": round(float(exit_price), 2),
            "Lot": int(lot),
            "PnL": round(float(pnl), 2)
        }

        print("SAVE TRADE:", trade_data)

        save_trade(trade_data)

        results.append(f"{s} → {sig} @ {round(price,2)}")

        log_data.append({
            "Stock": s,
            "Signal": sig,
            "Entry": round(price, 2)
        })

        trade_count += 1

    # ===== FALLBACK (AGAR FILE TIDAK KOSONG) =====
    if trade_count == 0:
        print("⚠️ TIDAK ADA TRADE, BUAT DUMMY")

        dummy = {
            "Stock": "BBCA.JK",
            "Signal": "BUY",
            "Entry": 100,
            "Exit": 102,
            "Lot": 1,
            "PnL": 200
        }

        save_trade(dummy)

        send(f"⚠️ MARKET: {market}\nTidak ada sinyal, dummy dibuat")
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

    send(msg)


if __name__ == "__main__":
    run()
