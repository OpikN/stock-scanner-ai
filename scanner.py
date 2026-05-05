import pandas as pd
import numpy as np
import yfinance as yf
import time
import os

# =========================
# CONFIG
# =========================
STOCKS = ["BBCA.JK", "BBRI.JK", "TLKM.JK"]
INITIAL_CAPITAL = 10000000
RISK_PER_TRADE = 0.02

# =========================
# AUTO CREATE FILE
# =========================
if not os.path.exists("trades.csv"):
    df_init = pd.DataFrame(columns=["Time","Stock","Signal","Entry","Exit","PnL"])
    df_init.to_csv("trades.csv", index=False)

# =========================
# LOAD TRADES
# =========================
def load_trades():
    return pd.read_csv("trades.csv")

# =========================
# SAVE TRADE
# =========================
def save_trade(trade):
    df = load_trades()
    df = pd.concat([df, pd.DataFrame([trade])], ignore_index=True)
    df.to_csv("trades.csv", index=False)

# =========================
# INDICATOR
# =========================
def compute_indicators(df):
    df["ema_fast"] = df["Close"].ewm(span=5).mean()
    df["ema_slow"] = df["Close"].ewm(span=10).mean()

    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(7).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(7).mean()
    rs = gain / (loss + 1e-9)
    df["rsi"] = 100 - (100 / (1 + rs))

    return df

# =========================
# SIGNAL LOGIC
# =========================
def generate_signal(df):
    last = df.iloc[-1]

    score = 0

    # TREND
    if last["ema_fast"] > last["ema_slow"]:
        score += 1
    else:
        score -= 1

    # MOMENTUM
    if last["rsi"] > 55:
        score += 1
    elif last["rsi"] < 45:
        score -= 1

    # FILTER SIDEWAYS
    spread = abs(last["ema_fast"] - last["ema_slow"])
    if spread < last["Close"] * 0.002:
        return "HOLD", score

    if score >= 2:
        return "BUY", score
    elif score <= -2:
        return "SELL", score
    else:
        return "HOLD", score

# =========================
# POSITION SIZE
# =========================
def calculate_position_size(equity, entry, sl):
    risk_amount = equity * RISK_PER_TRADE
    risk_per_share = abs(entry - sl)

    if risk_per_share == 0:
        return 0

    lot = risk_amount / risk_per_share
    return int(lot)

# =========================
# MAIN LOOP
# =========================
def run_scanner():
    trades_df = load_trades()

    equity = INITIAL_CAPITAL
    if not trades_df.empty:
        trades_df["PnL"] = pd.to_numeric(trades_df["PnL"], errors="coerce")
        equity = trades_df["PnL"].cumsum().iloc[-1] + INITIAL_CAPITAL

    print(f"\n📊 MARKET SCAN | Equity: {equity}\n")

    best_trade = None
    best_score = 0

    for s in STOCKS:
        try:
            df = yf.download(s, period="3mo", interval="1d")

            if df.empty or len(df) < 20:
                continue

            df = compute_indicators(df)

            signal, score = generate_signal(df)

            if signal == "HOLD":
                continue

            price = df["Close"].iloc[-1]

            # SL & TP (RR 1:2)
            if signal == "BUY":
                sl = price * 0.98
                tp = price * 1.04
            else:
                sl = price * 1.02
                tp = price * 0.96

            lot = calculate_position_size(equity, price, sl)

            pnl = (tp - price) * lot if signal == "BUY" else (price - tp) * lot

            print(f"[LOG] {s} | {signal} | Entry {price:.0f} | TP {tp:.0f} | SL {sl:.0f} | Lot {lot} | PnL {pnl:.0f}")

            if score > best_score:
                best_score = score
                best_trade = {
                    "Time": time.time(),
                    "Stock": s,
                    "Signal": signal,
                    "Entry": price,
                    "Exit": tp,
                    "PnL": pnl
                }

        except Exception as e:
            print(f"ERROR {s}: {e}")

    # =========================
    # SAVE BEST TRADE
    # =========================
    if best_trade:
        save_trade(best_trade)

        print("\n🔥 BEST TRADE SAVED 🔥")
        print(best_trade)

    else:
        print("⚠️ Tidak ada sinyal berkualitas hari ini")

# =========================
# RUN 24/7
# =========================
if __name__ == "__main__":
    while True:
        run_scanner()
        time.sleep(60)  # scan tiap 1 menit
