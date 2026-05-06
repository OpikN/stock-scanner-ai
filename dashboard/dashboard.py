import streamlit as st
import pandas as pd
import os
import time

from app.portfolio import get_stats

st.set_page_config(layout="wide")

DATA_PATH = "data/trades.csv"
POSITIONS_PATH = "data/positions.csv"

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
positions = load_csv(POSITIONS_PATH)


# =========================
# STATS
# =========================
stats = get_stats()

col1, col2, col3, col4 = st.columns(4)

col1.metric("📊 Trades", stats["trades"])
col2.metric("🎯 Winrate %", stats["winrate"])
col3.metric("💰 Total PnL", stats["total_pnl"])
col4.metric("🏦 Equity", stats["equity"])


# =========================
# LIVE SIGNAL
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
        else:
            st.error(text)


# =========================
# POSITIONS
# =========================
st.subheader("📂 Positions")

if positions.empty:
    st.warning("Belum ada posisi")
else:
    st.dataframe(positions.tail(20), use_container_width=True)


# =========================
# ACTIVE RISK VIEW
# =========================
st.subheader("🛡️ Active Risk")

if not positions.empty:
    open_pos = positions[positions["status"] == "OPEN"]

    if not open_pos.empty:
        st.dataframe(open_pos[["stock","entry","sl","tp","qty"]])
    else:
        st.info("Tidak ada posisi aktif")


# =========================
# EQUITY CURVE
# =========================
st.subheader("📈 Equity Curve")

if not positions.empty:
    closed = positions[positions["status"] == "CLOSED"]

    if not closed.empty:
        closed = closed.copy()
        closed["cum_pnl"] = closed["pnl"].cumsum()
        st.line_chart(closed["cum_pnl"])
    else:
        st.info("Belum ada trade closed")


# =========================
# AUTO REFRESH
# =========================
time.sleep(5)
st.rerun()
