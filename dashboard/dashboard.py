import streamlit as st
import pandas as pd
import os
import time
import json

from app.portfolio import get_equity

st.set_page_config(layout="wide")

POSITIONS_PATH = "data/positions.csv"
STATE_PATH = "data/state.json"
STRATEGY_PATH = "data/strategy.json"

st.title("📊 AI TRADING TERMINAL")


# =========================
# LOAD CSV
# =========================
def load_csv(path):
    if os.path.exists(path):
        try:
            return pd.read_csv(path)
        except:
            return pd.DataFrame()
    return pd.DataFrame()


positions = load_csv(POSITIONS_PATH)


# =========================
# ACCOUNT
# =========================
st.subheader("💰 Account")

equity = get_equity()
st.metric("Equity", f"{equity:,.0f}")


# =========================
# AI MODE
# =========================
st.subheader("🧠 AI Mode")

if os.path.exists(STATE_PATH):
    try:
        with open(STATE_PATH) as f:
            state = json.load(f)

        st.success(f"Mode: {state.get('mode', '-')}")
        st.info(f"Market: {state.get('market', '-')}")
    except:
        st.warning("State error")
else:
    st.warning("AI belum aktif")


# =========================
# AI STRATEGY (SELF LEARNING)
# =========================
st.subheader("🧠 AI Strategy")

if os.path.exists(STRATEGY_PATH):
    try:
        with open(STRATEGY_PATH) as f:
            strat = json.load(f)

        st.json(strat)
    except:
        st.warning("Strategy error")
else:
    st.warning("Strategy belum tersedia")


# =========================
# POSITIONS TABLE
# =========================
st.subheader("📂 All Positions")

if positions.empty:
    st.warning("Belum ada posisi")
else:
    df = positions.copy()

    # risk sisa ke SL
    df["risk_left"] = abs(df["entry"] - df["sl"]) * df["qty"]

    st.dataframe(df.tail(50), use_container_width=True)


# =========================
# OPEN POSITIONS
# =========================
st.subheader("📡 Open Positions")

if not positions.empty:
    open_pos = positions[positions["status"] == "OPEN"]

    if not open_pos.empty:
        st.dataframe(open_pos, use_container_width=True)
    else:
        st.info("Tidak ada posisi aktif")


# =========================
# CLOSED PERFORMANCE
# =========================
st.subheader("📈 Closed PnL")

if not positions.empty:
    closed = positions[positions["status"] == "CLOSED"]

    if not closed.empty:
        closed = closed.copy()
        closed["cum_pnl"] = closed["pnl"].cumsum()
        st.line_chart(closed["cum_pnl"])
    else:
        st.info("Belum ada trade closed")


# =========================
# AUTO REFRESH
# =========================
time.sleep(5)
st.rerun()
