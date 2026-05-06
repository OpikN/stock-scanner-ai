import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
import yfinance as yf

from app.strategy import generate_signal
from app.adaptive import update_mode
from app.storage import save_trade

STOCKS = ["BBCA.JK", "BBRI.JK", "TLKM.JK"]


def run():
    print("🚀 SCANNER START (AI LIVE MODE)")

    for symbol in STOCKS:
        try:
            df = yf.download(
                symbol,
                period="5d",
                interval="15m",
                auto_adjust=True,
                progress=False
            )

            if df is None or df.empty:
                continue

            # =========================
            # UPDATE AI MODE
            # =========================
            update_mode(df)

            # =========================
            # ADD INDICATORS
            # =========================
            df["ema_5"] = df["Close"].ewm(span=5).mean()
            df["ema_10"] = df["Close"].ewm(span=10).mean()
            df["ema_20"] = df["Close"].ewm(span=20).mean()
            df["ema_50"] = df["Close"].ewm(span=50).mean()

            delta = df["Close"].diff()
            gain = delta.clip(lower=0).rolling(14).mean()
            loss = -delta.clip(upper=0).rolling(14).mean()
            rs = gain / loss
            df["rsi"] = 100 - (100 / (1 + rs))

            # =========================
            # GENERATE SIGNAL
            # =========================
            signal, price = generate_signal(df)

            if signal != "HOLD":
                trade = {
                    "stock": symbol,
                    "signal": signal,
                    "price": round(price, 2)
                }

                print("📊 SIGNAL:", trade)

                save_trade(trade)

        except Exception as e:
            print("❌ ERROR:", symbol, e)


if __name__ == "__main__":
    run()
