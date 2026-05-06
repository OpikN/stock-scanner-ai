import pandas as pd
import yfinance as yf
import random
from app.storage import save_strategy


# =========================
# MAIN OPTIMIZER
# =========================
def optimize(limit=50):
    print("🧠 Optimizer start...")

    df = yf.download(
        "BBCA.JK",
        period="5d",
        interval="15m",
        progress=False
    )

    if df is None or df.empty or len(df) < 50:
        print("❌ Data tidak cukup")
        return

    best_score = -999999
    best_params = None

    for i in range(limit):
        ema_fast = random.randint(3, 10)
        ema_slow = random.randint(15, 30)
        rsi_buy = random.randint(20, 45)
        rsi_sell = random.randint(55, 80)

        pnl, winrate, trades = backtest(
            df, ema_fast, ema_slow, rsi_buy, rsi_sell
        )

        # 🔥 scoring lebih realistis
        score = pnl * 10 + winrate * 5 - (100 - winrate)

        if score > best_score:
            best_score = score
            best_params = {
                "ema_fast": ema_fast,
                "ema_slow": ema_slow,
                "rsi_buy": rsi_buy,
                "rsi_sell": rsi_sell,
                "score": round(score, 2),
                "trades": trades,
                "winrate": round(winrate, 2)
            }

        print(f"🔁 Iter {i+1}/{limit} | Score: {round(score,2)}")

    if best_params:
        save_strategy(best_params)
        print("✅ BEST STRATEGY:", best_params)


# =========================
# BACKTEST ENGINE
# =========================
def backtest(df, ema_fast, ema_slow, rsi_buy, rsi_sell):
    df = df.copy()

    # =========================
    # INDICATORS
    # =========================
    df["ema_fast"] = df["Close"].ewm(span=ema_fast).mean()
    df["ema_slow"] = df["Close"].ewm(span=ema_slow).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()

    rs = gain / (loss + 1e-9)
    df["rsi"] = 100 - (100 / (1 + rs))

    # =========================
    # SIMULATION
    # =========================
    pnl = 0
    wins = 0
    trades = 0

    position = None
    entry = 0

    for i in range(1, len(df)):
        row = df.iloc[i]

        ema_fast_val = row["ema_fast"]
        ema_slow_val = row["ema_slow"]
        rsi = row["rsi"]
        price = row["Close"]

        # OPEN BUY
        if position is None:
            if ema_fast_val > ema_slow_val and rsi < rsi_buy:
                position = "BUY"
                entry = price
                trades += 1

        # CLOSE BUY
        elif position == "BUY":
            if ema_fast_val < ema_slow_val or rsi > rsi_sell:
                result = price - entry
                pnl += result

                if result > 0:
                    wins += 1

                position = None

    # =========================
    # METRICS
    # =========================
    winrate = (wins / trades * 100) if trades > 0 else 0

    return pnl, winrate, trades
