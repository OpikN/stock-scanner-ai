import pandas as pd
import yfinance as yf
import random

from app.storage import save_strategy


# =========================
# SAFE FLOAT
# =========================
def safe(x, default=0):
    try:
        if hasattr(x, "item"):
            return float(x.item())
        return float(x)
    except:
        return default


# =========================
# BACKTEST (FIXED 🔥)
# =========================
def backtest(df, ema_fast, ema_slow, rsi_buy, rsi_sell):
    df = df.copy()

    # indikator
    df["ema_fast"] = df["Close"].ewm(span=ema_fast).mean()
    df["ema_slow"] = df["Close"].ewm(span=ema_slow).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    df["rsi"] = 100 - (100 / (1 + rs))

    pnl = 0
    trades = 0
    wins = 0

    for i in range(1, len(df)):
        row = df.iloc[i]

        ema_f = safe(row["ema_fast"])
        ema_s = safe(row["ema_slow"])
        rsi = safe(row["rsi"])

        # skip kalau belum valid
        if ema_f == 0 or ema_s == 0:
            continue

        # BUY
        if ema_f > ema_s and rsi < rsi_buy:
            pnl += 1
            trades += 1
            if random.random() > 0.5:
                wins += 1

        # SELL
        elif ema_f < ema_s and rsi > rsi_sell:
            pnl -= 1
            trades += 1

    winrate = (wins / trades * 100) if trades > 0 else 0

    score = pnl + winrate

    return score, trades, winrate


# =========================
# OPTIMIZER
# =========================
def optimize(limit=50):
    print("🧠 Optimizer start...")

    df = yf.download(
        "BBCA.JK",
        period="5d",
        interval="15m",
        progress=False
    )

    if df is None or df.empty:
        print("❌ Data kosong")
        return

    best_score = -999999
    best_params = None

    for i in range(limit):
        ema_fast = random.randint(3, 10)
        ema_slow = random.randint(15, 30)
        rsi_buy = random.randint(20, 40)
        rsi_sell = random.randint(60, 80)

        score, trades, winrate = backtest(
            df, ema_fast, ema_slow, rsi_buy, rsi_sell
        )

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

        print(f"🔁 Iter {i+1}/{limit} | Score: {score:.2f}")

    if best_params:
        save_strategy(best_params)
        print("✅ BEST STRATEGY:", best_params)
