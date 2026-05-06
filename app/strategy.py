from app.optimizer import load_strategy


def safe_float(x):
    try:
        if hasattr(x, "iloc"):
            return float(x.iloc[0])
        return float(x)
    except:
        return 0.0


def generate_signal(df):
    if df is None or df.empty:
        return "HOLD", 0

    last = df.iloc[-1]

    # =========================
    # LOAD AI STRATEGY
    # =========================
    params = load_strategy()

    if params:
        ema_fast_key = f"ema_{params['ema_fast']}"
        ema_slow_key = f"ema_{params['ema_slow']}"
        rsi_buy = params["rsi_buy"]
        rsi_sell = params["rsi_sell"]
    else:
        ema_fast_key = "ema_5"
        ema_slow_key = "ema_20"
        rsi_buy = 30
        rsi_sell = 70

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
