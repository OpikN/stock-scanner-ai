import json
import pandas as pd
import yfinance as yf
from itertools import product

STRATEGY_PATH = "data/strategy.json"


# =========================
# SAFE FLOAT (ANTI ERROR)
# =========================
def safe_float(x):
    try:
        if hasattr(x, "item"):
            return float(x.item())
        return float(x)
    except:
        return 0.0


# =========================
# LOAD / SAVE STRATEGY
# =========================
def save_strategy(params):
    try:
        with open(STRATEGY_PATH, "w") as f:
            json.dump(params, f, indent=2)
    except Exception as e:
        print("❌ Save error:", e)


def load_strategy():
    try:
        with open(STRATEGY_PATH, "r") as f:
            return json.load(f)
    except:
        return None


# =========================
# BACKTEST ENGINE 🔥
# =========================
def backtest(df, fast, slow, rsi_buy, rsi_sell):
    df = df.copy()

    # EMA
    df["ema_fast"] = df["Close"].ewm(span=fast).mean()
    df["ema_slow"] = df["Close"].ewm(span=slow).mean()

    # RSI
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

        ema_fast = safe_float(row["ema_fast"])
        ema_slow = safe_float(row["ema_slow"])
        rsi = safe_float(row["rsi"])
        price = safe_float(row["Close"])

        # skip data invalid
        if pd.isna(ema_fast) or pd.isna(ema_slow) or pd.isna(rsi):
            continue

        # =========================
        # BUY SIGNAL
        # =========================
        if ema_fast > ema_slow and rsi < rsi_buy:
            entry = price

            if i + 3 < len(df):
                exit_price = safe_float(df.iloc[i + 3]["Close"])
            else:
                exit_price = entry

            result = exit_price - entry

        # =========================
        # SELL SIGNAL
        # =========================
        elif ema_fast < ema_slow and rsi > rsi_sell:
            entry = price

            if i + 3 < len(df):
                exit_price = safe_float(df.iloc[i + 3]["Close"])
            else:
                exit_price = entry

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
# OPTIMIZER CORE 🔥
# =========================
def optimize():
    print("🚀 RUN AI OPTIMIZER")

    try:
        df = yf.download(
            "BBCA.JK",
            period="60d",
            interval="1h",
            auto_adjust=True,
            progress=False
        )
    except Exception as e:
        print("❌ Download error:", e)
        return

    if df is None or df.empty:
        print("❌ No data")
        return

    best_score = -999999
    best_params = None

    # =========================
    # PARAMETER GRID
    # =========================
    fast_range = [5, 8, 10]
    slow_range = [20, 30, 50]
    rsi_buy_range = [25, 30, 35]
    rsi_sell_range = [65, 70, 75]

    for fast, slow, rsi_b, rsi_s in product(
        fast_range, slow_range, rsi_buy_range, rsi_sell_range
    ):
        if fast >= slow:
            continue

        pnl, winrate, trades = backtest(df, fast, slow, rsi_b, rsi_s)

        # skip strategi lemah
        if trades < 5:
            continue

        # scoring formula
        score = pnl + (winrate * 10)

        if score > best_score:
            best_score = score
            best_params = {
                "ema_fast": fast,
                "ema_slow": slow,
                "rsi_buy": rsi_b,
                "rsi_sell": rsi_s,
                "score": round(score, 2),
                "trades": trades,
                "winrate": round(winrate, 2)
            }

    if best_params:
        save_strategy(best_params)
        print("✅ BEST STRATEGY FOUND:")
        print(best_params)
    else:
        print("❌ No valid strategy found")
