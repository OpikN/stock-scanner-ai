import pandas as pd
import yfinance as yf
import time
import os
import requests
import numpy as np

# =========================
# CONFIG
# =========================
STOCKS = ["BBCA.JK", "BBRI.JK", "TLKM.JK"]

INITIAL_CAPITAL = 10000000
RISK_PER_TRADE = 0.02
MAX_LOT = 100

# 🔥 ANTI LOSS SYSTEM
MAX_LOSS_STREAK = 2
MAX_DAILY_LOSS = -0.03   # -3%
COOLDOWN_TRADES = 2

TRADE_FILE = "trades.csv"
LOG_FILE = "scanner_log.csv"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# =========================
# TELEGRAM
# =========================
def send_telegram(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ TELEGRAM ENV NOT SET")
        return

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
    except:
        pass

# =========================
# FILE INIT
# =========================
if not os.path.exists(TRADE_FILE):
    pd.DataFrame(columns=["Time","Stock","Signal","Entry","TP","SL","Lot","PnL"]).to_csv(TRADE_FILE, index=False)

def load_trades():
    return pd.read_csv(TRADE_FILE)

def save_trade(trade):
    df = load_trades()
    df = pd.concat([df, pd.DataFrame([trade])], ignore_index=True)
    df.to_csv(TRADE_FILE, index=False)

# =========================
# INDICATORS
# =========================
def compute_indicators(df):
    df["ema_fast"] = df["Close"].ewm(span=5).mean()
    df["ema_slow"] = df["Close"].ewm(span=10).mean()
    df["ema_trend"] = df["Close"].ewm(span=50).mean()

    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(7).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(7).mean()
    rs = gain / (loss + 1e-9)
    df["rsi"] = 100 - (100 / (1 + rs))

    # 🔥 ATR (volatility)
    df["tr"] = np.maximum.reduce([
        df["High"] - df["Low"],
        abs(df["High"] - df["Close"].shift()),
        abs(df["Low"] - df["Close"].shift())
    ])
    df["atr"] = df["tr"].rolling(7).mean()

    return df

# =========================
# SIGNAL ENGINE
# =========================
def generate_signal(df):
    last = df.iloc[-1]

    ema_fast = float(last["ema_fast"])
    ema_slow = float(last["ema_slow"])
    ema_trend = float(last["ema_trend"])
    rsi = float(last["rsi"])
    price = float(last["Close"])

    score = 0

    trend = "BULL" if price > ema_trend else "BEAR"

    score += 1 if ema_fast > ema_slow else -1

    if rsi > 55:
        score += 1
    elif rsi < 45:
        score -= 1

    # 🔥 TREND STRENGTH FILTER
    strength = abs(ema_fast - ema_slow) / price
    if strength < 0.003:
        return "HOLD", score, trend

    if score >= 2 and trend == "BULL":
        return "BUY", score, trend
    elif score <= -2 and trend == "BEAR":
        return "SELL", score, trend

    return "HOLD", score, trend

# =========================
# POSITION SIZE
# =========================
def calculate_lot(equity, entry, sl):
    risk = equity * RISK_PER_TRADE
    diff = abs(entry - sl)
    lot = int(risk / diff) if diff != 0 else 0
    return min(lot, MAX_LOT)

# =========================
# ANTI LOSS SYSTEM
# =========================
def check_risk_control(trades):
    if trades.empty:
        return True

    # LOSS STREAK
    last_trades = trades.tail(MAX_LOSS_STREAK)
    if len(last_trades) == MAX_LOSS_STREAK and all(last_trades["PnL"] < 0):
        print("⛔ STOP: Loss streak")
        return False

    # DAILY LOSS
    today = trades.tail(10)
    if today["PnL"].sum() < INITIAL_CAPITAL * MAX_DAILY_LOSS:
        print("⛔ STOP: Daily loss limit")
        return False

    return True

# =========================
# MAIN
# =========================
def run():
    print("🚀 SCANNER START")

    trades = load_trades()

    if not check_risk_control(trades):
        send_telegram("⛔ Trading dihentikan sementara (risk control aktif)")
        return

    equity = INITIAL_CAPITAL
    if not trades.empty:
        equity += trades["PnL"].sum()

    best = None
    best_score = 0

    for s in STOCKS:
        try:
            df = yf.download(s, period="1mo", interval="1d", progress=False)
            if df is None or df.empty:
                continue

            df = compute_indicators(df)

            signal, score, trend = generate_signal(df)
            price = float(df["Close"].iloc[-1])
            atr = float(df["atr"].iloc[-1])

            if signal == "HOLD":
                continue

            # 🔥 SMART ENTRY (RETRACE)
            if signal == "BUY":
                entry = price - (0.3 * atr)
                sl = entry - (1 * atr)
                tp = entry + (2 * atr)
            else:
                entry = price + (0.3 * atr)
                sl = entry + (1 * atr)
                tp = entry - (2 * atr)

            lot = calculate_lot(equity, entry, sl)
            pnl = (tp - entry) * lot if signal == "BUY" else (entry - tp) * lot

            if best is None or abs(score) > abs(best_score):
                best_score = score
                best = {
                    "Time": time.time(),
                    "Stock": s,
                    "Signal": signal,
                    "Entry": entry,
                    "TP": tp,
                    "SL": sl,
                    "Lot": lot,
                    "PnL": pnl,
                    "Score": score,
                    "Trend": trend
                }

        except Exception as e:
            print("ERROR:", e)

    if best:
        save_trade(best)

        msg = f"""
📊 AI SMART SIGNAL

📍 {best['Stock']} | {best['Signal']} | {best['Trend']}

💰 Entry: {best['Entry']:.0f}
🎯 TP: {best['TP']:.0f}
🛑 SL: {best['SL']:.0f}

📊 Confidence: {abs(best['Score'])}/2
📦 Lot: {best['Lot']}

💵 Est.PnL: {best['PnL']:.0f}
"""
        send_telegram(msg)

    else:
        print("⚠️ No signal")

# =========================
if __name__ == "__main__":
    run()
