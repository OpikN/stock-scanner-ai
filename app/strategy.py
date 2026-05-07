import pandas as pd

from app.neural_engine import (
    calculate_neural_score
)

# =========================
# SAFE VALUE
# =========================
def safe_float(value):

    try:

        if isinstance(value, pd.Series):

            return float(value.iloc[0])

        return float(value)

    except:

        return 0

# =========================
# MARKET REGIME
# =========================
def detect_market_regime(df):

    try:

        last = df.iloc[-1]

        ema_fast = safe_float(
            last["EMA_FAST"]
        )

        ema_slow = safe_float(
            last["EMA_SLOW"]
        )

        rsi = safe_float(
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

        return "SIDEWAYS"

    except Exception as e:

        print(
            f"REGIME ERROR: {e}"
        )

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
        # SAFE PRICE
        # =========================
        price = safe_float(
            last["Close"]
        )

        ema_fast = safe_float(
            last["EMA_FAST"]
        )

        ema_slow = safe_float(
            last["EMA_SLOW"]
        )

        rsi = safe_float(
            last["RSI"]
        )

        # =========================
        # NEURAL SCORE
        # =========================
        confidence = (
            calculate_neural_score(df)
        )

        # =========================
        # BUY
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
        # SELL
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
