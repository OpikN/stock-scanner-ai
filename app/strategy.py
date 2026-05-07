import pandas as pd

# =========================
# SAFE FLOAT
# =========================
def safe_float(value):

    try:

        if isinstance(
            value,
            pd.Series
        ):

            return float(
                value.iloc[0]
            )

        return float(value)

    except:

        return 0

# =========================
# MARKET REGIME
# =========================
def detect_market_regime(df):

    try:

        close = safe_float(
            df["Close"].iloc[-1]
        )

        ema_fast = safe_float(
            df["EMA_FAST"].iloc[-1]
        )

        ema_slow = safe_float(
            df["EMA_SLOW"].iloc[-1]
        )

        atr = safe_float(
            df["ATR"].iloc[-1]
        )

        volatility = (
            atr / close
        )

        # =========================
        # TRENDING
        # =========================
        if (

            ema_fast > ema_slow

            and

            volatility > 0.015
        ):

            return "TRENDING"

        # =========================
        # SIDEWAYS
        # =========================
        if (

            abs(
                ema_fast - ema_slow
            ) / close

            < 0.01
        ):

            return "SIDEWAYS"

        return "WEAK"

    except Exception as e:

        print(
            f"REGIME ERROR: {e}"
        )

        return "UNKNOWN"

# =========================
# CONFIDENCE
# =========================
def calculate_confidence(df):

    try:

        confidence = 0

        ema_fast = safe_float(
            df["EMA_FAST"].iloc[-1]
        )

        ema_slow = safe_float(
            df["EMA_SLOW"].iloc[-1]
        )

        rsi = safe_float(
            df["RSI"].iloc[-1]
        )

        macd = safe_float(
            df["MACD"].iloc[-1]
        )

        macd_signal = safe_float(
            df["MACD_SIGNAL"].iloc[-1]
        )

        volume = safe_float(
            df["Volume"].iloc[-1]
        )

        volume_ma = safe_float(
            df["VOL_MA"].iloc[-1]
        )

        # =========================
        # EMA
        # =========================
        if ema_fast > ema_slow:

            confidence += 30

        # =========================
        # RSI
        # =========================
        if 40 <= rsi <= 65:

            confidence += 20

        # =========================
        # MACD
        # =========================
        if macd > macd_signal:

            confidence += 25

        # =========================
        # VOLUME
        # =========================
        if volume > volume_ma:

            confidence += 25

        return round(
            confidence,
            2
        )

    except Exception as e:

        print(
            f"CONFIDENCE ERROR: {e}"
        )

        return 0

# =========================
# SIGNAL
# =========================
def generate_signal(df):

    try:

        close = safe_float(
            df["Close"].iloc[-1]
        )

        ema_fast = safe_float(
            df["EMA_FAST"].iloc[-1]
        )

        ema_slow = safe_float(
            df["EMA_SLOW"].iloc[-1]
        )

        rsi = safe_float(
            df["RSI"].iloc[-1]
        )

        confidence = (
            calculate_confidence(df)
        )

        signal = "HOLD"

        # =========================
        # BUY
        # =========================
        if (

            ema_fast > ema_slow

            and

            rsi < 60
        ):

            signal = "BUY"

        # =========================
        # SELL
        # =========================
        elif (

            ema_fast < ema_slow

            and

            rsi > 40
        ):

            signal = "SELL"

        return (
            signal,
            close,
            confidence
        )

    except Exception as e:

        print(
            f"STRATEGY ERROR: {e}"
        )

        return (
            "HOLD",
            0,
            0
        )
