import yfinance as yf
import pandas as pd
import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

stocks = ["BBCA.JK","BBRI.JK","TLKM.JK"]

def send_telegram(msg):
    if not BOT_TOKEN or not CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

def run():
    results = []

    for s in stocks:
        try:
            df = yf.download(s, period="1mo", progress=False)

            # 🔥 AMANIN DATA
            if df is None or df.empty:
                print("Data kosong:", s)
                continue

            if "Close" not in df.columns:
                print("Kolom tidak ada:", s)
                continue

            price = df["Close"].iloc[-1]

            results.append({
                "Stock": s,
                "Price": round(float(price),2)
            })

        except Exception as e:
            print("Error:", s, str(e))

    # 🔥 CEK FINAL
    if not results:
        send_telegram("⚠️ Tidak ada data valid")
        return

    df = pd.DataFrame(results)

    # SAVE
    df.to_csv("data.csv", index=False)

    # TELEGRAM
    msg = "📊 STOCK UPDATE\n\n"
    for _, r in df.iterrows():
        msg += f"{r['Stock']} @ {r['Price']}\n"

    send_telegram(msg)

if __name__ == "__main__":
    run()
