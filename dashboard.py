import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import requests
import time
import traceback

st.set_page_config(layout="wide")
st.title("📊 AI TRADING TERMINAL")

STOCKS = ["BBCA.JK", "BBRI.JK", "TLKM.JK"]

# =========================
# SAFE FLOAT 🔥
# =========================
def safe_float(x):
    try:
        return float(x.values[0])
    except:
        return float(x)

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
# SCORE ENGINE (FIXED 🔥)
# =========================
def get_score(df):
    df["ema5"] = df["Close"].ewm(span=5).mean()
    df["ema10"] = df["Close"].ewm(span=10).mean()
    df["ema50"] = df["Close"].ewm(span=50).mean()

    last = df.iloc[-1:]

    ema5 = safe_float(last["ema5"])
    ema10 = safe_float(last["ema10"])
    ema50 = safe_float(last["ema50"])
    price = safe_float(last["Close"])

    score = 0

    score += 1 if ema5 > ema10 else -1
    score += 1 if price > ema50 else -1

    return score

# =========================
# TELEGRAM 🔥
# =========================
def get_telegram_updates():
    try:
        token = st.secrets.get("TELEGRAM_TOKEN", None)
        chat_id = st.secrets.get("TELEGRAM_CHAT_ID", None)

        if not token or not chat_id:
            return []

        url = f"https://api.telegram.org/bot{token}/getUpdates"
        res = requests.get(url).json()

        messages = []

        for item in res.get("result", []):
            msg = item.get("message", {})
            text = msg.get("text", "")
            cid = str(msg.get("chat", {}).get("id", ""))

            if cid == str(chat_id) and text:
                messages.append(text)

        return messages[-10:]
    except:
        return []

# =========================
# MAIN
# =========================
try:
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

    def color_signal(val):
        return "color: green" if val == "BUY" else "color: red"

    if not monitor_df.empty:
        st.dataframe(
            monitor_df.style.applymap(color_signal, subset=["Signal"]),
            use_container_width=True
        )

    # =========================
    # LEADERBOARD
    # =========================
    st.subheader("🏆 Leaderboard")

    if not monitor_df.empty:
        st.dataframe(
            monitor_df.sort_values(by="Score", ascending=False),
            use_container_width=True
        )

    # =========================
    # CHART
    # =========================
    st.subheader("📈 Chart")

    selected = st.selectbox("Pilih Stock", STOCKS)
    df = load_data(selected)

    if df is None:
        st.warning("Data kosong")
        st.stop()

    df["ema5"] = df["Close"].ewm(span=5).mean()
    df["ema10"] = df["Close"].ewm(span=10).mean()
    df["ema50"] = df["Close"].ewm(span=50).mean()

    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(7).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(7).mean()
    rs = gain / (loss + 1e-9)
    df["rsi"] = 100 - (100 / (1 + rs))

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.7, 0.3])

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"]
    ), row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df["ema5"], name="EMA5"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["ema10"], name="EMA10"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["ema50"], name="EMA50"), row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df["rsi"], name="RSI"), row=2, col=1)
    fig.add_hline(y=70, row=2, col=1)
    fig.add_hline(y=30, row=2, col=1)

    fig.update_layout(template="plotly_dark", height=700)

    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # TELEGRAM LIVE
    # =========================
    st.subheader("📡 Live Telegram Signal")

    msgs = get_telegram_updates()

    if not msgs:
        st.info("Belum ada signal Telegram")
    else:
        for m in reversed(msgs):
            if "BUY" in m:
                st.success(m)
            elif "SELL" in m:
                st.error(m)
            else:
                st.write(m)

    # =========================
    # REFRESH
    # =========================
    st.markdown("---")
    st.caption("🔄 Auto refresh aktif")

    time.sleep(5)
    st.rerun()

# =========================
# ERROR HANDLER
# =========================
except Exception as e:
    st.error("❌ ERROR")
    st.text(str(e))
    st.text(traceback.format_exc())
