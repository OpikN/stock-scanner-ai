import pandas as pd
import json
import os

STRATEGY_PATH = "data/strategy.json"
POSITIONS_PATH = "data/positions.csv"


# =========================
# LOAD / SAVE
# =========================
def load_strategy():
    try:
        with open(STRATEGY_PATH) as f:
            return json.load(f)
    except:
        return {}


def save_strategy(data):
    with open(STRATEGY_PATH, "w") as f:
        json.dump(data, f, indent=2)


# =========================
# LEARNING ENGINE 🔥
# =========================
def learn_from_trades():
    if not os.path.exists(POSITIONS_PATH):
        return

    df = pd.read_csv(POSITIONS_PATH)

    if df.empty:
        return

    closed = df[df["status"] == "CLOSED"]

    if len(closed) < 5:
        print("⚠️ Not enough trades to learn")
        return

    wins = closed[closed["pnl"] > 0]
    losses = closed[closed["pnl"] <= 0]

    winrate = len(wins) / len(closed) * 100
    avg_pnl = closed["pnl"].mean()

    strategy = load_strategy()

    # default fallback
    ema_fast = strategy.get("ema_fast", 5)
    ema_slow = strategy.get("ema_slow", 20)
    rsi_buy = strategy.get("rsi_buy", 30)
    rsi_sell = strategy.get("rsi_sell", 70)

    # =========================
    # ADAPT LOGIC 🔥
    # =========================

    # kalau sering loss → lebih konservatif
    if winrate < 45:
        rsi_buy -= 2
        rsi_sell += 2
        ema_fast = max(3, ema_fast - 1)

    # kalau bagus → lebih agresif
    elif winrate > 60:
        rsi_buy += 2
        rsi_sell -= 2
        ema_fast += 1

    # jaga batas aman
    rsi_buy = max(20, min(50, rsi_buy))
    rsi_sell = max(50, min(80, rsi_sell))

    # =========================
    # SAVE UPDATE
    # =========================
    new_strategy = {
        "ema_fast": ema_fast,
        "ema_slow": ema_slow,
        "rsi_buy": rsi_buy,
        "rsi_sell": rsi_sell,
        "winrate": round(winrate, 2),
        "avg_pnl": round(avg_pnl, 2)
    }

    save_strategy(new_strategy)

    print("🧠 AI LEARNING UPDATE:")
    print(new_strategy)
