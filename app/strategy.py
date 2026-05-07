import pandas as pd

from app.neural_engine import (
    calculate_neural_score
)

# =========================
# MARKET REGIME
# =========================
def detect_market_regime(df):

    try:

        last = df.iloc[-1]

        ema_fast = float(
            last["EMA_FAST"]
        )

        ema_slow = float(
            last["EMA_SLOW"]
        )

        rsi = float(
            last["RSI"]
        )

        # =========================
        # TRENDING
        # =========================
        if (
            ema_fast > ema_slow
            and
            rsi > 55
        ):

            return "TRENDING"

        # =========================
        # WEAK
        # =========================
        if (
            ema_fast < ema_slow
            and
            rsi < 45
        ):

            return "WEAK"

        # =========================
        # SIDEWAYS
        # =========================
        return "SIDEWAYS"

    except:

        return "UNKNOWN"

# =========================
# GENERATE SIGNAL
# =========================
def generate_signal(df):

    try:

        # =========================
        # VALIDATION
        # =========================
        if df is None:

            return (
                "HOLD",
                0,
                0
            )

        if df.empty:

            return (
                "HOLD",
                0,
                0
            )

        if len(df) < 20:

            return (
                "HOLD",
                0,
                0
            )

        # =========================
        # LAST ROW
        # =========================
        last = df.iloc[-1]

        # =========================
        # PRICE FIX
        # =========================
        close = last["Close"]

        if hasattr(close, "iloc"):

            if len(close.shape) > 0:

                price = float(
                    close.iloc[0]
                )

            else:

                price = float(close)

        else:

            price = float(close)

        # =========================
        # INDICATORS
        # =========================
        ema_fast = float(
            last["EMA_FAST"]
        )

        ema_slow = float(
            last["EMA_SLOW"]
        )

        rsi = float(
            last["RSI"]
        )

        # =========================
        # AI NEURAL SCORE
        # =========================
        confidence = (
            calculate_neural_score(df)
        )

        # =========================
        # BUY SIGNAL
        # =========================
        if (

            ema_fast > ema_slow

            and

            rsi > 50

            and

            confidence >= 70
        ):

            return (

                "BUY",

                round(price, 2),

                round(confidence, 2)
            )

        # =========================
        # SELL SIGNAL
        # =========================
        if (

            ema_fast < ema_slow

            and

            rsi < 45

            and

            confidence >= 70
        ):

            return (

                "SELL",

                round(price, 2),

                round(confidence, 2)
            )

        # =========================
        # HOLD
        # =========================
        return (

            "HOLD",

            round(price, 2),

            round(confidence, 2)
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
