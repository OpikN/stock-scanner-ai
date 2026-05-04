import yfinance as yf
import ta
import pandas as pd
import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

stocks = ["BBCA.JK","BBRI.JK","TLKM.JK"]

def send_telegram(msg):
    if not BOT_TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def run():
    results = []

    for s in stocks:
        try:
            df = yf.download(s, period="6mo", progress=False)
            price = df["Close"].iloc[-1]

            results.append({
                "Stock": s,
                "Price": round(price,2)
            })
        except:
            pass

    df = pd.DataFrame(results)
    df.to_csv("data.csv", index=False)

    msg = "📊 STOCK UPDATE\n\n"
    for _, r in df.iterrows():
        msg += f"{r['Stock']} @ {r['Price']}\n"

    send_telegram(msg)

if __name__ == "__main__":
    run()
