import streamlit as st
import pandas as pd
import os
import time
import json

st.set_page_config(layout="wide")

DATA_PATH = "data/trades.csv"
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


trades = load_csv(DATA_PATH)


# =========================
# AI MODE
# =========================
st.subheader("🧠 AI Live Mode")

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
# SIGNAL STREAM
# =========================
st.subheader("📡 Live Signal")

if trades.empty:
    st.warning("Belum ada signal")
else:
    latest = trades.tail(20)

    for _, row in latest.iloc[::-1].iterrows():
        text = f"{row['stock']} {row['signal']} @ {row['price']}"

        if row["signal"] == "BUY":
            st.success(text)
        elif row["signal"] == "SELL":
            st.error(text)
        else:
            st.info(text)


# =========================
# TABLE VIEW
# =========================
st.subheader("📋 Signal Table")

if not trades.empty:
    st.dataframe(trades.tail(50), use_container_width=True)


# =========================
# AUTO REFRESH
# =========================
time.sleep(5)
st.rerun()
