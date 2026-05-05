import pandas as pd
import numpy as np
import yfinance as yf
import time
import os
import requests

# =========================
# CONFIG
# =========================
STOCKS = ["BBCA.JK", "BBRI.JK", "TLKM.JK"]
INITIAL_CAPITAL = 10000000
RISK_PER_TRADE = 0.02

TRADE_FILE = "trades.csv"
LOG_FILE = "scanner_log.csv"

# 🔥 TELEGRAM
TELEGRAM_TOKEN = "ISI_TOKEN_KAMU"
TELEGRAM_CHAT_ID = "ISI_CHAT_ID_KAMU"

# =========================
# INIT FILE
# =========================
if not os.path.exists(TRADE_FILE):
    pd.DataFrame(columns=["Time","Stock","Signal","Entry","Exit","PnL"]).to_csv(TRADE_FILE, index=False)

if not os.path.exists(LOG_FILE):
    pd.DataFrame(columns=["Time","Stock","Price","Signal","Score"]).to_csv(LOG_FILE, index=False)

# =========================
# TELEGRAM
# =========================
def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg
        }, timeout=5)
    except Exception as e:
        print("❌ Telegram error:", e)

# =========================
# SAVE / LOAD
# =========================
def load_trades():
    return pd.read_csv(TRADE_FILE)

def save_trade(trade):
    df = load_trades()
    df = pd.concat([df, pd.DataFrame([trade])], ignore_index=True)
    df.to_csv(TRADE_FILE, index=False)

def save_log(data):
    df = pd.read_csv(LOG_FILE)
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(LOG_FILE, index=False)

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
# SIGNAL
# =========================
def generate_signal(df):
    last = df.iloc[-1]
    score = 0

    if last["ema_fast"] > last["ema_slow"]:
        score += 1
    else:
        score -= 1

    if last["rsi"] > 55:
        score += 1
    elif last["rsi"] < 45:
        score -= 1

    spread = abs(last["ema_fast"] - last["ema_slow"])
    if spread < last["Close"] * 0.002:
        return "HOLD", score

    if score >= 1:
        return "BUY", score
    elif score <= -1:
        return "SELL", score
    else:
        return "HOLD", score

# =========================
# LOT SIZE
# =========================
def calculate_position_size(equity, entry, sl):
    risk_amount = equity * RISK_PER_TRADE
    risk_per_share = abs(entry - sl)

    if risk_per_share == 0:
        return 0

    return int(risk_amount / risk_per_share)

# =========================
# SCANNER
# =========================
def run_scanner():
    print("\n🚀 Scanner running...")

    trades_df = load_trades()

    equity = INITIAL_CAPITAL
    if not trades_df.empty:
        trades_df["PnL"] = pd.to_numeric(trades_df["PnL"], errors="coerce")
        equity = trades_df["PnL"].cumsum().iloc[-1] + INITIAL_CAPITAL

    print(f"💰 Equity: {equity}")

    best_trade = None
    best_score = 0

    for s in STOCKS:
        try:
            print(f"\n⏳ Downloading {s}...")

            df = yf.download(
                s,
                period="1mo",         # 🔥 lebih cepat
                interval="1d",
                progress=False,
                threads=False
            )

            if df is None or df.empty:
                print(f"⚠️ {s} gagal load")
                continue

            print(f"✅ {s} loaded ({len(df)} rows)")

            df = compute_indicators(df)

            signal, score = generate_signal(df)
            price = df["Close"].iloc[-1]

            # 🔥 LOG ke dashboard
            save_log({
                "Time": time.time(),
                "Stock": s,
                "Price": price,
                "Signal": signal,
                "Score": score
            })

            if signal == "HOLD":
                print(f"➡️ {s} HOLD (score {score})")
                continue

            # SL / TP
            if signal == "BUY":
                sl = price * 0.98
                tp = price * 1.04
            else:
                sl = price * 1.02
                tp = price * 0.96

            lot = calculate_position_size(equity, price, sl)
            pnl = (tp - price) * lot if signal == "BUY" else (price - tp) * lot

            print(f"🔥 {s} {signal} | Entry {price:.0f} | TP {tp:.0f} | SL {sl:.0f} | Lot {lot} | PnL {pnl:.0f}")

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
            print(f"❌ ERROR {s}: {e}")

    # =========================
    # SAVE + TELEGRAM
    # =========================
    if best_trade:
        save_trade(best_trade)

        msg = f"""
📊 AI SIGNAL

Stock: {best_trade['Stock']}
Signal: {best_trade['Signal']}
Entry: {best_trade['Entry']:.0f}
TP: {best_trade['Exit']:.0f}
PnL Est: {best_trade['PnL']:.0f}
"""

        send_telegram(msg)

        print("📤 Signal dikirim ke Telegram")

    else:
        print("⚠️ Tidak ada signal kuat")

# =========================
# LOOP
# =========================
if __name__ == "__main__":
    while True:
        run_scanner()
        time.sleep(60)
