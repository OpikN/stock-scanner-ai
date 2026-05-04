import os
import requests
from core import *
from logger import save_log, get_stats

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID   = os.getenv("CHAT_ID")

def send(msg):
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Secret tidak terbaca")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


def run():
    # MARKET
    ihsg = get_data(IHSG)
    if ihsg is None:
        send("❌ Gagal ambil IHSG")
        return

    ihsg = compute(ihsg)
    market = get_market_regime(ihsg)

    results = []
    log_data = []

    for s in STOCKS:
        df = get_data(s)
        if df is None:
            continue

        df = compute(df)
        sig, price = signal(df)

        # FILTER MARKET
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

    if not results:
        send(f"⚠️ Market: {market}\nTidak ada sinyal")
        return

    save_log(log_data)

    msg = f"📊 MARKET: {market}\n\n🔥 SIGNAL 🔥\n\n"
    msg += "\n".join(results)

    stats = get_stats()
    msg += f"\n\n📊 STATS:\n{stats}"

    send(msg)


if __name__ == "__main__":
    run()
