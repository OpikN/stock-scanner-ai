import os
import requests
from core import *

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID   = os.getenv("CHAT_ID")

def send(msg):
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ BOT_TOKEN / CHAT_ID tidak terbaca")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    r = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

    print("STATUS:", r.status_code)
    print("RESPONSE:", r.text)


def run():
    results = []

    for s in STOCKS:
        df = get_data(s)

        if df is None:
            continue

        df = compute(df)

        sig, price = signal(df)

        results.append(f"{s} → {sig} @ {round(price,2)}")

    if not results:
        send("⚠️ Data kosong")
        return

    msg = "🔥 DAILY SIGNAL 🔥\n\n" + "\n".join(results)
    send(msg)


if __name__ == "__main__":
    run()
