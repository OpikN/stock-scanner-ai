import yfinance as yf
from datetime import datetime
import requests

from app.config import STOCKS, DATA_PATH, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from app.indicators import apply_indicators
from app.strategy import generate_signal
from app.storage import save_trade
from app.logger import log
from app.portfolio import open_position, update_positions


# =========================
# TELEGRAM
# =========================
def send_telegram(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=10)
    except:
        pass


# =========================
# MAIN SCANNER
# =========================
def run():
    log("🚀 SCANNER START")

    latest_prices = {}

    for stock in STOCKS:
        try:
            df = yf.download(stock, period="5d", interval="1h", progress=False)

            if df is None or df.empty or len(df) < 30:
                log(f"SKIP {stock} (data kurang)")
                continue

            df = apply_indicators(df)

            signal, price = generate_signal(df)
            price = float(price)

            latest_prices[stock] = price

            # =========================
            # SKIP HOLD (PENTING 🔥)
            # =========================
            if signal == "HOLD":
                log(f"{stock} HOLD")
                continue

            # =========================
            # SAVE SIGNAL
            # =========================
            data = {
                "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "stock": stock,
                "signal": signal,
                "price": round(price, 0)
            }

            save_trade(DATA_PATH, data)

            # =========================
            # TP SL
            # =========================
            if signal == "BUY":
                tp = price * 1.03
                sl = price * 0.98
            else:
                tp = price * 0.97
                sl = price * 1.02

            # =========================
            # OPEN POSITION (NO DUPLICATE 🔥)
            # =========================
            opened = open_position(stock, signal, price, tp, sl)

            if opened:
                msg = f"{stock} {signal} @ {price:.0f}"
                send_telegram(msg)
                log(msg)
            else:
                log(f"{stock} posisi sudah ada")

        except Exception as e:
            log(f"ERROR {stock}: {e}")

    # =========================
    # UPDATE TP/SL
    # =========================
    update_positions(latest_prices)
