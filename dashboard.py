import streamlit as st
import pandas as pd
import numpy as np
import time

st.set_page_config(layout="wide")

INITIAL_CAPITAL = 10000000

# AUTO REFRESH
refresh_rate = 10  # detik

placeholder = st.empty()

while True:
    with placeholder.container():

        st.markdown("## 🔥 AI Opik Trading PRO")

        # =========================
        # LOAD DATA
        # =========================
        try:
            df = pd.read_csv("trades.csv")
        except:
            st.warning("trades.csv belum ada")
            time.sleep(refresh_rate)
            st.rerun()

        if df.empty:
            st.warning("Belum ada trade")
            time.sleep(refresh_rate)
            st.rerun()

        # =========================
        # PREP DATA
        # =========================
        df["PnL"] = pd.to_numeric(df["PnL"], errors="coerce")
        df["Equity"] = df["PnL"].cumsum() + INITIAL_CAPITAL

        df["Win"] = df["PnL"] > 0

        # =========================
        # METRICS
        # =========================
        total = len(df)
        win = df["Win"].sum()
        loss = total - win
        winrate = (win / total) * 100 if total > 0 else 0

        avg_win = df[df["PnL"] > 0]["PnL"].mean() if win > 0 else 0
        avg_loss = df[df["PnL"] < 0]["PnL"].mean() if loss > 0 else 0

        expectancy = (winrate/100 * avg_win) + ((1 - winrate/100) * avg_loss)

        equity = df["Equity"].iloc[-1]

        # DRAW DOWN
        peak = df["Equity"].cummax()
        drawdown = df["Equity"] - peak
        max_dd = drawdown.min()

        # =========================
        # TOP METRICS
        # =========================
        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric("💰 Equity", f"{int(equity):,}")
        col2.metric("📊 Trades", total)
        col3.metric("🏆 Winrate", f"{winrate:.2f}%")
        col4.metric("📈 Expectancy", round(expectancy, 2))
        col5.metric("⚠️ Max DD", int(max_dd))

        st.divider()

        # =========================
        # CHARTS
        # =========================
        colA, colB = st.columns(2)

        with colA:
            st.subheader("💰 Equity Curve")
            st.line_chart(df["Equity"])

        with colB:
            st.subheader("📉 Drawdown")
            st.line_chart(drawdown)

        st.divider()

        # =========================
        # DAILY PNL
        # =========================
        st.subheader("📊 Daily PnL")
        df["Date"] = pd.date_range(end=pd.Timestamp.today(), periods=len(df))
        daily = df.groupby(df["Date"].dt.date)["PnL"].sum()

        st.bar_chart(daily)

        st.divider()

        # =========================
        # FILTER STOCK
        # =========================
        st.subheader("🔍 Filter per Saham")

        stocks = df["Stock"].unique()
        selected = st.selectbox("Pilih Saham", stocks)

        df_stock = df[df["Stock"] == selected]

        colC, colD = st.columns(2)

        with colC:
            st.write("Trade Detail")
            st.dataframe(df_stock.tail(10))

        with colD:
            st.write("Equity per Saham")
            st.line_chart(df_stock["PnL"].cumsum())

        st.divider()

        # =========================
        # DISTRIBUTION
        # =========================
        st.subheader("📊 PnL Distribution")
        st.bar_chart(df["PnL"])

        st.divider()

        # =========================
        # TRADE TABLE
        # =========================
        st.subheader("🧾 Last Trades")

        def highlight_pnl(val):
            color = "green" if val > 0 else "red"
            return f"color: {color}"

        st.dataframe(
            df.tail(15).style.applymap(highlight_pnl, subset=["PnL"])
        )

    time.sleep(refresh_rate)
