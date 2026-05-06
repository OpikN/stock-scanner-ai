import streamlit as st
import pandas as pd
import os
import json
import time

# =========================
# CONFIG
# =========================
DATA_PATH = "data/positions.csv"
STRATEGY_PATH = "data/strategy.json"
OPT_LOG = "data/last_opt.txt"

st.set_page_config(page_title="AI Trading Terminal", layout="wide")

# =========================
# LOAD FUNCTIONS
# =========================
def load_positions():
    if not os.path.exists(DATA_PATH):
        return pd.DataFrame()

    try:
        df = pd.read_csv(DATA_PATH)
        if df.empty:
            return pd.DataFrame()
        return df
    except Exception as e:
        st.error(f"Load error: {e}")
        return pd.DataFrame()


def load_strategy():
    if not os.path.exists(STRATEGY_PATH):
        return {}

    try:
        with open(STRATEGY_PATH, "r") as f:
            return json.load(f)
    except:
        return {}


def load_last_optimizer():
    if not os.path.exists(OPT_LOG):
        return "Optimizer belum jalan"

    try:
        t = os.path.getmtime(OPT_LOG)
        diff = int(time.time() - t)

        if diff < 60:
            return f"{diff} detik lalu"
        elif diff < 3600:
            return f"{diff // 60} menit lalu"
        else:
            return f"{diff // 3600} jam lalu"
    except:
        return "Error membaca optimizer"


def get_equity(df):
    if df.empty or "pnl" not in df.columns:
        return 100_000_000

    return int(100_000_000 + df["pnl"].sum())


# =========================
# LOAD DATA
# =========================
df = load_positions()
strategy = load_strategy()
last_opt = load_last_optimizer()

# =========================
# HEADER
# =========================
st.title("📊 AI TRADING TERMINAL")

# =========================
# ACCOUNT
# =========================
st.subheader("💰 Account")
equity = get_equity(df)
st.metric("Equity", f"{equity:,}")

# =========================
# AI MODE
# =========================
st.subheader("🧠 AI Mode")
st.write("Mode: SAFE")
st.write("Market: -")

# =========================
# STRATEGY
# =========================
st.subheader("🧠 AI Strategy")

if strategy:
    st.json(strategy)
else:
    st.info("Belum ada strategy")

# =========================
# BRAIN STATUS
# =========================
st.subheader("🧠 AI Brain Status")
st.write(f"Last Optimizer Run: {last_opt}")

# =========================
# ALL POSITIONS
# =========================
st.subheader("📂 All Positions")

if df.empty:
    st.info("Belum ada data posisi")
else:
    st.dataframe(df, use_container_width=True)

# =========================
# OPEN POSITIONS
# =========================
st.subheader("📡 Open Positions")

if df.empty:
    st.info("Tidak ada posisi terbuka")
else:
    open_df = df[df["status"] == "OPEN"]

    if open_df.empty:
        st.info("Tidak ada posisi terbuka")
    else:
        st.dataframe(open_df, use_container_width=True)

# =========================
# CLOSED PNL
# =========================
st.subheader("📈 Closed PnL")

if df.empty:
    st.info("Belum ada trade closed")
else:
    closed_df = df[df["status"] == "CLOSED"]

    if closed_df.empty:
        st.info("Belum ada trade closed")
    else:
        total_pnl = int(closed_df["pnl"].sum())
        st.metric("Total PnL", f"{total_pnl:,}")
        st.dataframe(closed_df, use_container_width=True)
