import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt

TRADES_FILE = "trades.csv"
START_CAPITAL = 10_000_000

st.set_page_config(page_title="AI Trading Dashboard", layout="wide")

st.title("📊 AI Trading Dashboard")

if not os.path.exists(TRADES_FILE):
    st.warning("Belum ada data trades")
    st.stop()

df = pd.read_csv(TRADES_FILE)

# ===== CLEAN =====
df = df.dropna()
df["PnL"] = pd.to_numeric(df["PnL"], errors="coerce")

# ===== EQUITY =====
df["CumulativePnL"] = df["PnL"].cumsum()
df["Equity"] = START_CAPITAL + df["CumulativePnL"]

# ===== METRICS =====
total_trade = len(df)
win = len(df[df["PnL"] > 0])
loss = len(df[df["PnL"] <= 0])
winrate = (win / total_trade) * 100 if total_trade > 0 else 0
equity = df["Equity"].iloc[-1]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Trade", total_trade)
col2.metric("Winrate", f"{round(winrate,2)}%")
col3.metric("Equity", f"{int(equity)}")
col4.metric("Net PnL", f"{int(df['PnL'].sum())}")

# ===== EQUITY CURVE =====
st.subheader("📈 Equity Curve")

fig = plt.figure()
plt.plot(df["Equity"])
plt.title("Equity Growth")
plt.xlabel("Trade #")
plt.ylabel("Equity")
st.pyplot(fig)

# ===== PNL CHART =====
st.subheader("💰 PnL Curve")

fig2 = plt.figure()
plt.plot(df["CumulativePnL"])
plt.title("Cumulative PnL")
plt.xlabel("Trade #")
plt.ylabel("PnL")
st.pyplot(fig2)

# ===== TABLE =====
st.subheader("📋 Trade History")
st.dataframe(df)
