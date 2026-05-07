import pandas as pd

from app.learning import (
    get_ai_learning_score
)

# =========================
# SAFE FLOAT
# =========================
def safe_float(value):

    try:

        if isinstance(value, pd.Series):

            return float(value.iloc[0])

        return float(value)

    except:

        return 0

# =========================
# AI NEURAL SCORE
# =========================
def calculate_neural_score(df):

    try:

        if df is None:

            return 0

        if df.empty:

            return 0

        if len(df) < 20:

            return 0

        last = df.iloc[-1]

        score = 0

        # =========================
        # EMA
        # =========================
        ema_fast = safe_float(
            last["EMA_FAST"]
        )

        ema_slow = safe_float(
            last["EMA_SLOW"]
        )

        if ema_fast > ema_slow:

            score += 25

        # =========================
        # RSI
        # =========================
        rsi = safe_float(
            last["RSI"]
        )

        if 40 <= rsi <= 70:

            score += 20

        # =========================
        # MOMENTUM
        # =========================
        close_now = safe_float(
            last["Close"]
        )

        close_prev = safe_float(
            df["Close"].iloc[-5]
        )

        momentum = (
            close_now
            -
            close_prev
        )

        if momentum > 0:

            score += 15

        # =========================
        # VOLUME
        # =========================
        try:

            volume_now = safe_float(
                last["Volume"]
            )

            avg_vol = safe_float(

                df["Volume"]
                .tail(10)
                .mean()
            )

            if volume_now > avg_vol:

                score += 10

        except:

            pass

        # =========================
        # VOLATILITY
        # =========================
        try:

            volatility = (

                df["Close"]
                .pct_change()
                .std()
            )

            volatility = safe_float(
                volatility
            )

            if volatility < 0.03:

                score += 10

        except:

            pass

        # =========================
        # LEARNING SCORE
        # =========================
        learning = (
            get_ai_learning_score()
        )

        score += (
            learning * 0.1
        )

        # =========================
        # LIMIT
        # =========================
        if score > 100:

            score = 100

        return round(score, 2)

    except Exception as e:

        print(
            f"NEURAL ERROR: {e}"
        )

        return 0
