import sys
import os
import json
import time
import pandas as pd

# FIX PATH
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

DATA_PATH = "data/positions.csv"
STATE_PATH = "data/state.json"


def load_positions():
    if os.path.exists(DATA_PATH):
        try:
            return pd.read_csv(DATA_PATH)
        except:
            return pd.DataFrame()
    return pd.DataFrame()


def detect_market_mode(df):
    if df.empty or len(df) < 5:
        return "SAFE"

    # gunakan pnl terakhir
    if "pnl" not in df.columns:
        return "SAFE"

    recent = df.tail(10)

    winrate = (recent["pnl"] > 0).mean() * 100
    avg_pnl = recent["pnl"].mean()

    # LOGIC MODE
    if winrate > 60 and avg_pnl > 0:
        return "AGGRESSIVE"
    elif winrate < 40:
        return "SAFE"
    else:
        return "SCALP"


def save_state(mode):
    state = {
        "mode": mode,
        "updated": time.time()
    }

    os.makedirs("data", exist_ok=True)

    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=4)


def run():
    print("🧠 RUN AI BRAIN")

    df = load_positions()

    mode = detect_market_mode(df)

    print(f"📊 AI MODE: {mode}")

    save_state(mode)


if __name__ == "__main__":
    run()
