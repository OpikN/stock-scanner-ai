import yfinance as yf
import pandas as pd
import ta
import time

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

            return df
        except:
            time.sleep(2)
    return None


def compute(df):
    close = df["Close"]
    df["ema20"] = ta.trend.ema_indicator(close, 20)
    df["ema50"] = ta.trend.ema_indicator(close, 50)
    df["rsi"]   = ta.momentum.rsi(close, 14)
    df["adx"]   = ta.trend.adx(df["High"], df["Low"], close, 14)
    return df


def get_market_regime(df):
    r = df.iloc[-1]

    if r["ema20"] > r["ema50"] and r["adx"] > 25:
        return "BULL"
    elif r["ema20"] < r["ema50"] and r["adx"] > 25:
        return "BEAR"

    return "SIDEWAYS"


def signal(df):
    r = df.iloc[-1]
    price = float(r["Close"])

    if r["ema20"] > r["ema50"]:
        return "BUY", price
    elif r["ema20"] < r["ema50"]:
        return "SELL", price

    return "HOLD", price
