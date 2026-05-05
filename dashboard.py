import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import time
import os

st.set_page_config(layout="wide")

st.title("📊 AI TRADING DASHBOARD PRO")

# =========================
# AUTO REFRESH 🔥
# =========================
refresh_rate = 10  # detik
st.caption(f"Auto refresh tiap {refresh_rate} detik")
time.sleep(refresh_rate)
st.rerun()

# =========================
# LOAD TRADE DATA
# =========================
if os.path.exists("trades.csv"):
    trades = pd.read_csv("trades.csv")
else:
    trades = pd.DataFrame()

# =========================
# PILIH STOCK
# =========================
stocks = ["BBCA.JK", "BBRI.JK", "TLKM.JK"]
selected = st.selectbox("Pilih Stock", stocks)

# =========================
# GET DATA LIVE
# =========================
df = yf.download(selected, period="1mo", interval="1h")

if df.empty:
    st.warning("Data tidak tersedia")
    st.stop()

# =========================
# CANDLESTICK CHART 🔥
# =========================
fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=df.index,
    open=df["Open"],
    high=df["High"],
    low=df["Low"],
    close=df["Close"],
    name="Price"
))

# =========================
# TAMBAH SIGNAL DARI CSV 🔥
# =========================
if not trades.empty:
    stock_trades = trades[trades["Stock"] == selected]

    for _, t in stock_trades.iterrows():
        fig.add_trace(go.Scatter(
            x=[pd.to_datetime(t["Time"], unit='s')],
            y=[t["Entry"]],
            mode="markers+text",
            marker=dict(size=12),
            text=[t["Signal"]],
            name="Signal"
        ))

# =========================
# LAYOUT CHART
# =========================
fig.update_layout(
    height=600,
    xaxis_rangeslider_visible=False,
    template="plotly_dark"
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# LIVE PRICE 🔥
# =========================
price = df["Close"].iloc[-1]
prev = df["Close"].iloc[-2]

col1, col2, col3 = st.columns(3)

col1.metric("💰 Harga", f"{price:.0f}", f"{price-prev:.0f}")
col2.metric("📊 High", f"{df['High'].iloc[-1]:.0f}")
col3.metric("📉 Low", f"{df['Low'].iloc[-1]:.0f}")

# =========================
# TRADE TABLE
# =========================
st.subheader("📜 Trade History")

if trades.empty:
    st.warning("Belum ada trade dari scanner")
else:
    st.dataframe(trades.tail(10))

# =========================
# STATUS SYSTEM
# =========================
st.subheader("🤖 System Status")

if trades.empty:
    st.info("Menunggu signal dari AI...")
else:
    last = trades.iloc[-1]
    st.success(f"Signal terakhir: {last['Stock']} {last['Signal']}")
