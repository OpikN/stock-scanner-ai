import streamlit as st
import pandas as pd
import json
import os
import time

# =========================
# PATH
# =========================
DATA_PATH = "data/positions.csv"
STATE_PATH = "data/state.json"
STRATEGY_PATH = "data/strategy.json"
OPT_PATH = "data/last_opt.txt"


# =========================
# LOAD FUNCTIONS
# =========================
def load_positions():
    if os.path.exists(DATA_PATH):
        try:
            return pd.read_csv(DATA_PATH)
        except:
            return pd.DataFrame()
    return pd.DataFrame()


def load_state():
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH) as f:
                return json.load(f)
        except:
            return {}
    return {}


def load_strategy():
    if os.path.exists(STRATEGY_PATH):
        try:
            with open(STRATEGY_PATH) as f:
                return json.load(f)
        except:
            return {}
    return {}


# =========================
# UI
# =========================
st.set_page_config(page_title="AI Trading Terminal", layout="wide")

st.title("📊 AI TRADING TERMINAL")

# =========================
# ACCOUNT
# =========================
st.subheader("💰 Account")
st.write("Equity")
st.write("100,000,000")


# =========================
# AI MODE
# =========================
st.subheader("🧠 AI Mode")

state = load_state()
mode = state.get("mode", "AI belum aktif")

st.write(f"Mode: {mode}")
st.write("Market: -")


# =========================
# STRATEGY
# =========================
st.subheader("🧠 AI Strategy")

strategy = load_strategy()

if strategy:
    st.json(strategy)
else:
    st.info("Belum ada strategy")


# =========================
# BRAIN STATUS (FIX ERROR 🔥)
# =========================
st.subheader("🧠 AI Brain Status")

try:
    if os.path.exists(OPT_PATH):
        with open(OPT_PATH) as f:
            content = f.read().strip()

            if content:
                last = float(content)
                minutes = int((time.time() - last) / 60)
                st.success(f"Last Optimizer Run: {minutes} menit lalu")
            else:
                st.warning("Optimizer belum jalan")
    else:
        st.warning("Optimizer belum pernah jalan")

except:
    st.error("Brain status error")


# =========================
# POSITIONS
# =========================
st.subheader("📂 All Positions")

df = load_positions()

if not df.empty:
    st.dataframe(df)
else:
    st.info("Belum ada data posisi")


# =========================
# OPEN POSITIONS
# =========================
st.subheader("📡 Open Positions")

if not df.empty and "status" in df.columns:
    open_pos = df[df["status"] == "OPEN"]
    if not open_pos.empty:
        st.dataframe(open_pos)
    else:
        st.info("Tidak ada posisi terbuka")
else:
    st.info("Tidak ada posisi terbuka")


# =========================
# CLOSED PNL
# =========================
st.subheader("📈 Closed PnL")

if not df.empty and "status" in df.columns:
    closed = df[df["status"] == "CLOSED"]

    if not closed.empty and "pnl" in closed.columns:
        total_pnl = closed["pnl"].sum()
        st.success(f"Total PnL: {round(total_pnl,2)}")
        st.dataframe(closed)
    else:
        st.info("Belum ada trade closed")
else:
    st.info("Belum ada trade closed")
