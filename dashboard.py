import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt

TRADES_FILE = "trades.csv"
START_CAPITAL = 10_000_000

st.title("📊 AI Trading Dashboard")

if not os.path.exists(TRADES_FILE):
    st.warning("Belum ada data trades")
    st.stop()

df = pd.read_csv(TRADES_FILE)

df["PnL"] = pd.to_numeric(df["PnL"], errors="coerce")
df = df.dropna()

df["CumulativePnL"] = df["PnL"].cumsum()
df["Equity"] = START_CAPITAL + df["CumulativePnL"]

st.subheader("📈 Equity Curve")
st.line_chart(df["Equity"])

st.subheader("💰 PnL")
st.line_chart(df["CumulativePnL"])

st.subheader("📋 Trades")
st.dataframe(df)
