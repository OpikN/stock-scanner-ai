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

MAX_POSITIONS = 3
MAX_DRAWDOWN = 0.15
RISK_PER_TRADE = 0.02

# ==============================
# STATE
# ==============================
def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return {"mode":"NORMAL"}

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
# DOWNLOAD
# ==============================
def get_data(symbol):
    for i in range(3):
        try:
            df = yf.download(symbol, period="6mo", interval="1d", progress=False, threads=False)

            if df is None or df.empty:
                time.sleep(2)
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            return df

        except:
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
# SIGNAL
# ==============================
def signal(df, mode):
    r = df.iloc[-1]

    price = float(r["Close"])
    ema20, ema50 = r["ema20"], r["ema50"]
    rsi, atr, adx = r["rsi"], r["atr"], r["adx"]

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
        sig = "BUY"
        sl = price - atr_mult * atr
        tp = price + 2 * atr

    elif ema20 < ema50 and rsi_low < rsi < rsi_high:
        sig = "SELL"
        sl = price + atr_mult * atr
        tp = price - 2 * atr

    else:
        return "HOLD", price, 0, 0, 0, "LOW"

    rr = abs((tp - price) / (price - sl)) if sig == "BUY" else abs((price - tp) / (sl - price))

    confidence = "LOW"
    if adx > 25 and rr >= 1.5:
        confidence = "HIGH"
    elif adx > 20:
        confidence = "MEDIUM"

    return sig, price, sl, tp, adx, confidence

# ==============================
# POSITION SIZE (IDX FIX)
# ==============================
def calc_lot(equity, entry, sl):
    risk_value = equity * RISK_PER_TRADE
    risk_per_share = abs(entry - sl)

    if risk_per_share == 0:
        return 0

    shares = risk_value / risk_per_share
    lot = int(shares / 100)

    max_lot = int(equity / (entry * 100))
    lot = min(lot, max_lot)

    return max(lot, 0)

# ==============================
# BACKTEST PORTFOLIO
# ==============================
def backtest_portfolio(df, mode):
    equity = CAPITAL_INIT
    peak = equity

    active = []
    trades = []

    for i in range(60, len(df)):

        # drawdown control
        drawdown = (equity - peak) / peak
        if drawdown <= -MAX_DRAWDOWN:
            break

        peak = max(peak, equity)

        sub = df.iloc[:i]
        sig, entry, sl, tp, _, _ = signal(sub, mode)

        # entry
        if sig != "HOLD" and len(active) < MAX_POSITIONS:
            lot = calc_lot(equity, entry, sl)
            if lot > 0:
                active.append({
                    "type": sig,
                    "entry": entry,
                    "sl": sl,
                    "tp": tp,
                    "lot": lot
                })

        # manage
        new_active = []

        for pos in active:
            high = df["High"].iloc[i]
            low  = df["Low"].iloc[i]

            exit_price = None

            if pos["type"] == "BUY":
                if low <= pos["sl"]:
                    exit_price = pos["sl"]
                elif high >= pos["tp"]:
                    exit_price = pos["tp"]

                if exit_price:
                    pnl = (exit_price - pos["entry"]) * pos["lot"]
                    equity += pnl
                    trades.append(pnl)
                else:
                    new_active.append(pos)

            elif pos["type"] == "SELL":
                if high >= pos["sl"]:
                    exit_price = pos["sl"]
                elif low <= pos["tp"]:
                    exit_price = pos["tp"]

                if exit_price:
                    pnl = (pos["entry"] - exit_price) * pos["lot"]
                    equity += pnl
                    trades.append(pnl)
                else:
                    new_active.append(pos)

        active = new_active

    if not trades:
        return 0, 0, int(equity)

    win = len([t for t in trades if t > 0])
    winrate = (win / len(trades)) * 100

    return round(winrate,2), len(trades), int(equity)

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
            continue

        df = compute(df)

        sig, entry, sl, tp, adx, conf = signal(df, mode)
        winrate, trades, final_cap = backtest_portfolio(df, mode)

        lot = calc_lot(CAPITAL_INIT, entry, sl)

        score = winrate * 0.6 + trades * 2

        rows.append({
            "Stock": s,
            "Signal": sig,
            "Entry": round(entry,2),
            "SL": round(sl,2),
            "TP": round(tp,2),
            "Lot": lot,
            "ADX": round(adx,2),
            "Confidence": conf,
            "Winrate": winrate,
            "Trades": trades,
            "Score": round(score,2)
        })

    if not rows:
        send("⚠️ Data kosong")
        return

    df = pd.DataFrame(rows)

    # adaptive mode
    avg = df["Winrate"].mean()
    if avg < 40:
        state["mode"] = "SAFE"
    elif avg > 65:
        state["mode"] = "AGGRESSIVE"
    else:
        state["mode"] = "NORMAL"

    save_state(state)

    # filter
    df = df[df["Signal"] != "HOLD"]
    df = df[df["Confidence"] != "LOW"]
    df = df[df["Winrate"] >= 50]

    if df.empty:
        df = pd.DataFrame(rows).sort_values("Score", ascending=False)
        label = "ALTERNATIF"
    else:
        df = df.sort_values("Score", ascending=False)
        label = "REAL SIGNAL"

    top = df.head(3)

    # telegram
    msg = f"🤖 MODE: {state['mode']} | {label}\n"
    msg += f"📊 Max Posisi: {MAX_POSITIONS}\n\n🔥 TOP SIGNAL 🔥\n\n"

    for _, r in top.iterrows():
        capital_used = int(r["Lot"] * r["Entry"] * 100)

        msg += (
            f"{r['Stock']} ({r['Signal']})\n"
            f"Entry: {r['Entry']} | SL: {r['SL']} | TP: {r['TP']}\n"
            f"Lot: {r['Lot']} | Capital: {capital_used}\n"
            f"ADX: {r['ADX']} | Conf: {r['Confidence']}\n"
            f"Winrate: {r['Winrate']}% | Trades: {r['Trades']}\n"
            f"Score: {r['Score']}\n\n"
        )

    send(msg)

# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    run()
