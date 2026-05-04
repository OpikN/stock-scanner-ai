import yfinance as yf
import pandas as pd
import ta
import time

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

            if df is None or df.empty:
                time.sleep(2)
                continue

            # FIX multi index
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # buang data kosong
            df = df.dropna()

            if df.empty:
                time.sleep(2)
                continue

            return df

        except Exception as e:
            print("ERROR GET DATA:", symbol, e)
            time.sleep(2)

    return None


# ===== COMPUTE =====
def compute(df):
    try:
        close = df["Close"]

        df["ema20"] = ta.trend.ema_indicator(close, window=20)
        df["ema50"] = ta.trend.ema_indicator(close, window=50)
        df["rsi"]   = ta.momentum.rsi(close, window=14)
        df["adx"]   = ta.trend.adx(df["High"], df["Low"], close, window=14)

        # buang NaN hasil indikator
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


# ===== SIGNAL (UPGRADE) =====
def signal(df):
    if df is None or df.empty:
        return "HOLD", None

    r = df.iloc[-1]

    price = r["Close"]

    # ===== VALIDASI PRICE =====
    if price is None or pd.isna(price):
        return "HOLD", None

    try:
        price = float(price)
    except:
        return "HOLD", None

    ema20 = r["ema20"]
    ema50 = r["ema50"]
    rsi   = r["rsi"]
    adx   = r["adx"]

    # ===== VALIDASI INDIKATOR =====
    if pd.isna(ema20) or pd.isna(ema50) or pd.isna(rsi) or pd.isna(adx):
        return "HOLD", price

    # ===== FILTER TREND LEMAH =====
    if adx < 20:
        return "HOLD", price

    # ===== FILTER ENTRY JELEK =====
    # hindari SELL saat terlalu oversold
    if rsi < 30:
        return "HOLD", price

    # hindari BUY saat terlalu overbought
    if rsi > 70:
        return "HOLD", price

    # ===== LOGIC KUAT =====
    if ema20 > ema50 and rsi > 50:
        return "BUY", price

    elif ema20 < ema50 and rsi < 50:
        return "SELL", price

    return "HOLD", price
