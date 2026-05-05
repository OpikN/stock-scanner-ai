import streamlit as st
import pandas as pd
import os
import time

st.set_page_config(layout="wide")

INITIAL_CAPITAL = 10000000
REFRESH_RATE = 5

# =========================
# AUTO CREATE FILE
# =========================
if not os.path.exists("trades.csv"):
    df_init = pd.DataFrame(columns=["Time","Stock","Signal","Entry","Exit","PnL"])
    df_init.to_csv("trades.csv", index=False)

# =========================
# MAIN LOOP (AUTO REFRESH)
# =========================
placeholder = st.empty()

while True:
    with placeholder.container():

        st.title("🔥 AI Trading Dashboard PRO (SYNC)")

        # =========================
        # LOAD DATA
        # =========================
        df = pd.read_csv("trades.csv")

        if not df.empty:

            # CLEAN DATA
            df["PnL"] = pd.to_numeric(df["PnL"], errors="coerce").fillna(0)
            df["Time"] = pd.to_numeric(df["Time"], errors="coerce")

            df = df.sort_values("Time", ascending=False)

            # EQUITY
            df["Equity"] = df["PnL"].cumsum() + INITIAL_CAPITAL

            # =========================
            # METRICS
            # =========================
            total = len(df)
            win = len(df[df["PnL"] > 0])
            loss = len(df[df["PnL"] <= 0])
            winrate = (win / total) * 100 if total > 0 else 0
            equity = df["Equity"].iloc[0]

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("💰 Equity", f"{int(equity):,}")
            c2.metric("📊 Trades", total)
            c3.metric("🏆 Winrate", f"{winrate:.2f}%")
            c4.metric("❌ Loss", loss)

            st.divider()

            # =========================
            # LAST SIGNAL
            # =========================
            last = df.iloc[0]

            color = "green" if last["PnL"] > 0 else "red"

            st.subheader("📡 Last Signal")

            st.markdown(f"""
            **Stock:** {last['Stock']}  
            **Signal:** :{color}[{last['Signal']}]  
            **Entry:** {last['Entry']}  
            **Exit:** {last['Exit']}  
            **PnL:** {last['PnL']}  
            """)

            st.divider()

            # =========================
            # EQUITY CURVE
            # =========================
            st.subheader("📈 Equity Curve")

            df_sorted = df.sort_values("Time")
            st.line_chart(df_sorted["Equity"])

            st.divider()

            # =========================
            # PERFORMANCE DETAIL
            # =========================
            st.subheader("📊 Performance Detail")

            avg_win = df[df["PnL"] > 0]["PnL"].mean()
            avg_loss = df[df["PnL"] < 0]["PnL"].mean()
            expectancy = df["PnL"].mean()

            c1, c2, c3 = st.columns(3)
            c1.metric("📈 Avg Win", f"{avg_win:.0f}" if not pd.isna(avg_win) else "0")
            c2.metric("📉 Avg Loss", f"{avg_loss:.0f}" if not pd.isna(avg_loss) else "0")
            c3.metric("🎯 Expectancy", f"{expectancy:.0f}")

            st.divider()

            # =========================
            # TRADE HISTORY
            # =========================
            st.subheader("🧾 Trade History")

            def highlight(val):
                color = "green" if val > 0 else "red"
                return f"color: {color}"

            st.dataframe(
                df.head(20).style.applymap(highlight, subset=["PnL"])
            )

        else:
            st.warning("Belum ada data trade dari scanner.py")

    time.sleep(REFRESH_RATE)
    st.rerun()
