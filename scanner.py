# ==============================
# IMPORT
# ==============================
import yfinance as yf
import pandas as pd
import requests, os, json
import ta

# ==============================
# CONFIG
# ==============================
STOCKS = ["BBCA.JK","BBRI.JK","TLKM.JK","BMRI.JK","ASII.JK"]

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID   = os.getenv("CHAT_ID")

CAPITAL_INIT = 10_000_000
STATE_FILE = "state.json"

# ==============================
# STATE (AI MEMORY)
# ==============================
def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return {
            "mode":"NORMAL",
            "last_winrate":0,
            "last_capital":CAPITAL_INIT
        }

def save_state(state):
    with open(STATE_FILE,"w") as f:
        json.dump(state,f)

# ==============================
# TELEGRAM
# ==============================
def send(msg):
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Secret tidak terbaca")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# ==============================
# INDICATOR
# ==============================
def compute(df):
    close = df["Close"]
    df["ema20"] = ta.trend.ema_indicator(close, 20)
    df["ema50"] = ta.trend.ema_indicator(close, 50)
    df["rsi"]   = ta.momentum.rsi(close, 14)
    df["atr"]   = ta.volatility.average_true_range(df["High"], df["Low"], close, 14)
    return df

# ==============================
# ADAPTIVE SIGNAL
# ==============================
def signal(df, mode):
    r = df.iloc[-1]
    price = float(r["Close"])
    ema20, ema50, rsi, atr = r["ema20"], r["ema50"], r["rsi"], r["atr"]

    if mode == "SAFE":
        rsi_low, rsi_high = 45, 55
        atr_mult = 2.0
    elif mode == "AGGRESSIVE":
        rsi_low, rsi_high = 30, 70
        atr_mult = 1.2
    else:
        rsi_low, rsi_high = 35, 60
        atr_mult = 1.5

    if ema20 > ema50 and rsi_low < rsi < rsi_high:
        return "BUY", price, price - atr_mult*atr, price + 2*atr

    elif ema20 < ema50 and rsi_low < rsi < rsi_high:
        return "SELL", price, price + atr_mult*atr, price - 2*atr

    return "HOLD", price, 0, 0

# ==============================
# BACKTEST REAL
# ==============================
def backtest(df, mode):
    capital = CAPITAL_INIT
    trades = []

    for i in range(60, len(df)):
        sub = df.iloc[:i]
        sig, entry, sl, tp = signal(sub, mode)

        if sig == "HOLD":
            continue

        for j in range(i, len(df)):
            high = df["High"].iloc[j]
            low  = df["Low"].iloc[j]

            if sig == "BUY":
                if low <= sl:
                    pnl = (sl - entry) / entry
                    trades.append(pnl)
                    capital *= (1 + pnl)
                    break
                elif high >= tp:
                    pnl = (tp - entry) / entry
                    trades.append(pnl)
                    capital *= (1 + pnl)
                    break

            if sig == "SELL":
                if high >= sl:
                    pnl = (entry - sl) / entry
                    trades.append(pnl)
                    capital *= (1 + pnl)
                    break
                elif low <= tp:
                    pnl = (entry - tp) / entry
                    trades.append(pnl)
                    capital *= (1 + pnl)
                    break

    if not trades:
        return 0, 0, capital

    win = len([t for t in trades if t > 0])
    winrate = (win / len(trades)) * 100

    return round(winrate,2), len(trades), int(capital)

# ==============================
# MAIN
# ==============================
def run():
    state = load_state()
    mode = state["mode"]

    rows = []

    for s in STOCKS:
        try:
            df = yf.download(s, period="6mo", progress=False)

            if df is None or len(df) < 80:
                continue

            df = compute(df)

            sig, entry, sl, tp = signal(df, mode)

            winrate, trades, final_cap = backtest(df, mode)

            score = winrate * 0.6 + trades * 2

            rows.append({
                "Stock": s,
                "Signal": sig,
                "Entry": round(entry,2),
                "SL": round(sl,2),
                "TP": round(tp,2),
                "Winrate": winrate,
                "Trades": trades,
                "FinalCap": final_cap,
                "Score": round(score,2)
            })

        except Exception as e:
            print("ERR", s, e)

    if not rows:
        send("⚠️ Data kosong")
        return

    df = pd.DataFrame(rows)

    # ADAPTIVE UPDATE MODE
    avg_winrate = df["Winrate"].mean()

    if avg_winrate < 40:
        state["mode"] = "SAFE"
    elif avg_winrate > 65:
        state["mode"] = "AGGRESSIVE"
    else:
        state["mode"] = "NORMAL"

    state["last_winrate"] = avg_winrate
    save_state(state)

    # FILTER
    df = df[df["Signal"] != "HOLD"]

    if df.empty:
        df = pd.DataFrame(rows)

    df = df.sort_values("Score", ascending=False)

    top = df.head(3)

    # SAVE
    top.to_csv("data.csv", index=False)

    # TELEGRAM
    msg = f"🤖 MODE: {state['mode']}\n\n🔥 TOP SIGNAL 🔥\n\n"

    for i, r in top.iterrows():
        msg += (
            f"{r['Stock']} ({r['Signal']})\n"
            f"Entry: {r['Entry']} | SL: {r['SL']} | TP: {r['TP']}\n"
            f"Winrate: {r['Winrate']}% | Trades: {r['Trades']}\n"
            f"Score: {r['Score']}\n\n"
        )

    send(msg)

# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    run()
