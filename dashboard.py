import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import os

st.set_page_config(layout="wide")
st.title("📊 AI TRADING DASHBOARD PRO")

# =========================
# AUTO REFRESH
# =========================
refresh = 10
st.caption(f"Auto refresh {refresh}s")
time.sleep(refresh)
st.rerun()

# =========================
# LOAD TRADE
# =========================
if os.path.exists("trades.csv"):
    trades = pd.read_csv("trades.csv")
else:
    trades = pd.DataFrame()

# =========================
# PILIH STOCK
# =========================
stocks = ["BBCA.JK", "BBRI.JK", "TLKM.JK"]
selected = st.selectbox("Stock", stocks)

# =========================
# DATA
# =========================
df = yf.download(selected, period="1mo", interval="1h")

if df.empty:
    st.warning("Data kosong")
    st.stop()

# =========================
# INDIKATOR 🔥
# =========================
df["ema5"] = df["Close"].ewm(span=5).mean()
df["ema10"] = df["Close"].ewm(span=10).mean()
df["ema50"] = df["Close"].ewm(span=50).mean()

delta = df["Close"].diff()
gain = (delta.where(delta > 0, 0)).rolling(7).mean()
loss = (-delta.where(delta < 0, 0)).rolling(7).mean()
rs = gain / (loss + 1e-9)
df["rsi"] = 100 - (100 / (1 + rs))

# =========================
# CHART (2 PANEL)
# =========================
fig = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.05,
    row_heights=[0.7, 0.3]
)

# 🔥 CANDLE
fig.add_trace(go.Candlestick(
    x=df.index,
    open=df["Open"],
    high=df["High"],
    low=df["Low"],
    close=df["Close"],
    name="Price"
), row=1, col=1)

# 🔥 EMA
fig.add_trace(go.Scatter(x=df.index, y=df["ema5"], name="EMA 5", line=dict(width=1)), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df["ema10"], name="EMA 10", line=dict(width=1)), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df["ema50"], name="EMA 50", line=dict(width=2)), row=1, col=1)

# =========================
# SIGNAL (WARNA 🔥)
# =========================
if not trades.empty:
    tdf = trades[trades["Stock"] == selected]

    for _, t in tdf.iterrows():
        color = "green" if t["Signal"] == "BUY" else "red"

        fig.add_trace(go.Scatter(
            x=[pd.to_datetime(t["Time"], unit='s')],
            y=[t["Entry"]],
            mode="markers+text",
            marker=dict(size=12, color=color),
            text=[t["Signal"]],
            name="Signal"
        ), row=1, col=1)

# =========================
# RSI PANEL 🔥
# =========================
fig.add_trace(go.Scatter(
    x=df.index,
    y=df["rsi"],
    name="RSI"
), row=2, col=1)

# garis RSI
fig.add_hline(y=70, line_dash="dash", row=2, col=1)
fig.add_hline(y=30, line_dash="dash", row=2, col=1)

# =========================
# LAYOUT
# =========================
fig.update_layout(
    height=700,
    template="plotly_dark",
    xaxis_rangeslider_visible=False
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# LIVE PRICE
# =========================
price = df["Close"].iloc[-1]
prev = df["Close"].iloc[-2]

col1, col2, col3 = st.columns(3)

col1.metric("💰 Price", f"{price:.0f}", f"{price-prev:.0f}")
col2.metric("📈 High", f"{df['High'].iloc[-1]:.0f}")
col3.metric("📉 Low", f"{df['Low'].iloc[-1]:.0f}")

# =========================
# HISTORY
# =========================
st.subheader("📜 Trade History")
if trades.empty:
    st.warning("Belum ada trade")
else:
    st.dataframe(trades.tail(10))
