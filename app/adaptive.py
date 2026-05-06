import json
import pandas as pd

STATE_PATH = "data/state.json"


# =========================
# SAVE STATE
# =========================
def save_state(state):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def load_state():
    try:
        with open(STATE_PATH) as f:
            return json.load(f)
    except:
        return {"mode": "SAFE"}


# =========================
# DETECT MARKET
# =========================
def detect_market(df):
    df = df.copy()

    df["ema20"] = df["Close"].ewm(span=20).mean()
    df["ema50"] = df["Close"].ewm(span=50).mean()

    trend = df["ema20"].iloc[-1] - df["ema50"].iloc[-1]

    volatility = df["Close"].pct_change().rolling(10).std().iloc[-1]

    if volatility > 0.03:
        return "VOLATILE"

    if trend > 0:
        return "UPTREND"

    if trend < 0:
        return "DOWNTREND"

    return "SIDEWAYS"


# =========================
# SELECT MODE
# =========================
def select_mode(market_type):
    if market_type == "UPTREND":
        return "AGGRESSIVE"

    if market_type == "DOWNTREND":
        return "SAFE"

    if market_type == "VOLATILE":
        return "SCALP"

    return "SAFE"


# =========================
# MAIN ADAPTIVE ENGINE
# =========================
def update_mode(df):
    market = detect_market(df)
    mode = select_mode(market)

    state = {
        "mode": mode,
        "market": market
    }

    save_state(state)

    print("🧠 AI MODE:", state)

    return state
