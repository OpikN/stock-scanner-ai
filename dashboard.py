import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
import os

st.set_page_config(layout="wide")

INITIAL_CAPITAL = 10000000
REFRESH_RATE = 5

# =========================
# AUTO CREATE trades.csv
# =========================
if not os.path.exists("trades.csv"):
    df_init = pd.DataFrame(columns=["Stock","Signal","Entry","Exit","PnL"])
    df_init.to_csv("trades.csv", index=False)

# =========================
# COINS
# =========================
COINS = ["bitcoin", "ethereum", "solana"]

# =========================
# GET LIVE PRICE (SAFE)
# =========================
def get_prices():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": ",".join(COINS),
            "vs_currencies": "usd"
        }
        res = requests.get(url, params=params, timeout=5)
        return res.json()
    except:
        return {}

# =========================
# PERFORMANCE MODE
# =========================
def get_performance_mode(df):
    if len(df) < 10:
        return "BALANCED"

    recent = df.tail(10)
    win = len(recent[recent["PnL"] > 0])
    winrate = win / len(recent) * 100

    if winrate >= 70:
        return "AGGRESSIVE"
    elif winrate <= 40:
        return "DEFENSIVE"
    else:
        return "BALANCED"

# =========================
# PARAMETER ADAPTIVE
# =========================
def get_params(mode):
    if mode == "AGGRESSIVE":
        return {"rsi_buy": 52, "rsi_sell": 48, "ema_fast": 5, "ema_slow": 9}
    elif mode == "DEFENSIVE":
        return {"rsi_buy": 60, "rsi_sell": 40, "ema_fast": 8, "ema_slow": 15}
    else:
        return {"rsi_buy": 55, "rsi_sell": 45, "ema_fast": 6, "ema_slow": 12}

# =========================
# INDICATOR
# =========================
def compute_indicators(prices, ema_fast, ema_slow):
    df = pd.DataFrame(prices, columns=["price"])

    df["ema_fast"] = df["price"].ewm(span=ema_fast).mean()
    df["ema_slow"] = df["price"].ewm(span=ema_slow).mean()

    delta = df["price"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(7).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(7).mean()
    rs = gain / (loss + 1e-9)
    df["rsi"] = 100 - (100 / (1 + rs))

    return df

# =========================
# SIGNAL ENGINE
# =========================
def generate_signal(prices, trades_df):
    mode = get_performance_mode(trades_df)
    params = get_params(mode)

    if len(prices) < 20:
        return "HOLD", mode, 0

    df = compute_indicators(prices, params["ema_fast"], params["ema_slow"])
    last = df.iloc[-1]

    score = 0

    if last["ema_fast"] > last["ema_slow"]:
        score += 1
    else:
        score -= 1

    if last["rsi"] > params["rsi_buy"]:
        score += 1
    elif last["rsi"] < params["rsi_sell"]:
        score -= 1

    spread = abs(last["ema_fast"] - last["ema_slow"])
    if spread < last["price"] * 0.002:
        return "HOLD", mode, 0

    if score >= 2:
        return "BUY", mode, score
    elif score <= -2:
        return "SELL", mode, score
    else:
        return "HOLD", mode, score

# =========================
# SESSION STATE
# =========================
if "price_history" not in st.session_state:
    st.session_state.price_history = {c: [] for c in COINS}

# =========================
# MAIN LOOP
# =========================
placeholder = st.empty()

while True:
    with placeholder.container():

        st.title("🔥 AI Trading Dashboard PRO (STABLE)")

        # =========================
        # LOAD TRADES
        # =========================
        trades_df = pd.read_csv("trades.csv")

        if not trades_df.empty:
            trades_df["PnL"] = pd.to_numeric(trades_df["PnL"], errors="coerce")
            trades_df["Equity"] = trades_df["PnL"].cumsum() + INITIAL_CAPITAL

            total = len(trades_df)
            win = len(trades_df[trades_df["PnL"] > 0])
            winrate = (win / total) * 100 if total > 0 else 0
            equity = trades_df["Equity"].iloc[-1]
        else:
            total, winrate, equity = 0, 0, INITIAL_CAPITAL

        # =========================
        # METRICS
        # =========================
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Equity", f"{int(equity):,}")
        c2.metric("📊 Trades", total)
        c3.metric("🏆 Winrate", f"{winrate:.2f}%")

        st.divider()

        # =========================
        # LIVE MARKET
        # =========================
        st.subheader("🚀 Live Market + AI Signal")

        prices = get_prices()
        cols = st.columns(len(COINS))

        for i, coin in enumerate(COINS):

            data = prices.get(coin, {})
            price = data.get("usd", 0)

            if price == 0:
                with cols[i]:
                    st.metric(coin.upper(), "N/A")
                    st.warning("API error / limit")
                continue

            st.session_state.price_history[coin].append(price)
            hist = st.session_state.price_history[coin]

            signal, mode, score = generate_signal(hist, trades_df)

            color = "white"
            if signal == "BUY":
                color = "green"
            elif signal == "SELL":
                color = "red"

            with cols[i]:
                st.metric(coin.upper(), f"${price}")
                st.markdown(f"Mode: **{mode}**")
                st.markdown(f"Signal: :{color}[{signal}]")
                st.markdown(f"Score: {score}")
                st.line_chart(hist[-50:])

        st.divider()

        # =========================
        # EQUITY
        # =========================
        if not trades_df.empty:
            st.subheader("📈 Equity Curve")
            st.line_chart(trades_df["Equity"])

        st.divider()

        # =========================
        # TRADES
        # =========================
        st.subheader("🧾 Last Trades")

        if not trades_df.empty:
            def highlight(val):
                color = "green" if val > 0 else "red"
                return f"color: {color}"

            st.dataframe(
                trades_df.tail(10).style.applymap(highlight, subset=["PnL"])
            )

    time.sleep(REFRESH_RATE)
    st.rerun()
