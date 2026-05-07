import pandas as pd

# =========================
# MARKET REGIME
# =========================
def detect_market_regime(df):

    try:

        close = df["Close"]

        if isinstance(close, pd.DataFrame):

            close = close.iloc[:, 0]

        ema_fast = close.ewm(span=20).mean()

        ema_slow = close.ewm(span=50).mean()

        volatility = (
            close.pct_change()
            .std() * 100
        )

        # TRENDING
        if ema_fast.iloc[-1] > ema_slow.iloc[-1]:

            if volatility < 1.5:

                return "TRENDING"

            return "VOLATILE"

        # PANIC
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
# RSI
# =========================
def calculate_rsi(close, period=14):

    delta = close.diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()

    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi

# =========================
# AI CONFIDENCE ENGINE
# =========================
def calculate_confidence(df):

    try:

        close = df["Close"]

        if isinstance(close, pd.DataFrame):

            close = close.iloc[:, 0]

        score = 50

        # =========================
        # EMA TREND
        # =========================
        ema_fast = close.ewm(span=20).mean()

        ema_slow = close.ewm(span=50).mean()

        if ema_fast.iloc[-1] > ema_slow.iloc[-1]:

            score += 20

        else:

            score -= 20

        # =========================
        # RSI
        # =========================
        rsi = calculate_rsi(close)

        last_rsi = rsi.iloc[-1]

        if 45 <= last_rsi <= 70:

            score += 15

        elif last_rsi > 80:

            score -= 15

        # =========================
        # MOMENTUM
        # =========================
        momentum = (
            close.iloc[-1] -
            close.iloc[-5]
        ) / close.iloc[-5]

        if momentum > 0:

            score += 10

        else:

            score -= 10

        # =========================
        # VOLATILITY
        # =========================
        volatility = (
            close.pct_change()
            .std() * 100
        )

        if volatility < 2:

            score += 10

        else:

            score -= 10

        # =========================
        # MARKET REGIME
        # =========================
        regime = detect_market_regime(df)

        if regime == "TRENDING":

            score += 15

        elif regime == "PANIC":

            score -= 25

        # LIMIT
        score = max(0, min(100, score))

        return round(score, 2)

    except:

        return 0

# =========================
# GENERATE SIGNAL
# =========================
def generate_signal(df):

    if df is None or df.empty:

        return "HOLD", 0, 0

    try:

        close = df["Close"]

        if isinstance(close, pd.DataFrame):

            close = close.iloc[:, 0]

        price = float(close.iloc[-1])

        regime = detect_market_regime(df)

        confidence = calculate_confidence(df)

        # =========================
        # BUY
        # =========================
        if regime == "TRENDING":

            if confidence >= 70:

                return "BUY", price, confidence

        # =========================
        # SELL
        # =========================
        if regime == "PANIC":

            return "SELL", price, confidence

        return "HOLD", price, confidence

    except:

        return "HOLD", 0, 0
