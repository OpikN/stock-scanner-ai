import pandas as pd

# =========================
# MARKET REGIME DETECTOR
# =========================
def detect_market_regime(df):

    try:

        close = df["Close"]

        # =========================
        # HANDLE DATAFRAME
        # =========================
        if isinstance(close, pd.DataFrame):

            close = close.iloc[:, 0]

        # =========================
        # EMA
        # =========================
        ema_fast = close.ewm(span=20).mean()

        ema_slow = close.ewm(span=50).mean()

        # =========================
        # VOLATILITY
        # =========================
        volatility = close.pct_change().std() * 100

        # =========================
        # TRENDING
        # =========================
        if ema_fast.iloc[-1] > ema_slow.iloc[-1]:

            if volatility < 1.5:
                return "TRENDING"

            return "VOLATILE"

        # =========================
        # PANIC
        # =========================
        drop = (
            close.iloc[-1] -
            close.iloc[-5]
        ) / close.iloc[-5]

        if drop < -0.03:

            return "PANIC"

        return "SIDEWAYS"

    except:

        return "UNKNOWN"

# =========================
# GENERATE SIGNAL
# =========================
def generate_signal(df):

    if df is None or df.empty:

        return "HOLD", 0

    try:

        close = df["Close"]

        # dataframe fix
        if isinstance(close, pd.DataFrame):

            close = close.iloc[:, 0]

        price = float(close.iloc[-1])

        regime = detect_market_regime(df)

        # =========================
        # TRENDING
        # =========================
        if regime == "TRENDING":

            return "BUY", price

        # =========================
        # VOLATILE
        # =========================
        if regime == "VOLATILE":

            return "HOLD", price

        # =========================
        # PANIC
        # =========================
        if regime == "PANIC":

            return "SELL", price

        # =========================
        # SIDEWAYS
        # =========================
        return "HOLD", price

    except:

        return "HOLD", 0
