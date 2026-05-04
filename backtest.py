import pandas as pd

def run_backtest(df, signal, entry_price):
    """
    Real backtest engine:
    - SL / TP
    - Loop candle ke depan
    """

    if df is None or len(df) < 10:
        return None, 0

    # ===== PARAMETER =====
    SL_PCT = 0.02
    TP_PCT = 0.04
    MAX_HOLD = 5  # max 5 candle

    # ===== SET LEVEL =====
    if signal == "BUY":
        sl = entry_price * (1 - SL_PCT)
        tp = entry_price * (1 + TP_PCT)
    else:  # SELL
        sl = entry_price * (1 + SL_PCT)
        tp = entry_price * (1 - TP_PCT)

    # ===== LOOP FORWARD =====
    future = df.tail(MAX_HOLD + 1).iloc[::-1]  # ambil candle ke depan

    exit_price = entry_price

    for i in range(len(future)):
        row = future.iloc[i]

        high = row["High"]
        low = row["Low"]
        close = row["Close"]

        if signal == "BUY":
            if low <= sl:
                return sl, -1
            if high >= tp:
                return tp, 1

        elif signal == "SELL":
            if high >= sl:
                return sl, -1
            if low <= tp:
                return tp, 1

        exit_price = close

    # ===== TIME EXIT =====
    if signal == "BUY":
        pnl_dir = 1 if exit_price > entry_price else -1
    else:
        pnl_dir = 1 if exit_price < entry_price else -1

    return exit_price, pnl_dir
