# ==============================
# IMPORT
# ==============================
import yfinance as yf
import pandas as pd
import requests, os, json, time
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
# STATE
# ==============================
def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return {"mode":"NORMAL","last_winrate":0}

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
# DOWNLOAD (ANTI ERROR)
# ==============================
def get_data(symbol):
    for i in range(3):
        try:
            df = yf.download(symbol, period="6mo", interval="1d", progress=False, threads=False)

            if df is None or df.empty:
                print("Retry kosong:", symbol)
                time.sleep(2)
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            print("OK:", symbol, "Rows:", len(df))
            return df

        except Exception as e:
            print("Retry error:", symbol, e)
            time.sleep(2)

    return None

# ==============================
# INDICATOR
# ==============================
def compute(df):
    close = df["Close"]
    df["ema20"] = ta.trend.ema_indicator(close, 20)
    df["ema50"] = ta.trend.ema_indicator(close, 50)
    df["rsi"]   = ta.momentum.rsi(close, 14)
    df["atr"]   = ta.volatility.average_true_range(df["High"], df["Low"], close, 14)
    df["adx"]   = ta.trend.adx(df["High"], df["Low"], close, 14)
    return df

# ==============================
# SIGNAL + CONFIDENCE
# ==============================
def signal(df, mode):
    r = df.iloc[-1]

    price = float(r["Close"])
    ema20, ema50 = r["ema20"], r["ema50"]
    rsi, atr, adx = r["rsi"], r["atr"], r["adx"]

    # MODE
    if mode == "SAFE":
        rsi_low, rsi_high = 45, 55
        atr_mult = 2.0
    elif mode == "AGGRESSIVE":
        rsi_low, rsi_high = 30, 70
        atr_mult = 1.2
    else:
        rsi_low, rsi_high = 35, 60
        atr_mult = 1.5

    # SIGNAL
    if ema20 > ema50 and rsi_low < rsi < rsi_high:
        sig = "BUY"
        sl = price - atr_mult * atr
        tp = price + 2 * atr

    elif ema20 < ema50 and rsi_low < rsi < rsi_high:
        sig = "SELL"
        sl = price + atr_mult * atr
        tp = price - 2 * atr

    else:
        return "HOLD", price, 0, 0, 0, "LOW"

    # RR
    rr = abs((tp - price) / (price - sl)) if sig == "BUY" else abs((price - tp) / (sl - price))

    # CONFIDENCE
    confidence = "LOW"

    if adx > 25 and rr >= 1.5:
        confidence = "HIGH"
    elif adx > 20:
        confidence = "MEDIUM"

    return sig, price, sl, tp, adx, confidence

# ==============================
# BACKTEST REAL
# ==============================
def backtest(df, mode):
    capital = CAPITAL_INIT
    trades = []

    for i in range(60, len(df)):
        sub = df.iloc[:i]
        sig, entry, sl, tp, _, _ = signal(sub, mode)

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
        df = get_data(s)

        if df is None or len(df) < 50:
            print("Skip:", s)
            continue

        try:
            df = compute(df)

            sig, entry, sl, tp, adx, confidence = signal(df, mode)
            winrate, trades, final_cap = backtest(df, mode)

            score = winrate * 0.6 + trades * 2

            rows.append({
                "Stock": s,
                "Signal": sig,
                "Entry": round(entry,2),
                "SL": round(sl,2),
                "TP": round(tp,2),
                "ADX": round(adx,2),
                "Confidence": confidence,
                "Winrate": winrate,
                "Trades": trades,
                "Score": round(score,2)
            })

        except Exception as e:
            print("ERR:", s, e)

    if not rows:
        send("⚠️ Data kosong (API error / market libur)")
        return

    df = pd.DataFrame(rows)

    # UPDATE MODE
    avg_winrate = df["Winrate"].mean()

    if avg_winrate < 40:
        state["mode"] = "SAFE"
    elif avg_winrate > 65:
        state["mode"] = "AGGRESSIVE"
    else:
        state["mode"] = "NORMAL"

    save_state(state)

    # FILTER
    df = df[df["Signal"] != "HOLD"]
    df = df[df["Confidence"] != "LOW"]

    if df.empty:
        df = pd.DataFrame(rows).sort_values("Score", ascending=False)
        mode_label = "ALTERNATIF"
    else:
        df = df.sort_values("Score", ascending=False)
        mode_label = "REAL SIGNAL"

    top = df.head(3)

    # TELEGRAM
    msg = f"🤖 MODE: {state['mode']} | {mode_label}\n\n🔥 TOP SIGNAL 🔥\n\n"

    for _, r in top.iterrows():
        msg += (
            f"{r['Stock']} ({r['Signal']})\n"
            f"Entry: {r['Entry']} | SL: {r['SL']} | TP: {r['TP']}\n"
            f"ADX: {r['ADX']} | Confidence: {r['Confidence']}\n"
            f"Winrate: {r['Winrate']}% | Trades: {r['Trades']}\n"
            f"Score: {r['Score']}\n\n"
        )

    send(msg)

# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    run()
