import pandas as pd

from app.learning import (
    get_ai_learning_score
)

# =========================
# AI NEURAL SCORE
# =========================
def calculate_neural_score(df):

    try:

        last = df.iloc[-1]

        score = 0

        # =========================
        # EMA TREND
        # =========================
        if (
            last["EMA_FAST"]
            >
            last["EMA_SLOW"]
        ):

            score += 25

        # =========================
        # RSI
        # =========================
        rsi = float(last["RSI"])

        if 40 <= rsi <= 70:

            score += 20

        # =========================
        # MOMENTUM
        # =========================
        momentum = (
            last["Close"]
            -
            df["Close"].iloc[-5]
        )

        if momentum > 0:

            score += 15

        # =========================
        # VOLUME
        # =========================
        avg_vol = (
            df["Volume"]
            .tail(10)
            .mean()
        )

        if last["Volume"] > avg_vol:

            score += 10

        # =========================
        # VOLATILITY
        # =========================
        volatility = (
            df["Close"]
            .pct_change()
            .std()
        )

        if volatility < 0.03:

            score += 10

        # =========================
        # MARKET REGIME
        # =========================
        if (
            last["EMA_FAST"]
            >
            last["EMA_SLOW"]
        ):

            score += 10

        # =========================
        # AI LEARNING
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
            f"NEURAL SCORE ERROR: {e}"
        )

        return 0
