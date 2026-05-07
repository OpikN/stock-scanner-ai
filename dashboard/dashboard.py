import streamlit as st
import pandas as pd
import json
import os
import time
import yfinance as yf

from app.portfolio import (
    get_equity,
    get_live_equity,
    calculate_floating_pnl
)

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="AI Trading Terminal",
    layout="wide"
)

# =========================
# FILES
# =========================
POSITIONS_FILE = "data/positions.csv"
STRATEGY_FILE = "data/strategy.json"
OPT_FILE = "data/last_opt.txt"

# =========================
# LOAD POSITIONS
# =========================
def load_positions():

    try:

        if not os.path.exists(POSITIONS_FILE):
            st.error("positions.csv tidak ditemukan")
            return pd.DataFrame()

        df = pd.read_csv(
            POSITIONS_FILE,
            engine="python"
        )

        st.write("DEBUG ROWS:", len(df))

        return df

    except Exception as e:
        st.error(f"ERROR CSV: {e}")
        return pd.DataFrame()

# =========================
# LOAD STRATEGY
# =========================
def load_strategy():

    try:
        with open(STRATEGY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

# =========================
# OPTIMIZER STATUS
# =========================
def optimizer_status():

    try:

        if not os.path.exists(OPT_FILE):
            return "Belum pernah jalan"

        diff = int(time.time() - os.path.getmtime(OPT_FILE))

        if diff < 60:
            return f"{diff} detik lalu"

        if diff < 3600:
            return f"{diff // 60} menit lalu"

        return f"{diff // 3600} jam lalu"

    except:
        return "ERROR"

# =========================
# LOAD DATA
# =========================
df = load_positions()
strategy = load_strategy()

# =========================
# LIVE MARKET PRICE
# =========================
latest_prices = {}

try:

    tickers = ["BBCA.JK", "BBRI.JK", "TLKM.JK"]

    for t in tickers:

        data = yf.download(
            t,
            period="1d",
            interval="1m",
            progress=False
        )

        if not data.empty:

            latest_prices[t] = float(data["Close"].iloc[-1])

except:
    pass

# =========================
# LIVE EQUITY
# =========================
floating_pnl = calculate_floating_pnl(latest_prices)

live_equity = get_live_equity(latest_prices)

# =========================
# HEADER
# =========================
st.title("📊 AI TRADING TERMINAL")

# =========================
# ACCOUNT
# =========================
st.subheader("💰 Account")

st.metric(
    "Live Equity",
    f"{live_equity:,.0f}"
)

st.metric(
    "Floating PnL",
    f"{floating_pnl:,.0f}"
)

# =========================
# AI MODE
# =========================
st.subheader("🧠 AI Mode")
st.write("Mode: SAFE")
st.write("Market: LIVE")

# =========================
# STRATEGY
# =========================
st.subheader("🧠 AI Strategy")

if strategy:
    st.json(strategy)
else:
    st.warning("Strategy belum ada")

# =========================
# AI BRAIN
# =========================
st.subheader("🧠 AI Brain Status")
st.write(f"Last Optimizer Run: {optimizer_status()}")

# =========================
# RAW CSV DATA
# =========================
st.subheader("🛠 RAW CSV DATA")

if df.empty:
    st.error("DATAFRAME KOSONG")
else:

    st.markdown(
        df.astype(str).to_html(index=False),
        unsafe_allow_html=True
    )

# =========================
# ALL POSITIONS
# =========================
st.subheader("📂 All Positions")

if not df.empty:

    st.markdown(
        df.astype(str).to_html(index=False),
        unsafe_allow_html=True
    )

# =========================
# OPEN POSITIONS
# =========================
st.subheader("📡 Open Positions")

if not df.empty:

    if "status" in df.columns:

        open_df = df[df["status"] == "OPEN"]

        st.write("OPEN ROWS:", len(open_df))

        if open_df.empty:
            st.warning("Tidak ada OPEN")
        else:

            st.markdown(
                open_df.astype(str).to_html(index=False),
                unsafe_allow_html=True
            )

# =========================
# CLOSED POSITIONS
# =========================
st.subheader("📈 Closed PnL")

if not df.empty:

    if "status" in df.columns:

        closed_df = df[df["status"] == "CLOSED"]

        if closed_df.empty:
            st.info("Belum ada CLOSED")
        else:

            st.markdown(
                closed_df.astype(str).to_html(index=False),
                unsafe_allow_html=True
            )
