import sys
import os

# =========================
# FIX IMPORT PATH
# =========================
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

import streamlit as st
import pandas as pd
import json
import time
import yfinance as yf

from app.portfolio import (
    get_equity,
    get_live_equity,
    calculate_floating_pnl
)

from app.strategy import (
    detect_market_regime
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

            st.error(
                "positions.csv tidak ditemukan"
            )

            return pd.DataFrame()

        df = pd.read_csv(
            POSITIONS_FILE,
            engine="python"
        )

        st.write(
            "DEBUG ROWS:",
            len(df)
        )

        return df

    except Exception as e:

        st.error(
            f"ERROR CSV: {e}"
        )

        return pd.DataFrame()

# =========================
# LOAD STRATEGY
# =========================
def load_strategy():

    try:

        with open(
            STRATEGY_FILE,
            "r"
        ) as f:

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

        diff = int(
            time.time() -
            os.path.getmtime(OPT_FILE)
        )

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

market_regime = "UNKNOWN"

try:

    tickers = [
        "BBCA.JK",
        "BBRI.JK",
        "TLKM.JK"
    ]

    for t in tickers:

        # =========================
        # LIVE PRICE
        # =========================
        data = yf.download(
            t,
            period="1d",
            interval="1m",
            progress=False
        )

        if not data.empty:

            close_data = data["Close"]

            # dataframe
            if isinstance(
                close_data,
                pd.DataFrame
            ):

                latest_prices[t] = float(
                    close_data.iloc[-1, 0]
                )

            # series
            elif isinstance(
                close_data,
                pd.Series
            ):

                latest_prices[t] = float(
                    close_data
                    .dropna()
                    .iloc[-1]
                )

            else:

                latest_prices[t] = float(
                    close_data
                )

        # =========================
        # MARKET REGIME
        # =========================
        regime_df = yf.download(
            t,
            period="5d",
            interval="1h",
            progress=False
        )

        market_regime = detect_market_regime(
            regime_df
        )

        break

except Exception as e:

    st.error(
        f"MARKET ERROR: {e}"
    )

# =========================
# LIVE EQUITY
# =========================
floating_pnl = calculate_floating_pnl(
    latest_prices
)

live_equity = get_live_equity(
    latest_prices
)

closed_equity = get_equity()

# =========================
# HEADER
# =========================
st.title(
    "📊 AI TRADING TERMINAL"
)

# =========================
# ACCOUNT
# =========================
st.subheader(
    "💰 Account"
)

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Closed Equity",
        f"{closed_equity:,.0f}"
    )

with col2:

    st.metric(
        "Live Equity",
        f"{live_equity:,.0f}"
    )

with col3:

    st.metric(
        "Floating PnL",
        f"{floating_pnl:,.0f}"
    )

# =========================
# AI MODE
# =========================
st.subheader(
    "🧠 AI Mode"
)

if market_regime == "TRENDING":

    ai_mode = "AGGRESSIVE"

elif market_regime == "VOLATILE":

    ai_mode = "CAUTIOUS"

elif market_regime == "PANIC":

    ai_mode = "DEFENSIVE"

else:

    ai_mode = "SAFE"

st.write(
    f"Mode: {ai_mode}"
)

st.write(
    f"Market Regime: "
    f"{market_regime}"
)

# =========================
# AI STRATEGY
# =========================
st.subheader(
    "🧠 AI Strategy"
)

if strategy:

    st.json(strategy)

else:

    st.warning(
        "Strategy belum ada"
    )

# =========================
# AI BRAIN
# =========================
st.subheader(
    "🧠 AI Brain Status"
)

st.write(
    f"Last Optimizer Run: "
    f"{optimizer_status()}"
)

# =========================
# RAW CSV
# =========================
st.subheader(
    "🛠 RAW CSV DATA"
)

if df.empty:

    st.error(
        "DATAFRAME KOSONG"
    )

else:

    st.dataframe(df)

# =========================
# ALL POSITIONS
# =========================
st.subheader(
    "📂 All Positions"
)

if not df.empty:

    st.dataframe(df)

# =========================
# OPEN POSITIONS
# =========================
st.subheader(
    "📡 Open Positions"
)

if not df.empty:

    if "status" in df.columns:

        open_df = df[
            df["status"] == "OPEN"
        ]

        st.write(
            "OPEN ROWS:",
            len(open_df)
        )

        if open_df.empty:

            st.warning(
                "Tidak ada posisi OPEN"
            )

        else:

            st.dataframe(open_df)

# =========================
# CLOSED POSITIONS
# =========================
st.subheader(
    "📈 Closed PnL"
)

if not df.empty:

    if "status" in df.columns:

        closed_df = df[
            df["status"] == "CLOSED"
        ]

        if closed_df.empty:

            st.info(
                "Belum ada CLOSED"
            )

        else:

            st.dataframe(
                closed_df
            )

            total_closed = (
                closed_df["pnl"]
                .astype(float)
                .sum()
            )

            st.success(
                f"TOTAL CLOSED PNL: "
                f"{total_closed:,.0f}"
            )

# =========================
# FOOTER
# =========================
st.markdown("---")

st.caption(
    "🔥 REAL MARKET REGIME AI ACTIVE"
)
