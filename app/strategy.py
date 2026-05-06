from app.storage import load_strategy
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

    ema_fast_period = params.get("ema_fast", 5)
    ema_slow_period = params.get("ema_slow", 20)

    ema_fast_key = f"ema_{ema_fast_period}"
    ema_slow_key = f"ema_{ema_slow_period}"

    # =========================
    # LOAD ADAPTIVE MODE
    # =========================
    state = load_state()
    mode = state.get("mode", "SAFE")

    # mode-based RSI
    if mode == "AGGRESSIVE":
        rsi_buy = 45
        rsi_sell = 55
    elif mode == "SCALP":
        rsi_buy = 50
        rsi_sell = 50
    else:  # SAFE
        rsi_buy = 40
        rsi_sell = 60

    # =========================
    # GET VALUE
    # =========================
    ema_fast = safe_float(last.get(ema_fast_key, 0))
    ema_slow = safe_float(last.get(ema_slow_key, 0))
    rsi = safe_float(last.get("rsi", 50))
    price = safe_float(last.get("Close", 0))

    # =========================
    # VALIDASI DATA
    # =========================
    if price == 0:
        return "HOLD", 0

    # =========================
    # SIGNAL LOGIC (SMART TREND + RSI)
    # =========================

    # TREND UP
    if ema_fast > ema_slow:
        if rsi < rsi_buy:
            return "BUY", price

    # TREND DOWN
    elif ema_fast < ema_slow:
        if rsi > rsi_sell:
            return "SELL", price

    # =========================
    # FALLBACK (ANTI DIAM)
    # =========================
    if ema_fast > ema_slow:
        return "BUY", price
    elif ema_fast < ema_slow:
        return "SELL", price

    return "HOLD", price
