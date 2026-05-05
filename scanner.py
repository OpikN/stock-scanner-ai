import pandas as pd
import numpy as np
import yfinance as yf
import time
import os
import requests
import threading

# =========================
# CONFIG
# =========================
STOCKS = ["BBCA.JK", "BBRI.JK", "TLKM.JK"]
INITIAL_CAPITAL = 10000000
RISK_PER_TRADE = 0.02

TRADE_FILE = "trades.csv"
LOG_FILE = "scanner_log.csv"

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
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": msg},
            timeout=5
        )
    except:
        print("❌ Telegram error")

# =========================
# SAFE DOWNLOAD (ANTI FREEZE)
# =========================
def safe_download(symbol, result):
    try:
        df = yf.download(symbol, period="1mo", interval="1d", progress=False, threads=False)
        result["data"] = df
    except:
        result["data"] = None

def download_with_timeout(symbol, timeout=10):
    result = {"data": None}
    thread = threading.Thread(target=safe_download, args=(symbol, result))
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        print(f"⛔ TIMEOUT {symbol}")
        return None

    return result["data"]

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

    score += 1 if last["ema_fast"] > last["ema_slow"] else -1

    if last["rsi"] > 55:
        score += 1
    elif last["rsi"] < 45:
        score -= 1

    if score >= 1:
        return "BUY", score
    elif score <= -1:
        return "SELL", score
    return "HOLD", score

# =========================
# LOT
# =========================
def calculate_position_size(equity, entry, sl):
    risk = equity * RISK_PER_TRADE
    diff = abs(entry - sl)
    return int(risk / diff) if diff != 0 else 0

# =========================
# SAVE
# =========================
def save_trade(trade):
    df = pd.read_csv(TRADE_FILE)
    df = pd.concat([df, pd.DataFrame([trade])], ignore_index=True)
    df.to_csv(TRADE_FILE, index=False)

def save_log(log):
    df = pd.read_csv(LOG_FILE)
    df = pd.concat([df, pd.DataFrame([log])], ignore_index=True)
    df.to_csv(LOG_FILE, index=False)

# =========================
# MAIN
# =========================
def run_scanner():
    print("\n🚀 SCANNING...")

    best_trade = None
    best_score = 0

    for s in STOCKS:
        print(f"⏳ {s}...")

        df = download_with_timeout(s)

        if df is None or df.empty:
            print(f"⚠️ SKIP {s}")
            continue

        df = compute_indicators(df)

        signal, score = generate_signal(df)
        price = df["Close"].iloc[-1]

        save_log({
            "Time": time.time(),
            "Stock": s,
            "Price": price,
            "Signal": signal,
            "Score": score
        })

        print(f"➡️ {s} | {signal} | Score {score}")

        if signal == "HOLD":
            continue

        sl = price * 0.98 if signal == "BUY" else price * 1.02
        tp = price * 1.04 if signal == "BUY" else price * 0.96

        lot = calculate_position_size(INITIAL_CAPITAL, price, sl)
        pnl = (tp - price) * lot if signal == "BUY" else (price - tp) * lot

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

    if best_trade:
        save_trade(best_trade)

        send_telegram(f"""
📊 SIGNAL
{best_trade['Stock']} {best_trade['Signal']}
Entry {best_trade['Entry']:.0f}
TP {best_trade['Exit']:.0f}
""")

        print("🔥 SIGNAL SENT")
    else:
        print("⚠️ No signal")

# =========================
# LOOP
# =========================
if __name__ == "__main__":
    while True:
        run_scanner()
        time.sleep(60)
