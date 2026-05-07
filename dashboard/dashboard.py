import streamlit as st
import pandas as pd
import json
import os
import time

st.set_page_config(layout="wide")

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

        # FORCE STRING SAFE
        df = pd.read_csv(
            POSITIONS_FILE,
            engine="python"
        )

        # DEBUG
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
# OPT STATUS
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
# LOAD
# =========================
df = load_positions()
strategy = load_strategy()

# =========================
# UI
# =========================
st.title("📊 AI TRADING TERMINAL")

# ACCOUNT
st.subheader("💰 Account")
st.metric("Equity", "100,000,000")

# MODE
st.subheader("🧠 AI Mode")
st.write("Mode: SAFE")
st.write("Market: -")

# STRATEGY
st.subheader("🧠 AI Strategy")
st.json(strategy)

# OPTIMIZER
st.subheader("🧠 AI Brain Status")
st.write(f"Last Optimizer Run: {optimizer_status()}")

# =========================
# RAW CSV DEBUG
# =========================
st.subheader("🛠 RAW CSV DATA")

if df.empty:
    st.error("DATAFRAME KOSONG")
else:
    st.dataframe(df)

# =========================
# ALL POSITIONS
# =========================
st.subheader("📂 All Positions")

if not df.empty:
    st.dataframe(df, use_container_width=True)

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
            st.dataframe(open_df, use_container_width=True)

# =========================
# CLOSED
# =========================
st.subheader("📈 Closed PnL")

if not df.empty:

    if "status" in df.columns:

        closed_df = df[df["status"] == "CLOSED"]

        if closed_df.empty:
            st.info("Belum ada CLOSED")
        else:
            st.dataframe(closed_df)
