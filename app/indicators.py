import pandas as pd

# =========================
# FIX YFINANCE COLUMNS
# =========================
def normalize_columns(df):

    try:

        # =========================
        # MULTI INDEX FIX
        # =========================
        if isinstance(
            df.columns,
            pd.MultiIndex
        ):

            df.columns = [

                col[0]

                for col in df.columns
            ]

        return df

    except:

        return df

# =========================
# APPLY INDICATORS
# =========================
def apply_indicators(df):

    try:

        if df is None:

            return df

        if df.empty:

            return df

        # =========================
        # NORMALIZE
        # =========================
        df = normalize_columns(df)

        # =========================
        # CLOSE FIX
        # =========================
        close = df["Close"]

        close = pd.to_numeric(

            close,

            errors="coerce"
        )

        # =========================
        # EMA FAST
        # =========================
        df["EMA_FAST"] = (

            close
            .ewm(span=5)
            .mean()
        )

        # =========================
        # EMA SLOW
        # =========================
        df["EMA_SLOW"] = (

            close
            .ewm(span=29)
            .mean()
        )

        # =========================
        # RSI
        # =========================
        delta = close.diff()

        gain = delta.clip(
            lower=0
        )

        loss = -delta.clip(
            upper=0
        )

        avg_gain = (
            gain
            .rolling(14)
            .mean()
        )

        avg_loss = (
            loss
            .rolling(14)
            .mean()
        )

        rs = avg_gain / avg_loss

        df["RSI"] = (

            100
            -
            (
                100
                /
                (1 + rs)
            )
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

        return df
