import sys
import os

# supaya bisa import app/*
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import yfinance as yf

from app.strategy import generate_signal
from app.adaptive import update_mode
from app.portfolio import open_position, update_positions
from app.learning import learn_from_trades

STOCKS = ["BBCA.JK", "BBRI.JK", "TLKM.JK"]


def run():
    print("🚀 SCANNER START (FULL AI SYSTEM)")

    price_map = {}

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
            # SIGNAL
            # =========================
            signal, price = generate_signal(df)

            price_map[symbol] = price

            if signal != "HOLD":
                print(f"📊 SIGNAL: {symbol} {signal} @ {price}")
                open_position(symbol, signal, price)

        except Exception as e:
            print("❌ ERROR:", symbol, e)

    # =========================
    # UPDATE POSITIONS (TP/SL/TRAILING)
    # =========================
    update_positions(price_map)

    # =========================
    # AI SELF LEARNING 🔥
    # =========================
    learn_from_trades()


if __name__ == "__main__":
    run()
