import pandas as pd
import yfinance as yf
import random
from app.storage import save_strategy


def optimize(limit=50):
    print("🧠 Optimizer start...")

    df = yf.download(
        "BBCA.JK",
        period="5d",     # 🔥 jangan terlalu besar
        interval="15m",
        progress=False
    )

    if df is None or df.empty:
        print("❌ Data kosong")
        return

    best_score = -999999
    best_params = None

    # 🔥 RANDOM SEARCH (bukan brute force)
    for i in range(limit):
        ema_fast = random.randint(3, 10)
        ema_slow = random.randint(15, 30)
        rsi_buy = random.randint(20, 40)
        rsi_sell = random.randint(60, 80)

        score = backtest(df, ema_fast, ema_slow, rsi_buy, rsi_sell)

        if score > best_score:
            best_score = score
            best_params = {
                "ema_fast": ema_fast,
                "ema_slow": ema_slow,
                "rsi_buy": rsi_buy,
                "rsi_sell": rsi_sell
            }

        print(f"🔁 Iter {i+1}/{limit} | Score: {score}")

    if best_params:
        save_strategy(best_params)
        print("✅ BEST STRATEGY:", best_params)


# =========================
# SIMPLE BACKTEST
# =========================
def backtest(df, ema_fast, ema_slow, rsi_buy, rsi_sell):
    df = df.copy()

    df["ema_fast"] = df["Close"].ewm(span=ema_fast).mean()
    df["ema_slow"] = df["Close"].ewm(span=ema_slow).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    df["rsi"] = 100 - (100 / (1 + rs))

    pnl = 0

    for i in range(1, len(df)):
        row = df.iloc[i]

        if row["ema_fast"] > row["ema_slow"] and row["rsi"] < rsi_buy:
            pnl += 1
        elif row["ema_fast"] < row["ema_slow"] and row["rsi"] > rsi_sell:
            pnl -= 1

    return pnl
