# scanner.py
# OPIK AI TERMINAL - Stock Scanner
# Versi stabil untuk GitHub Codespaces / VPS / PC lokal

import yfinance as yf
import pandas as pd
import time
from datetime import datetime

WATCHLIST = [
    "BBCA.JK",
    "BBRI.JK",
    "TLKM.JK",
    "ASII.JK",
    "BMRI.JK"
]

def calculate_signal(df):
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA50"] = df["Close"].rolling(50).mean()

    last = df.iloc[-1]

    if last["MA20"] > last["MA50"]:
        return "BUY"
    elif last["MA20"] < last["MA50"]:
        return "SELL"
    else:
        return "HOLD"

def scan_stock(symbol):
    try:
        df = yf.download(
            symbol,
            period="3mo",
            interval="1d",
            progress=False,
            auto_adjust=True
        )

        if df.empty:
            return {
                "Symbol": symbol,
                "Price": "-",
                "Signal": "NO DATA"
            }

        signal = calculate_signal(df)

        price = round(df["Close"].iloc[-1], 2)

        return {
            "Symbol": symbol,
            "Price": price,
            "Signal": signal
        }

    except Exception as e:
        return {
            "Symbol": symbol,
            "Price": "-",
            "Signal": f"ERROR: {e}"
        }

def run_scanner():
    print("=" * 60)
    print("📊 OPIK AI TERMINAL - LIVE SCANNER")
    print("⏰", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)

    results = []

    for stock in WATCHLIST:
        result = scan_stock(stock)
        results.append(result)

    df = pd.DataFrame(results)

    print(df.to_string(index=False))
    print("=" * 60)

if __name__ == "__main__":
    while True:
        run_scanner()
        time.sleep(60)