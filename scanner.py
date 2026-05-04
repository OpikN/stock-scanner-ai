import yfinance as yf
import pandas as pd
import requests, os
import ta

# ================= CONFIG =================
STOCKS = ["BBCA.JK","BBRI.JK","TLKM.JK","BMRI.JK","ASII.JK"]
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID   = os.getenv("CHAT_ID")

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
    # trend + pullback
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

    rr = abs((tp-price)/(price-sl)) if sig=="BUY" else abs((price-tp)/(sl-price))

    # scoring sederhana tapi efektif
    score = 0
    score += 25 if sig!="HOLD" else 0
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
        "score": int(score)
    }

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
        send("⚠️ Tidak ada sinyal kuat hari ini")
        return

    df = pd.DataFrame(rows)

    # FILTER: hanya yang cukup kuat
    df = df[df["score"] >= 60].sort_values("score", ascending=False)

    if df.empty:
        send("⚠️ Tidak ada sinyal kuat (>=60)")
        return

    # TOP 3 saja
    top = df.head(3)

    # simpan untuk dashboard
    top.to_csv("data.csv", index=False)

    # format pesan
    msg = "🔥 TOP SIGNAL HARI INI 🔥\n\n"
    for i, r in top.iterrows():
        msg += (
            f"{len(msg)}\n"  # nomor sederhana
        )
    # nomor yang rapi
    msg = "🔥 TOP SIGNAL HARI INI 🔥\n\n"
    for idx, r in enumerate(top.itertuples(), start=1):
        msg += (
            f"{idx}) {r.Stock} — {r.signal}\n"
            f"Entry: {r.entry} | SL: {r.sl} | TP: {r.tp}\n"
            f"Score: {r.score} | RR: 1:{r.rr}\n\n"
        )

    send(msg)

if __name__ == "__main__":
    run()
