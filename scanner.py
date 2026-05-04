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
IHSG = "^JKSE"

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
    for _ in range(3):
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
# MARKET REGIME
# ==============================
def get_market_regime(df):
    r = df.iloc[-1]
    ema20 = r["ema20"]
    ema50 = r["ema50"]
    adx   = r["adx"]

    if ema20 > ema50 and adx > 25:
        return "BULL"
    elif ema20 < ema50 and adx > 25:
        return "BEAR"
    return "SIDEWAYS"

# ==============================
# VOLATILITY
# ==============================
def get_volatility_regime(df):
    atr = df["atr"]
    current = atr.iloc[-1]
    avg = atr.rolling(20).mean().iloc[-1]

    if current > avg * 1.3:
        return "HIGH"
    elif current < avg * 0.7:
        return "LOW"
    return "NORMAL"

# ==============================
# DYNAMIC RISK
# ==============================
def get_dynamic_risk(base_risk, winrate, vol):
    risk = base_risk

    if winrate > 70:
        risk *= 1.3
    elif winrate < 40:
        risk *= 0.7

    if vol == "HIGH":
        risk *= 0.5
    elif vol == "LOW":
        risk *= 0.8

    return min(max(risk, 0.005), 0.03)

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

    conf = "LOW"
    if adx > 25 and rr >= 1.5:
        conf = "HIGH"
    elif adx > 20:
        conf = "MEDIUM"

    return sig, price, sl, tp, adx, conf

# ==============================
# POSITION SIZE
# ==============================
def calc_lot(equity, entry, sl, risk_pct):
    risk_value = equity * risk_pct
    risk_per_share = abs(entry - sl)

    if risk_per_share == 0:
        return 0

    shares = risk_value / risk_per_share
    lot = int(shares / 100)

    max_lot = int(equity / (entry * 100))
    return max(min(lot, max_lot), 0)

# ==============================
# CORRELATION FILTER
# ==============================
def correlation_filter(data_map, selected, candidate, threshold=0.8):
    if not selected:
        return True

    df_cand = data_map[candidate]["Close"]

    for s in selected:
        df_sel = data_map[s]["Close"]
        min_len = min(len(df_sel), len(df_cand))

        if min_len < 30:
            continue

        corr = df_sel[-min_len:].corr(df_cand[-min_len:])
        if corr > threshold:
            return False

    return True

# ==============================
# MAIN
# ==============================
def run():
    state = load_state()
    mode = state["mode"]

    # MARKET REGIME
    ihsg_df = get_data(IHSG)
    if ihsg_df is None:
        send("❌ Gagal ambil data IHSG")
        return

    ihsg_df = compute(ihsg_df)
    market = get_market_regime(ihsg_df)

    rows = []
    data_map = {}

    for s in STOCKS:
        df = get_data(s)
        if df is None or len(df) < 50:
            continue

        df = compute(df)
        data_map[s] = df

        sig, entry, sl, tp, adx, conf = signal(df, mode)

        # FILTER MARKET
        if market == "BULL" and sig == "SELL":
            continue
        if market == "BEAR" and sig == "BUY":
            continue
        if market == "SIDEWAYS":
            continue

        vol = get_volatility_regime(df)
        dyn_risk = get_dynamic_risk(RISK_PER_TRADE, 60, vol)  # simplified

        lot = calc_lot(CAPITAL_INIT, entry, sl, dyn_risk)

        score = adx * 0.5 + (10 if conf == "HIGH" else 5)

        rows.append({
            "Stock": s,
            "Signal": sig,
            "Entry": round(entry,2),
            "SL": round(sl,2),
            "TP": round(tp,2),
            "Lot": lot,
            "Vol": vol,
            "Risk": round(dyn_risk*100,2),
            "ADX": round(adx,2),
            "Conf": conf,
            "Score": round(score,2)
        })

    if not rows:
        send(f"⚠️ Market: {market}\nTidak ada sinyal")
        return

    df = pd.DataFrame(rows).sort_values("Score", ascending=False)

    selected = []
    portfolio = []

    for _, row in df.iterrows():
        if len(portfolio) >= MAX_POSITIONS:
            break

        if correlation_filter(data_map, selected, row["Stock"]):
            portfolio.append(row)
            selected.append(row["Stock"])

    top = pd.DataFrame(portfolio)

    msg = f"📊 MARKET: {market}\n\n🔥 TOP PORTFOLIO 🔥\n\n"

    for _, r in top.iterrows():
        msg += (
            f"{r['Stock']} ({r['Signal']})\n"
            f"Entry: {r['Entry']} | SL: {r['SL']} | TP: {r['TP']}\n"
            f"Lot: {r['Lot']} | Risk: {r['Risk']}%\n"
            f"Vol: {r['Vol']} | ADX: {r['ADX']}\n\n"
        )

    send(msg)

# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    run()
