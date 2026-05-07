import pandas as pd

# =========================
# MARKET REGIME
# =========================
def detect_market_regime(df):

    try:

        close = float(
            df["Close"].iloc[-1]
        )

        ema_fast = float(
            df["EMA_FAST"].iloc[-1]
        )

        ema_slow = float(
            df["EMA_SLOW"].iloc[-1]
        )

        atr = float(
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

        # =========================
        # WEAK
        # =========================
        return "WEAK"

    except:

        return "UNKNOWN"

# =========================
# NEURAL CONFIDENCE
# =========================
def calculate_confidence(
    df
):

    try:

        confidence = 0

        ema_fast = float(
            df["EMA_FAST"].iloc[-1]
        )

        ema_slow = float(
            df["EMA_SLOW"].iloc[-1]
        )

        rsi = float(
            df["RSI"].iloc[-1]
        )

        macd = float(
            df["MACD"].iloc[-1]
        )

        macd_signal = float(
            df["MACD_SIGNAL"].iloc[-1]
        )

        volume = float(
            df["Volume"].iloc[-1]
        )

        volume_ma = float(
            df["VOL_MA"].iloc[-1]
        )

        # =========================
        # EMA TREND
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
# GENERATE SIGNAL
# =========================
def generate_signal(df):

    try:

        close = float(
            df["Close"].iloc[-1]
        )

        ema_fast = float(
            df["EMA_FAST"].iloc[-1]
        )

        ema_slow = float(
            df["EMA_SLOW"].iloc[-1]
        )

        rsi = float(
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
