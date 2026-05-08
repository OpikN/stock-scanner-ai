import ta


def generate_signal(df):

    try:

        close = df["Close"]

        # =========================
        # EMA
        # =========================

        ema_fast = ta.trend.ema_indicator(

            close,

            window=10
        )

        ema_slow = ta.trend.ema_indicator(

            close,

            window=30
        )

        # =========================
        # RSI
        # =========================

        rsi = ta.momentum.rsi(

            close,

            window=14
        )

        # =========================
        # MACD
        # =========================

        macd = ta.trend.macd_diff(
            close
        )

        # =========================
        # LAST VALUES
        # =========================

        last_close = float(
            close.iloc[-1]
        )

        last_ema_fast = float(
            ema_fast.iloc[-1]
        )

        last_ema_slow = float(
            ema_slow.iloc[-1]
        )

        last_rsi = float(
            rsi.iloc[-1]
        )

        last_macd = float(
            macd.iloc[-1]
        )

        # =========================
        # DEFAULT
        # =========================

        signal = "HOLD"

        confidence = 25

        regime = "SIDEWAYS"

        # =========================
        # TREND
        # =========================

        if last_ema_fast > last_ema_slow:

            regime = "TRENDING"

            confidence += 25

        # =========================
        # RSI BOOST
        # =========================

        if last_rsi > 55:

            confidence += 25

        # =========================
        # MACD BOOST
        # =========================

        if last_macd > 0:

            confidence += 25

        # =========================
        # BUY SIGNAL
        # =========================

        if (

            last_ema_fast > last_ema_slow

            and

            last_rsi > 55

            and

            last_macd > 0
        ):

            signal = "BUY"

        # =========================
        # SELL SIGNAL
        # =========================

        elif (

            last_ema_fast < last_ema_slow

            and

            last_rsi < 45

            and

            last_macd < 0
        ):

            signal = "SELL"

        # =========================
        # WEAK MARKET
        # =========================

        if confidence < 50:

            regime = "WEAK"

        # =========================
        # RETURN
        # =========================

        return {

            "signal": signal,

            "confidence": confidence,

            "regime": regime,

            "price": last_close,

            "ema_fast": last_ema_fast,

            "ema_slow": last_ema_slow,

            "rsi": last_rsi,

            "macd": last_macd
        }

    except Exception as e:

        print(
            f"STRATEGY ERROR: {e}"
        )

        return {

            "signal": "HOLD",

            "confidence": 0,

            "regime": "UNKNOWN",

            "price": 0,

            "ema_fast": 0,

            "ema_slow": 0,

            "rsi": 0,

            "macd": 0
        }
