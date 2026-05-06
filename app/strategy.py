# =========================
# SAFE EXTRACT
# =========================
def safe_float(x, default=0.0):
    try:
        # kalau Series → ambil terakhir
        if hasattr(x, "iloc"):
            return float(x.iloc[-1])
        # kalau numpy scalar
        if hasattr(x, "item"):
            return float(x.item())
        return float(x)
    except:
        return default


# =========================
# STRATEGY ENGINE (ANTI ERROR)
# =========================
def generate_signal(df):
    if df is None or df.empty:
        return "HOLD", 0

    try:
        # =========================
        # AMBIL BARIS TERAKHIR
        # =========================
        last = df.iloc[-1]

        # =========================
        # SAFE VALUE (ANTI SERIES 🔥)
        # =========================
        price = safe_float(last["Close"])
        ema_fast = safe_float(last.get("ema_10"))
        ema_slow = safe_float(last.get("ema_50"))
        rsi = safe_float(last.get("rsi"), 50)

        if price == 0:
            return "HOLD", 0

    except Exception as e:
        print("❌ ERROR parsing strategy:", e)
        return "HOLD", 0

    # =========================
    # 🔥 FORCE TRADE (TEST)
    # =========================
    return "BUY", price

    # =========================
    # 🔽 NANTI AKTIFKAN AI
    # =========================
    """
    if ema_fast > ema_slow and rsi < 45:
        return "BUY", price
    elif ema_fast < ema_slow and rsi > 55:
        return "SELL", price
    return "HOLD", price
    """
