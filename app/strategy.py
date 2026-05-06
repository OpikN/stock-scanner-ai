# =========================
# STRATEGY ENGINE (FIXED)
# =========================

def generate_signal(df):
    """
    Safe version:
    - Tidak error pandas Series
    - Ambil value terakhir
    - Bisa force trade untuk testing
    """

    if df is None or df.empty:
        return "HOLD", 0

    try:
        # =========================
        # AMBIL BARIS TERAKHIR (WAJIB 🔥)
        # =========================
        last = df.iloc[-1]

        # =========================
        # AMBIL VALUE (PASTIKAN FLOAT)
        # =========================
        price = float(last["Close"])

        # gunakan .get supaya tidak error kalau kolom belum ada
        ema_fast = float(last.get("ema_10", 0))
        ema_slow = float(last.get("ema_50", 0))
        rsi = float(last.get("rsi", 50))

    except Exception as e:
        print("❌ ERROR parsing strategy:", e)
        return "HOLD", 0

    # =========================
    # 🔥 MODE TEST (FORCE TRADE)
    # =========================
    return "BUY", price

    # =========================
    # 🔽 NANTI AKTIFKAN INI (AI REAL)
    # =========================
    """
    if ema_fast > ema_slow and rsi < 45:
        return "BUY", price

    elif ema_fast < ema_slow and rsi > 55:
        return "SELL", price

    return "HOLD", price
    """
