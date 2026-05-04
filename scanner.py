import yfinance as yf
import pandas as pd
import requests, os
import ta
import math

# ================= CONFIG =================
STOCKS = ["BBCA.JK","BBRI.JK","TLKM.JK","BMRI.JK","ASII.JK"]
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID   = os.getenv("CHAT_ID")

CAPITAL_INIT = 10_000_000   # modal awal
RISK_PCT     = 0.02         # 2% risk per trade
LOT_SIZE     = 100          # 1 lot IDX = 100 saham

# ================ TELEGRAM ================
def send(msg):
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Secret tidak terbaca"); return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    r = requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    print("TG:", r.status_code)

# ================ INDICATORS ==============
def compute(df):
    close = df["Close"]
    df["ema20"] = ta.trend.ema_indicator(close, 20)
    df["ema50"] = ta.trend.ema_indicator(close, 50)
    df["rsi"]   = ta.momentum.rsi(close, 14)
    df["atr"]   = ta.volatility.average_true_range(df["High"], df["Low"], close, 14)
    return df

# ================ SIGNAL ==================
def signal_row(df):
    r = df.iloc[-1]
    price = float(r["Close"])
    ema20, ema50, rsi, atr = r["ema20"], r["ema50"], r["rsi"], r["atr"]

    sig = "HOLD"
    if ema20 > ema50 and 35 < rsi < 60:
        sig = "BUY"
        sl = price - 1.5*atr
        tp = price + 2.5*atr
    elif ema20 < ema50 and 40 < rsi < 65:
        sig = "SELL"
        sl = price + 1.5*atr
        tp = price - 2.5*atr
    else:
        return {"signal":"HOLD"}

    # risk-reward
    rr = abs((tp-price)/(price-sl)) if sig=="BUY" else abs((price-tp)/(sl-price))

    # scoring
    score = 0
    score += 25
    score += 20 if (ema20>ema50 and sig=="BUY") or (ema20<ema50 and sig=="SELL") else 0
    score += 15 if (40<=rsi<=60) else 5
    score += 20 if rr>=1.5 else 10
    score += 10 if atr>0 else 0

    return {
        "signal": sig,
        "entry": round(price,2),
        "sl": round(sl,2),
        "tp": round(tp,2),
        "rr": round(rr,2),
        "score": int(score),
        "atr": float(atr)
    }

# ============ POSITION SIZING =============
def calc_lot(capital, entry, sl):
    risk_amount = capital * RISK_PCT
    risk_per_share = abs(entry - sl)

    if risk_per_share == 0:
        return 0, 0

    shares = risk_amount / risk_per_share

    # bulatkan ke lot (100 saham)
    shares = int(shares // LOT_SIZE * LOT_SIZE)

    cost = shares * entry
    return shares, int(cost)

# ============ PORTFOLIO SIM ==============
def simulate(capital, row):
    entry, sl, tp, sig = row["entry"], row["sl"], row["tp"], row["signal"]

    shares, cost = calc_lot(capital, entry, sl)
    if shares == 0:
        return capital, 0, 0

    # asumsi sederhana: hit TP (optimistic) untuk demo
    if sig == "BUY":
        pnl = (tp - entry) * shares
    else:
        pnl = (entry - tp) * shares

    new_capital = capital + pnl
    return new_capital, shares, pnl

# ================ MAIN ====================
def run():
    rows = []

    for s in STOCKS:
        try:
            df = yf.download(s, period="6mo", progress=False)
            if df is None or df.empty or len(df) < 60: continue
            if not all(c in df.columns for c in ["Close","High","Low"]): continue

            df = compute(df)
            out = signal_row(df)

            if out.get("signal") != "HOLD":
                rows.append({"Stock": s, **out})

        except Exception as e:
            print("ERR", s, e)

    if not rows:
        send("⚠️ Tidak ada sinyal hari ini")
        return

    df = pd.DataFrame(rows)

    # filter & ranking
    df = df[df["score"] >= 50].sort_values("score", ascending=False)

    if df.empty:
        df = pd.DataFrame(rows).sort_values("score", ascending=False)

    top = df.head(3)

    # ===== PORTFOLIO =====
    capital = CAPITAL_INIT
    msg = "🔥 TOP SIGNAL + AUTO LOT 🔥\n\n"

    for idx, r in enumerate(top.itertuples(), start=1):
        capital, shares, pnl = simulate(capital, r._asdict())

        lot = shares // LOT_SIZE

        msg += (
            f"{idx}) {r.Stock} — {r.signal}\n"
            f"Entry: {r.entry} | SL: {r.sl} | TP: {r.tp}\n"
            f"Lot: {lot} ({shares} saham)\n"
            f"Score: {r.score} | RR: 1:{r.rr}\n"
            f"PnL Sim: {int(pnl)}\n\n"
        )

    msg += f"💰 Modal Awal: {CAPITAL_INIT}\n"
    msg += f"💰 Modal Akhir: {int(capital)}"

    # save
    top.to_csv("data.csv", index=False)

    send(msg)

if __name__ == "__main__":
    run()
