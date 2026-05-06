from app.storage import load_strategy
from app.adaptive import load_state


# =========================
# SAFE FLOAT
# =========================
def safe_float(x, default=0.0):
    try:
        if hasattr(x, "iloc"):
            return float(x.iloc[-1])
        if hasattr(x, "item"):
            return float(x.item())
        return float(x)
    except:
        return default


# =========================
# SIGNAL GENERATOR (AI ADAPTIVE)
# =========================
def generate_signal(df):
    if df is None or df.empty:
        return "HOLD", 0

    last = df.iloc[-1]

    # =========================
    # LOAD STRATEGY (OPTIMIZER)
    # =========================
    params = load_strategy() or {}

    ema_fast_n = params.get("ema_fast", 10)
    ema_slow_n = params.get("ema_slow", 50)
    rsi_buy = params.get("rsi_buy", 30)
    rsi_sell = params.get("rsi_sell", 70)

    ema_fast_key = f"ema_{ema_fast_n}"
    ema_slow_key = f"ema_{ema_slow_n}"

    # =========================
    # LOAD MODE (AI BRAIN)
    # =========================
    state = load_state() or {}
    mode = state.get("mode", "SAFE")

    # adapt threshold berdasarkan mode
    if mode == "AGGRESSIVE":
        rsi_buy += 10   # lebih gampang BUY
        rsi_sell -= 10
    elif mode == "SCALP":
        rsi_buy += 5
        rsi_sell -= 5
    # SAFE → default

    # =========================
    # GET VALUE
    # =========================
    ema_fast = safe_float(last.get(ema_fast_key))
    ema_slow = safe_float(last.get(ema_slow_key))
    rsi = safe_float(last.get("rsi"), 50)
    price = safe_float(last.get("Close"))

    # =========================
    # VALIDASI DATA
    # =========================
    if price == 0:
        return "HOLD", 0

    # =========================
    # TREND STRENGTH FILTER 🔥
    # =========================
    trend_strength = abs(ema_fast - ema_slow) / price

    if trend_strength < 0.002:  # market sideways
        return "HOLD", price

    # =========================
    # SIGNAL LOGIC (REAL)
    # =========================
    # BUY
    if ema_fast > ema_slow and rsi < rsi_buy:
        return "BUY", price

    # SELL
    if ema_fast < ema_slow and rsi > rsi_sell:
        return "SELL", price

    # =========================
    # NO SIGNAL
    # =========================
    return "HOLD", price
