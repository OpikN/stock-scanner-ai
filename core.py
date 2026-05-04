import yfinance as yf
import pandas as pd
import ta
import time
import math

STOCKS = ["BBCA.JK","BBRI.JK","TLKM.JK","BMRI.JK","ASII.JK"]
IHSG = "^JKSE"


# ===== GET DATA =====
def get_data(symbol):
    for _ in range(3):
        try:
            df = yf.download(
                symbol,
                period="6mo",
                interval="1d",
                progress=False
            )

            # VALIDASI
            if df is None or df.empty:
                time.sleep(2)
                continue

            # FIX MULTI INDEX
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # BUANG DATA KOSONG
            df = df.dropna()

            if df.empty:
                time.sleep(2)
                continue

            return df

        except Exception as e:
            print("ERROR GET DATA:", symbol, e)
            time.sleep(2)

    return None


# ===== COMPUTE INDICATOR =====
def compute(df):
    try:
        close = df["Close"]

        df["ema20"] = ta.trend.ema_indicator(close, window=20)
        df["ema50"] = ta.trend.ema_indicator(close, window=50)
        df["rsi"]   = ta.momentum.rsi(close, window=14)
        df["adx"]   = ta.trend.adx(df["High"], df["Low"], close, window=14)

        # BUANG NAN HASIL INDIKATOR
        df = df.dropna()

        return df

    except Exception as e:
        print("ERROR COMPUTE:", e)
        return None


# ===== MARKET REGIME =====
def get_market_regime(df):
    if df is None or df.empty:
        return "SIDEWAYS"

    r = df.iloc[-1]

    if pd.isna(r["ema20"]) or pd.isna(r["ema50"]) or pd.isna(r["adx"]):
        return "SIDEWAYS"

    if r["ema20"] > r["ema50"] and r["adx"] > 25:
        return "BULL"
    elif r["ema20"] < r["ema50"] and r["adx"] > 25:
        return "BEAR"

    return "SIDEWAYS"


# ===== SIGNAL =====
def signal(df):
    if df is None or df.empty:
        return "HOLD", None

    r = df.iloc[-1]

    price = r["Close"]

    # ===== FIX NAN PRICE =====
    if price is None or pd.isna(price):
        return "HOLD", None

    try:
        price = float(price)
    except:
        return "HOLD", None

    # VALIDASI INDIKATOR
    if pd.isna(r["ema20"]) or pd.isna(r["ema50"]):
        return "HOLD", price

    # ===== LOGIC =====
    if r["ema20"] > r["ema50"]:
        return "BUY", price
    elif r["ema20"] < r["ema50"]:
        return "SELL", price

    return "HOLD", price
