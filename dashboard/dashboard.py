import streamlit as st
import pandas as pd
import os
import time

DATA_PATH = "data/trades.csv"

st.set_page_config(layout="wide")
st.title("📊 AI TRADING TERMINAL")

def load_data():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    return pd.DataFrame()

st.subheader("📡 Live Signal")

df = load_data()

if df.empty:
    st.warning("Belum ada data")
else:
    latest = df.tail(20)

    for _, row in latest[::-1].iterrows():
        text = f"{row['stock']} {row['signal']} @ {row['price']}"
        if row["signal"] == "BUY":
            st.success(text)
        else:
            st.error(text)

time.sleep(3)
st.rerun()
