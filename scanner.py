# ==============================
# IMPORT
# ==============================
import yfinance as yf
import pandas as pd
import requests
import os

# ==============================
# CONFIG
# ==============================
stocks = ["BBCA.JK", "BBRI.JK", "TLKM.JK"]

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ==============================
# TELEGRAM FUNCTION
# ==============================
def send_telegram(msg):
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ BOT_TOKEN / CHAT_ID tidak terbaca")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    try:
        res = requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": msg
        })

        print("STATUS:", res.status_code)
        print("RESPONSE:", res.text)

    except Exception as e:
        print("ERROR TELEGRAM:", str(e))


# ==============================
# MAIN SCANNER
# ==============================
def run():
    results = []

    for s in stocks:
        try:
            print("Scan:", s)

            df = yf.download(s, period="1mo", progress=False)

            if df is None or df.empty:
                print("Data kosong:", s)
                continue

            if "Close" not in df.columns:
                print("Kolom tidak ada:", s)
                continue

            price = float(df["Close"].iloc[-1])

            results.append({
                "Stock": s,
                "Price": round(price, 2)
            })

        except Exception as e:
            print("ERROR:", s, str(e))

    if not results:
        send_telegram("⚠️ Tidak ada data valid")
        return

    df_result = pd.DataFrame(results)

    # SAVE FILE
    df_result.to_csv("data.csv", index=False)

    # FORMAT MESSAGE
    msg = "📊 STOCK UPDATE\n\n"
    for _, r in df_result.iterrows():
        msg += f"{r['Stock']} @ {r['Price']}\n"

    send_telegram(msg)


# ==============================
# DEBUG + EXECUTE
# ==============================
if __name__ == "__main__":
    print("=== DEBUG ENV ===")
    print("BOT_TOKEN:", BOT_TOKEN)
    print("CHAT_ID:", CHAT_ID)

    # 🔥 TEST TELEGRAM
    send_telegram("TEST 🚀 dari GitHub Actions")

    # 🔥 RUN SCANNER
    run()
