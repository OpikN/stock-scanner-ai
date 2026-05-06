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


# =========================
# INDICATORS
# =========================
def add_indicators(df, fast, slow):
    df["ema_fast"] = df["Close"].ewm(span=fast).mean()
    df["ema_slow"] = df["Close"].ewm(span=slow).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    df["rsi"] = 100 - (100 / (1 + rs))

    return df


# =========================
# TP/SL BACKTEST 🔥
# =========================
def backtest_tp_sl(df, fast, slow, rsi_buy, rsi_sell, rr):
    df = add_indicators(df.copy(), fast, slow)

    pnl = 0
    trades = 0
    wins = 0

    for i in range(30, len(df) - 5):
        row = df.iloc[i]

        ema_fast = safe_float(row["ema_fast"])
        ema_slow = safe_float(row["ema_slow"])
        rsi = safe_float(row["rsi"])
        price = safe_float(row["Close"])

        if pd.isna(ema_fast) or pd.isna(ema_slow) or pd.isna(rsi):
            continue

        # =========================
        # BUY
        # =========================
        if ema_fast > ema_slow and rsi < rsi_buy:
            entry = price
            sl = entry * 0.98
            tp = entry + (entry - sl) * rr

            for j in range(i + 1, min(i + 10, len(df))):
                high = safe_float(df.iloc[j]["High"])
                low = safe_float(df.iloc[j]["Low"])

                if low <= sl:
                    pnl -= (entry - sl)
                    trades += 1
                    break

                if high >= tp:
                    pnl += (tp - entry)
                    trades += 1
                    wins += 1
                    break

        # =========================
        # SELL
        # =========================
        elif ema_fast < ema_slow and rsi > rsi_sell:
            entry = price
            sl = entry * 1.02
            tp = entry - (sl - entry) * rr

            for j in range(i + 1, min(i + 10, len(df))):
                high = safe_float(df.iloc[j]["High"])
                low = safe_float(df.iloc[j]["Low"])

                if high >= sl:
                    pnl -= (sl - entry)
                    trades += 1
                    break

                if low <= tp:
                    pnl += (entry - tp)
                    trades += 1
                    wins += 1
                    break

    winrate = (wins / trades * 100) if trades > 0 else 0
    return pnl, winrate, trades


# =========================
# WALK FORWARD 🔥
# =========================
def walk_forward(df, fast, slow, rsi_b, rsi_s, rr):
    window = int(len(df) * 0.6)
    step = int(len(df) * 0.2)

    scores = []

    for start in range(0, len(df) - window, step):
        train = df.iloc[start:start + window]
        test = df.iloc[start + window:start + window + step]

        if len(test) < 20:
            continue

        pnl_train, wr_train, _ = backtest_tp_sl(train, fast, slow, rsi_b, rsi_s, rr)
        pnl_test, wr_test, tr_test = backtest_tp_sl(test, fast, slow, rsi_b, rsi_s, rr)

        if tr_test < 3:
            continue

        stability = abs(wr_train - wr_test)

        score = pnl_test * 1.5 + wr_test * 10 - stability * 5
        scores.append(score)

    return sum(scores) / len(scores) if scores else -9999


# =========================
# LOAD DATA
# =========================
def load_data():
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
    print("🚀 AI OPTIMIZER WALK-FORWARD")

    data_map = load_data()

    if not data_map:
        print("❌ No data")
        return

    best_score = -999999
    best_params = None

    fast_range = [5, 8, 10]
    slow_range = [20, 30, 50]
    rsi_buy_range = [25, 30, 35]
    rsi_sell_range = [65, 70, 75]
    rr_range = [1.5, 2.0, 2.5]

    for fast, slow, rsi_b, rsi_s, rr in product(
        fast_range, slow_range, rsi_buy_range, rsi_sell_range, rr_range
    ):
        if fast >= slow:
            continue

        total_score = 0
        count = 0

        for stock, df in data_map.items():
            score = walk_forward(df, fast, slow, rsi_b, rsi_s, rr)

            if score == -9999:
                continue

            total_score += score
            count += 1

        if count == 0:
            continue

        avg_score = total_score / count

        if avg_score > best_score:
            best_score = avg_score
            best_params = {
                "ema_fast": fast,
                "ema_slow": slow,
                "rsi_buy": rsi_b,
                "rsi_sell": rsi_s,
                "rr": rr,
                "score": round(avg_score, 2),
                "stocks_used": count
            }

    if best_params:
        save_strategy(best_params)
        print("✅ BEST STRATEGY:")
        print(best_params)
    else:
        print("❌ No strategy found")
