import yfinance as yf
from datetime import datetime
import requests

from .config import STOCKS, DATA_PATH, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from .indicators import apply_indicators
from .strategy import generate_signal
from .storage import save_trade
from .logger import log

def send_telegram(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=10)
    except:
        pass

def run():
    log("🚀 SCANNER START")

    for stock in STOCKS:
        try:
            df = yf.download(stock, period="5d", interval="1h", progress=False)

            if df is None or df.empty or len(df) < 20:
                log(f"SKIP {stock} (data kurang)")
                continue

            df = apply_indicators(df)
            signal, price = generate_signal(df)

            data = {
                "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "stock": stock,
                "signal": signal,
                "price": round(price, 0)
            }

            save_trade(DATA_PATH, data)

            msg = f"{stock} {signal} @ {price:.0f}"
            send_telegram(msg)

            log(msg)

        except Exception as e:
            log(f"ERROR {stock}: {e}")
