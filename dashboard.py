import streamlit as st
import pandas as pd
import os
import time

st.set_page_config(layout="wide")

INITIAL_CAPITAL = 10000000
REFRESH_RATE = 5

TRADE_FILE = "trades.csv"
LOG_FILE = "scanner_log.csv"

# =========================
# INIT
# =========================
if not os.path.exists(TRADE_FILE):
    pd.DataFrame(columns=["Time","Stock","Signal","Entry","Exit","PnL"]).to_csv(TRADE_FILE, index=False)

placeholder = st.empty()

while True:
    with placeholder.container():

        st.title("🔥 AI Trading Dashboard PRO (LIVE)")

        # =========================
        # STATUS
        # =========================
        c1, c2 = st.columns(2)
        c1.metric("🧠 Scanner", "RUNNING")
        c2.metric("⏱️ Last Update", time.strftime("%H:%M:%S"))

        st.divider()

        # =========================
        # LIVE SCANNER LOG
        # =========================
        st.subheader("⚡ Live Scanner Activity")

        if os.path.exists(LOG_FILE):
            log_df = pd.read_csv(LOG_FILE)

            if not log_df.empty:
                log_df = log_df.sort_values("Time", ascending=False)

                def color(val):
                    if val == "BUY":
                        return "color: green"
                    elif val == "SELL":
                        return "color: red"
                    return "color: gray"

                st.dataframe(
                    log_df.head(20).style.applymap(color, subset=["Signal"])
                )
            else:
                st.info("Scanner aktif... belum ada data")
        else:
            st.warning("Log belum ada")

        st.divider()

        # =========================
        # TRADES
        # =========================
        st.subheader("📊 Trade Performance")

        df = pd.read_csv(TRADE_FILE)

        if not df.empty:
            df["PnL"] = pd.to_numeric(df["PnL"], errors="coerce")
            df["Equity"] = df["PnL"].cumsum() + INITIAL_CAPITAL

            total = len(df)
            win = len(df[df["PnL"] > 0])
            winrate = (win / total) * 100 if total > 0 else 0
            equity = df["Equity"].iloc[-1]

            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Equity", f"{int(equity):,}")
            c2.metric("📊 Trades", total)
            c3.metric("🏆 Winrate", f"{winrate:.2f}%")

            st.line_chart(df["Equity"])

        else:
            st.warning("Belum ada trade")

    time.sleep(REFRESH_RATE)
    st.rerun()
