import yfinance as yf
import pandas as pd
import ta
import time
from ai_strategy import choose_strategy

STOCKS = ["BBCA.JK","BBRI.JK","TLKM.JK","BMRI.JK","ASII.JK"]
IHSG = "^JKSE"


def get_data(symbol):
    for _ in range(3):
        try:
            df = yf.download(symbol, period="6mo", interval="1d", progress=False)

            if df is None or df.empty:
                time.sleep(2)
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df = df.dropna()

            if df.empty:
                continue

            return df

        except:
            time.sleep(2)

    return None


def compute(df):
    try:
        close = df["Close"]

        df["ema20"] = ta.trend.ema_indicator(close, window=20)
        df["ema50"] = ta.trend.ema_indicator(close, window=50)
        df["rsi"]   = ta.momentum.rsi(close, window=14)
        df["adx"]   = ta.trend.adx(df["High"], df["Low"], close, window=14)

        df = df.dropna()
        return df

    except:
        return None


def get_market_regime(df):
    if df is None or df.empty:
        return "SIDEWAYS"

    r = df.iloc[-1]

    if r["ema20"] > r["ema50"] and r["adx"] > 25:
        return "BULL"

    elif r["ema20"] < r["ema50"] and r["adx"] > 25:
        return "BEAR"

    return "SIDEWAYS"


def signal(df):
    if df is None or len(df) < 2:
        return "HOLD", None

    r = df.iloc[-1]
    prev = df.iloc[-2]

    price = float(r["Close"])

    ema20 = r["ema20"]
    ema50 = r["ema50"]
    adx   = r["adx"]
    rsi   = r["rsi"]

    if pd.isna(ema20) or pd.isna(ema50) or pd.isna(adx):
        return "HOLD", price

    strategy = choose_strategy(df)

    # 🔥 TREND FLEX ENTRY
    if strategy == "TREND":

        if ema20 < ema50:
            if (r["Close"] < prev["Low"] or r["Close"] < ema20) and adx > 15:
                return "SELL", price

        if ema20 > ema50:
            if (r["Close"] > prev["High"] or r["Close"] > ema20) and adx > 15:
                return "BUY", price

    # 🔥 SIDEWAYS
    elif strategy == "SIDEWAYS":

        if rsi > 65:
            return "SELL", price

        if rsi < 35:
            return "BUY", price

    return "HOLD", price
