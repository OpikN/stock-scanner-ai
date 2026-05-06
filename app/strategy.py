from app.optimizer import load_strategy
from app.adaptive import load_state


# =========================
# SAFE FLOAT
# =========================
def safe_float(x):
    try:
        if hasattr(x, "iloc"):
            return float(x.iloc[0])
        if hasattr(x, "item"):
            return float(x.item())
        return float(x)
    except:
        return 0.0


# =========================
# SIGNAL GENERATOR
# =========================
def generate_signal(df):
    if df is None or df.empty:
        return "HOLD", 0

    last = df.iloc[-1]

    # =========================
    # LOAD AI STRATEGY
    # =========================
    params = load_strategy()

    if params:
        ema_fast_key = f"ema_{params.get('ema_fast', 5)}"
        ema_slow_key = f"ema_{params.get('ema_slow', 20)}"
    else:
        ema_fast_key = "ema_5"
        ema_slow_key = "ema_20"

    # =========================
    # LOAD ADAPTIVE MODE
    # =========================
    state = load_state()
    mode = state.get("mode", "SAFE")

    if mode == "AGGRESSIVE":
        rsi_buy = 35
        rsi_sell = 65
    elif mode == "SCALP":
        rsi_buy = 40
        rsi_sell = 60
    else:  # SAFE
        rsi_buy = 25
        rsi_sell = 75

    # =========================
    # GET VALUE
    # =========================
    ema_fast = safe_float(last.get(ema_fast_key, 0))
    ema_slow = safe_float(last.get(ema_slow_key, 0))
    rsi = safe_float(last.get("rsi", 50))
    price = safe_float(last.get("Close", 0))

    # =========================
    # SIGNAL LOGIC
    # =========================
    if ema_fast > ema_slow and rsi < rsi_buy:
        return "BUY", price

    elif ema_fast < ema_slow and rsi > rsi_sell:
        return "SELL", price

    return "HOLD", price
