import pandas as pd
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

# ENV TELEGRAM
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

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
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ TELEGRAM ENV NOT SET")
        return

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        res = requests.post(url, data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg
        })

        print("📨 STATUS:", res.status_code)
        print("📨 RESPONSE:", res.text)

    except Exception as e:
        print("❌ Telegram error:", e)

# =========================
# SAVE
# =========================
def load_trades():
    return pd.read_csv(TRADE_FILE)

def save_trade(trade):
    df = load_trades()
    new_row = pd.DataFrame([trade])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(TRADE_FILE, index=False)

def save_log(data):
    df = pd.read_csv(LOG_FILE)
    new_row = pd.DataFrame([data])
    df = pd.concat([df, new_row], ignore_index=True)
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
# SIGNAL (NO WARNING VERSION)
# =========================
def generate_signal(df):
    last = df.iloc[-1]

    ema_fast = float(last["ema_fast"])
    ema_slow = float(last["ema_slow"])
    rsi = float(last["rsi"])

    score = 0

    if ema_fast > ema_slow:
        score += 1
    else:
        score -= 1

    if rsi > 55:
        score += 1
    elif rsi < 45:
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
# MAIN
# =========================
def run_scanner():
    print("🚀 SCANNER START")

    print("TOKEN:", TELEGRAM_TOKEN)
    print("CHAT_ID:", TELEGRAM_CHAT_ID)

    send_telegram("TEST 🔥 Scanner aktif")

    trades_df = load_trades()

    equity = INITIAL_CAPITAL
    if not trades_df.empty:
        trades_df["PnL"] = pd.to_numeric(trades_df["PnL"], errors="coerce")
        equity = trades_df["PnL"].cumsum().iloc[-1] + INITIAL_CAPITAL

    best_trade = None
    best_score = 0

    for s in STOCKS:
        try:
            print(f"⏳ {s}")

            df = yf.download(s, period="1mo", interval="1d", progress=False)

            if df is None or df.empty:
                print(f"⚠️ skip {s}")
                continue

            df = compute_indicators(df)

            signal, score = generate_signal(df)
            price = float(df["Close"].iloc[-1])

            save_log({
                "Time": time.time(),
                "Stock": s,
                "Price": price,
                "Signal": signal,
                "Score": score
            })

            print(f"{s} → {signal} ({score})")

            if signal == "HOLD":
                continue

            sl = price * 0.98 if signal == "BUY" else price * 1.02
            tp = price * 1.04 if signal == "BUY" else price * 0.96

            lot = calculate_position_size(equity, price, sl)
            pnl = (tp - price) * lot if signal == "BUY" else (price - tp) * lot

            # 🔥 FIX AGAR SELL MASUK
            if best_trade is None or abs(score) > abs(best_score):
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

    if best_trade:
        save_trade(best_trade)

        send_telegram(f"""
📊 AI SIGNAL
{best_trade['Stock']} {best_trade['Signal']}
Entry {best_trade['Entry']:.0f}
TP {best_trade['Exit']:.0f}
""")

        print("🔥 SIGNAL SENT")
    else:
        print("⚠️ No signal")

# =========================
# RUN
# =========================
if __name__ == "__main__":
    run_scanner()
