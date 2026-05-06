import streamlit as st
import pandas as pd
import os
import json
import time

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="AI Trading Terminal",
    layout="wide"
)

# =========================
# FILE PATH
# =========================
POSITIONS_FILE = "./data/positions.csv"
STRATEGY_FILE = "./data/strategy.json"
OPT_FILE = "./data/last_opt.txt"

# =========================
# LOAD POSITIONS
# =========================
def load_positions():

    if not os.path.exists(POSITIONS_FILE):
        st.error(f"File tidak ditemukan: {POSITIONS_FILE}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(POSITIONS_FILE)

        return df

    except Exception as e:
        st.error(f"Gagal baca CSV: {e}")
        return pd.DataFrame()

# =========================
# LOAD STRATEGY
# =========================
def load_strategy():

    if not os.path.exists(STRATEGY_FILE):
        return {}

    try:
        with open(STRATEGY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

# =========================
# LOAD OPTIMIZER STATUS
# =========================
def load_optimizer():

    if not os.path.exists(OPT_FILE):
        return "Optimizer belum jalan"

    try:
        diff = int(time.time() - os.path.getmtime(OPT_FILE))

        if diff < 60:
            return f"{diff} detik lalu"

        if diff < 3600:
            return f"{diff // 60} menit lalu"

        return f"{diff // 3600} jam lalu"

    except:
        return "Optimizer error"

# =========================
# LOAD DATA
# =========================
df = load_positions()
strategy = load_strategy()
optimizer = load_optimizer()

# =========================
# HEADER
# =========================
st.title("📊 AI TRADING TERMINAL")

# =========================
# ACCOUNT
# =========================
st.subheader("💰 Account")
st.metric("Equity", "100,000,000")

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
    st.warning("Strategy belum ada")

# =========================
# OPTIMIZER
# =========================
st.subheader("🧠 AI Brain Status")
st.write(f"Last Optimizer Run: {optimizer}")

# =========================
# ALL POSITIONS
# =========================
st.subheader("📂 All Positions")

if df.empty:
    st.warning("positions.csv kosong")
else:
    st.dataframe(df, use_container_width=True)

# =========================
# OPEN POSITIONS
# =========================
st.subheader("📡 Open Positions")

if not df.empty:

    if "status" in df.columns:

        open_df = df[df["status"] == "OPEN"]

        if open_df.empty:
            st.info("Tidak ada posisi OPEN")
        else:
            st.dataframe(open_df, use_container_width=True)

# =========================
# CLOSED POSITIONS
# =========================
st.subheader("📈 Closed PnL")

if not df.empty:

    if "status" in df.columns:

        closed_df = df[df["status"] == "CLOSED"]

        if closed_df.empty:
            st.info("Belum ada trade closed")
        else:
            st.dataframe(closed_df, use_container_width=True)
