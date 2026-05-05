import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import traceback

st.set_page_config(layout="wide")
st.title("📊 AI TRADING TERMINAL")

# =========================
# CONFIG
# =========================
STOCKS = ["BBCA.JK", "BBRI.JK", "TLKM.JK"]

# =========================
# LOAD TRADES
# =========================
def load_trades():
    try:
        if os.path.exists("trades.csv"):
            return pd.read_csv("trades.csv")
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# =========================
# LOAD DATA
# =========================
def load_data(symbol):
    try:
        df = yf.download(symbol, period="1mo", interval="1h", progress=False)
        if df is None or df.empty:
            return None
        return df
    except:
        return None

# =========================
# SCORE ENGINE (LEADERBOARD)
# =========================
def get_score(df):
    df["ema5"] = df["Close"].ewm(span=5).mean()
    df["ema10"] = df["Close"].ewm(span=10).mean()
    df["ema50"] = df["Close"].ewm(span=50).mean()

    last = df.iloc[-1]

    score = 0

    if last["ema5"] > last["ema10"]:
        score += 1
    else:
        score -= 1

    if last["Close"] > last["ema50"]:
        score += 1
    else:
        score -= 1

    return score

# =========================
# MULTI COIN MONITOR 🔥
# =========================
st.subheader("📡 Market Monitor")

rows = []

for s in STOCKS:
    df = load_data(s)
    if df is None:
        continue

    score = get_score(df)

    price = df["Close"].iloc[-1]
    prev = df["Close"].iloc[-2]
    change = price - prev

    signal = "BUY" if score >= 1 else "SELL"

    rows.append({
        "Stock": s,
        "Price": round(price, 0),
        "Change": round(change, 0),
        "Signal": signal,
        "Score": score
    })

monitor_df = pd.DataFrame(rows)

# warna
def color_signal(val):
    if val == "BUY":
        return "color: green"
    return "color: red"

st.dataframe(
    monitor_df.style.applymap(color_signal, subset=["Signal"]),
    use_container_width=True
)

# =========================
# LEADERBOARD 🔥
# =========================
st.subheader("🏆 Leaderboard Signal")

if not monitor_df.empty:
    leaderboard = monitor_df.sort_values(by="Score", ascending=False)
    st.dataframe(leaderboard, use_container_width=True)

# =========================
# CHART DETAIL
# =========================
st.subheader("📈 Chart Detail")

selected = st.selectbox("Pilih Stock", STOCKS)

df = load_data(selected)

if df is None:
    st.error("Data tidak tersedia")
    st.stop()

# indikator
df["ema5"] = df["Close"].ewm(span=5).mean()
df["ema10"] = df["Close"].ewm(span=10).mean()
df["ema50"] = df["Close"].ewm(span=50).mean()

delta = df["Close"].diff()
gain = (delta.where(delta > 0, 0)).rolling(7).mean()
loss = (-delta.where(delta < 0, 0)).rolling(7).mean()
rs = gain / (loss + 1e-9)
df["rsi"] = 100 - (100 / (1 + rs))

# chart
fig = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.05,
    row_heights=[0.7, 0.3]
)

fig.add_trace(go.Candlestick(
    x=df.index,
    open=df["Open"],
    high=df["High"],
    low=df["Low"],
    close=df["Close"],
    name="Price"
), row=1, col=1)

fig.add_trace(go.Scatter(x=df.index, y=df["ema5"], name="EMA5"), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df["ema10"], name="EMA10"), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df["ema50"], name="EMA50"), row=1, col=1)

# RSI
fig.add_trace(go.Scatter(x=df.index, y=df["rsi"], name="RSI"), row=2, col=1)
fig.add_hline(y=70, row=2, col=1)
fig.add_hline(y=30, row=2, col=1)

fig.update_layout(
    height=700,
    template="plotly_dark",
    xaxis_rangeslider_visible=False
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# TRADE HISTORY
# =========================
st.subheader("📜 Trade History")

trades = load_trades()

if trades.empty:
    st.info("Belum ada trade")
else:
    st.dataframe(trades.tail(10), use_container_width=True)

# =========================
# REFRESH
# =========================
st.markdown("---")
if st.button("🔄 Refresh"):
    st.rerun()

# =========================
# ERROR HANDLER
# =========================
try:
    pass
except Exception as e:
    st.error("ERROR")
    st.text(str(e))
    st.text(traceback.format_exc())
