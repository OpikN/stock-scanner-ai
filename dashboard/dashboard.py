import streamlit as st
import pandas as pd
import os
import time
import json

from app.portfolio import get_equity

st.set_page_config(layout="wide")

DATA_PATH = "data/positions.csv"
STATE_PATH = "data/state.json"

st.title("📊 AI TRADING TERMINAL")


# =========================
# LOAD DATA
# =========================
def load_csv(path):
    if os.path.exists(path):
        try:
            return pd.read_csv(path)
        except:
            return pd.DataFrame()
    return pd.DataFrame()


positions = load_csv(DATA_PATH)


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
# POSITIONS
# =========================
st.subheader("📂 Positions")

if positions.empty:
    st.warning("Belum ada posisi")
else:
    st.dataframe(positions.tail(50), use_container_width=True)


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
# CLOSED PNL
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
