import json
import pandas as pd
import yfinance as yf
from itertools import product

STRATEGY_PATH = "data/strategy.json"


# =========================
# LOAD / SAVE STRATEGY
# =========================
def save_strategy(params):
    with open(STRATEGY_PATH, "w") as f:
        json.dump(params, f, indent=2)


def load_strategy():
    try:
        with open(STRATEGY_PATH, "r") as f:
            return json.load(f)
    except:
        return None


# =========================
# SIMPLE BACKTEST
# =========================
def backtest(df, fast, slow, rsi_buy, rsi_sell):
    df = df.copy()

    df["ema_fast"] = df["Close"].ewm(span=fast).mean()
    df["ema_slow"] = df["Close"].ewm(span=slow).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    df["rsi"] = 100 - (100 / (1 + rs))

    pnl = 0
    wins = 0
    trades = 0

    for i in range(20, len(df)):
        row = df.iloc[i]

        if row["ema_fast"] > row["ema_slow"] and row["rsi"] < rsi_buy:
            entry = row["Close"]
            exit_price = df.iloc[i+3]["Close"] if i+3 < len(df) else entry
            result = exit_price - entry

        elif row["ema_fast"] < row["ema_slow"] and row["rsi"] > rsi_sell:
            entry = row["Close"]
            exit_price = df.iloc[i+3]["Close"] if i+3 < len(df) else entry
            result = entry - exit_price

        else:
            continue

        pnl += result
        trades += 1

        if result > 0:
            wins += 1

    winrate = (wins / trades * 100) if trades > 0 else 0

    return pnl, winrate, trades


# =========================
# OPTIMIZER CORE
# =========================
def optimize():
    print("🚀 RUN AI OPTIMIZER")

    df = yf.download("BBCA.JK", period="60d", interval="1h", progress=False)

    if df is None or df.empty:
        print("❌ No data")
        return

    best_score = -999999
    best_params = None

    # PARAMETER GRID
    fast_range = [5, 8, 10]
    slow_range = [20, 30, 50]
    rsi_buy_range = [25, 30, 35]
    rsi_sell_range = [65, 70, 75]

    for fast, slow, rsi_b, rsi_s in product(fast_range, slow_range, rsi_buy_range, rsi_sell_range):

        if fast >= slow:
            continue

        pnl, winrate, trades = backtest(df, fast, slow, rsi_b, rsi_s)

        if trades < 5:
            continue

        score = pnl + (winrate * 10)

        if score > best_score:
            best_score = score
            best_params = {
                "ema_fast": fast,
                "ema_slow": slow,
                "rsi_buy": rsi_b,
                "rsi_sell": rsi_s,
                "score": score
            }

    if best_params:
        save_strategy(best_params)
        print("✅ BEST STRATEGY:", best_params)
    else:
        print("❌ No strategy found")
