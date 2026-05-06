import json
import pandas as pd
import yfinance as yf
from itertools import product

STRATEGY_PATH = "data/strategy.json"

STOCKS = ["BBCA.JK", "BBRI.JK", "TLKM.JK"]


# =========================
# SAFE FLOAT
# =========================
def safe_float(x):
    try:
        if hasattr(x, "item"):
            return float(x.item())
        return float(x)
    except:
        return 0.0


# =========================
# SAVE / LOAD
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
# BACKTEST
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
    trades = 0
    wins = 0

    for i in range(20, len(df)):
        row = df.iloc[i]

        ema_fast = safe_float(row["ema_fast"])
        ema_slow = safe_float(row["ema_slow"])
        rsi = safe_float(row["rsi"])
        price = safe_float(row["Close"])

        if pd.isna(ema_fast) or pd.isna(ema_slow) or pd.isna(rsi):
            continue

        if ema_fast > ema_slow and rsi < rsi_buy:
            entry = price
            exit_price = safe_float(df.iloc[i + 3]["Close"]) if i + 3 < len(df) else entry
            result = exit_price - entry

        elif ema_fast < ema_slow and rsi > rsi_sell:
            entry = price
            exit_price = safe_float(df.iloc[i + 3]["Close"]) if i + 3 < len(df) else entry
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
# SPLIT TRAIN / VALID
# =========================
def split_data(df):
    split = int(len(df) * 0.7)
    return df.iloc[:split], df.iloc[split:]


# =========================
# DOWNLOAD MULTI STOCK
# =========================
def load_all_data():
    data = {}

    for s in STOCKS:
        try:
            df = yf.download(
                s,
                period="90d",
                interval="1h",
                auto_adjust=True,
                progress=False
            )

            if df is not None and not df.empty:
                data[s] = df

        except:
            continue

    return data


# =========================
# OPTIMIZER CORE 🔥
# =========================
def optimize():
    print("🚀 AI OPTIMIZER MULTI STOCK")

    data_map = load_all_data()

    if not data_map:
        print("❌ No data")
        return

    best_score = -999999
    best_params = None

    fast_range = [5, 8, 10]
    slow_range = [20, 30, 50]
    rsi_buy_range = [25, 30, 35]
    rsi_sell_range = [65, 70, 75]

    for fast, slow, rsi_b, rsi_s in product(
        fast_range, slow_range, rsi_buy_range, rsi_sell_range
    ):
        if fast >= slow:
            continue

        total_score = 0
        valid_count = 0

        for stock, df in data_map.items():
            train, valid = split_data(df)

            pnl_train, wr_train, tr_train = backtest(train, fast, slow, rsi_b, rsi_s)
            pnl_val, wr_val, tr_val = backtest(valid, fast, slow, rsi_b, rsi_s)

            if tr_train < 5 or tr_val < 3:
                continue

            # =========================
            # ANTI OVERFIT SCORE
            # =========================
            stability = abs(wr_train - wr_val)

            score = (
                pnl_val * 1.5 +
                wr_val * 10 -
                stability * 5
            )

            total_score += score
            valid_count += 1

        if valid_count == 0:
            continue

        avg_score = total_score / valid_count

        if avg_score > best_score:
            best_score = avg_score
            best_params = {
                "ema_fast": fast,
                "ema_slow": slow,
                "rsi_buy": rsi_b,
                "rsi_sell": rsi_s,
                "score": round(avg_score, 2),
                "stocks_used": valid_count
            }

    if best_params:
        save_strategy(best_params)
        print("✅ BEST GLOBAL STRATEGY:")
        print(best_params)
    else:
        print("❌ No strategy found")
