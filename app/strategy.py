# =========================
# STRATEGY (FORCE MODE)
# =========================

def generate_signal(df):
    """
    FORCE TRADE MODE
    Tujuan:
    - Memastikan sistem entry minimal 1 trade
    - Test end-to-end (scanner → portfolio → dashboard)
    """

    if df is None or df.empty:
        return "HOLD", 0

    try:
        last = df.iloc[-1]
        price = float(last["Close"])
    except:
        return "HOLD", 0

    # =========================
    # FORCE ENTRY 🔥
    # =========================
    return "BUY", price
