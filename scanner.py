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
MAX_LOT = 100

# 🔥 AUTO MODE (override manual kalau ada)
MANUAL_MODE = os.getenv("TRADING_MODE")  # optional: SAFE / AGGRESSIVE

MAX_LOSS_STREAK = 2
MAX_DAILY_LOSS = -0.03

TRADE_FILE = "trades.csv"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# =========================
# SAFE FLOAT
# =========================
def safe_float(x):
    try:
        if hasattr(x, "values"):
            x = x.values
        if isinstance(x, (list, tuple, np.ndarray)):
            return float(x[0])
        return float(x)
    except:
        return 0.0

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

    df["tr"] = np.maximum.reduce([
        df["High"] - df["Low"],
        abs(df["High"] - df["Close"].shift()),
        abs(df["Low"] - df["Close"].shift())
    ])
    df["atr"] = df["tr"].rolling(7).mean()

    return df

# =========================
# 🔥 MARKET MODE DETECTOR
# =========================
def detect_mode(df):
    last = df.iloc[-1:]

    ema_fast = safe_float(last["ema_fast"])
    ema_slow = safe_float(last["ema_slow"])
    price = safe_float(last["Close"])
    rsi = safe_float(last["rsi"])

    volume_now = safe_float(df["Volume"].iloc[-1:])
    volume_avg = safe_float(df["Volume"].rolling(10).mean().iloc[-1:])

    strength = abs(ema_fast - ema_slow) / price

    score = 0

    if strength > 0.004:
        score += 1
    if rsi > 60 or rsi < 40:
        score += 1
    if volume_now > volume_avg:
        score += 1

    # 🔥 keputusan
    if score >= 2:
        return "AGGRESSIVE"
    return "SAFE"

# =========================
# SIGNAL ENGINE
# =========================
def generate_signal(df, MODE):
    last = df.iloc[-1:]

    ema_fast = safe_float(last["ema_fast"])
    ema_slow = safe_float(last["ema_slow"])
    ema_trend = safe_float(last["ema_trend"])
    rsi = safe_float(last["rsi"])
    price = safe_float(last["Close"])

    score = 0
    trend = "BULL" if price > ema_trend else "BEAR"

    score += 1 if ema_fast > ema_slow else -1

    if rsi > 55:
        score += 1
    elif rsi < 45:
        score -= 1

    strength = abs(ema_fast - ema_slow) / price

    if MODE == "AGGRESSIVE":
        if strength < 0.002:
            return "HOLD", score, trend
        MIN_SCORE = 1
    else:
        if strength < 0.003:
            return "HOLD", score, trend
        MIN_SCORE = 2

        # SAFE FILTER
        volume_now = safe_float(df["Volume"].iloc[-1:])
        volume_avg = safe_float(df["Volume"].rolling(10).mean().iloc[-1:])
        if volume_now < volume_avg:
            return "HOLD", score, trend

    if score >= MIN_SCORE and trend == "BULL":
        return "BUY", score, trend
    elif score <= -MIN_SCORE and trend == "BEAR":
        return "SELL", score, trend

    return "HOLD", score, trend

# =========================
# LOT
# =========================
def calculate_lot(equity, entry, sl, MODE):
    risk_pct = 0.03 if MODE == "AGGRESSIVE" else 0.02
    risk = equity * risk_pct
    diff = abs(entry - sl)
    lot = int(risk / diff) if diff != 0 else 0
    return min(lot, MAX_LOT)

# =========================
# RISK CONTROL
# =========================
def check_risk(trades):
    if trades.empty:
        return True

    last = trades.tail(MAX_LOSS_STREAK)
    if len(last) == MAX_LOSS_STREAK and all(last["PnL"] < 0):
        return False

    if trades.tail(10)["PnL"].sum() < INITIAL_CAPITAL * MAX_DAILY_LOSS:
        return False

    return True

# =========================
# MAIN
# =========================
def run():
    print("🚀 SCANNER START (AUTO MODE)")

    trades = load_trades()

    if not check_risk(trades):
        send_telegram("⛔ Trading dihentikan (risk control aktif)")
        return

    equity = INITIAL_CAPITAL + trades["PnL"].sum() if not trades.empty else INITIAL_CAPITAL

    best = None
    best_score = 0
    final_mode = "SAFE"

    for s in STOCKS:
        try:
            df = yf.download(s, period="1mo", interval="1d", progress=False)
            if df is None or df.empty:
                continue

            df = compute_indicators(df)

            # 🔥 AUTO MODE DETECT
            MODE = MANUAL_MODE if MANUAL_MODE else detect_mode(df)
            final_mode = MODE

            signal, score, trend = generate_signal(df, MODE)

            price = safe_float(df["Close"].iloc[-1:])
            atr = safe_float(df["atr"].iloc[-1:])

            if signal == "HOLD":
                continue

            # ENTRY
            if signal == "BUY":
                entry = price - (0.2 * atr if MODE == "AGGRESSIVE" else 0.3 * atr)
                sl = entry - (1 * atr)
                tp = entry + ((1.2 if MODE == "AGGRESSIVE" else 1.5) * atr)
            else:
                entry = price + (0.2 * atr if MODE == "AGGRESSIVE" else 0.3 * atr)
                sl = entry + (1 * atr)
                tp = entry - ((1.2 if MODE == "AGGRESSIVE" else 1.5) * atr)

            lot = calculate_lot(equity, entry, sl, MODE)

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
                    "Mode": MODE
                }

        except Exception as e:
            print("ERROR:", e)

    if best:
        save_trade(best)

        msg = f"""
📊 AI AUTO MODE SIGNAL

⚙️ Mode: {best['Mode']}

📍 {best['Stock']} | {best['Signal']}

💰 Entry: {best['Entry']:.0f}
🎯 TP: {best['TP']:.0f}
🛑 SL: {best['SL']:.0f}

📦 Lot: {best['Lot']}
💵 Est.PnL: {best['PnL']:.0f}
"""
        send_telegram(msg)

    else:
        print(f"⚠️ No signal | Mode: {final_mode}")

# =========================
if __name__ == "__main__":
    run()
