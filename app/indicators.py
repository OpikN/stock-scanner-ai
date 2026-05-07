import pandas as pd

# =========================
# EMA
# =========================
def ema(series, period):

    return series.ewm(
        span=period,
        adjust=False
    ).mean()

# =========================
# RSI
# =========================
def rsi(series, period=14):

    delta = series.diff()

    gain = (
        delta.where(
            delta > 0,
            0
        )
    )

    loss = (
        -delta.where(
            delta < 0,
            0
        )
    )

    avg_gain = gain.rolling(
        period
    ).mean()

    avg_loss = loss.rolling(
        period
    ).mean()

    rs = avg_gain / avg_loss

    return (
        100 -
        (
            100 /
            (1 + rs)
        )
    )

# =========================
# ATR
# =========================
def atr(df, period=14):

    high_low = (
        df["High"] -
        df["Low"]
    )

    high_close = (
        (
            df["High"] -
            df["Close"].shift()
        )
        .abs()
    )

    low_close = (
        (
            df["Low"] -
            df["Close"].shift()
        )
        .abs()
    )

    ranges = pd.concat(

        [
            high_low,
            high_close,
            low_close
        ],

        axis=1
    )

    true_range = (
        ranges.max(axis=1)
    )

    return true_range.rolling(
        period
    ).mean()

# =========================
# MACD
# =========================
def macd(series):

    ema12 = ema(
        series,
        12
    )

    ema26 = ema(
        series,
        26
    )

    macd_line = (
        ema12 - ema26
    )

    signal_line = ema(
        macd_line,
        9
    )

    return (
        macd_line,
        signal_line
    )

# =========================
# APPLY INDICATORS
# =========================
def apply_indicators(df):

    try:

        # =========================
        # EMA
        # =========================
        df["EMA_FAST"] = ema(
            df["Close"],
            5
        )

        df["EMA_SLOW"] = ema(
            df["Close"],
            29
        )

        # =========================
        # RSI
        # =========================
        df["RSI"] = rsi(
            df["Close"]
        )

        # =========================
        # ATR
        # =========================
        df["ATR"] = atr(df)

        # =========================
        # MACD
        # =========================
        (
            df["MACD"],
            df["MACD_SIGNAL"]
        ) = macd(
            df["Close"]
        )

        # =========================
        # VOLUME MA
        # =========================
        df["VOL_MA"] = (
            df["Volume"]
            .rolling(20)
            .mean()
        )

        # =========================
        # CLEAN
        # =========================
        df = df.dropna()

        return df

    except Exception as e:

        print(
            f"INDICATOR ERROR: {e}"
        )

        return pd.DataFrame()
