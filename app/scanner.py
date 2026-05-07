import yfinance as yf
from datetime import datetime
import requests

from app.config import (
    STOCKS,
    DATA_PATH,
    TELEGRAM_TOKEN,
    TELEGRAM_CHAT_ID
)

from app.indicators import apply_indicators

from app.strategy import (
    generate_signal,
    detect_market_regime
)

from app.storage import save_trade

from app.logger import log

from app.portfolio import (
    open_position,
    update_positions
)

# =========================
# TELEGRAM
# =========================
def send_telegram(msg):

    if not TELEGRAM_TOKEN:

        return

    if not TELEGRAM_CHAT_ID:

        return

    try:

        url = (
            f"https://api.telegram.org/"
            f"bot{TELEGRAM_TOKEN}/sendMessage"
        )

        requests.post(
            url,
            data={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": msg
            },
            timeout=10
        )

    except:

        pass

# =========================
# MAIN SCANNER
# =========================
def run():

    log(
        "🚀 SCANNER START "
        "(AI CONFIDENCE ENGINE)"
    )

    latest_prices = {}

    # =========================
    # LOOP STOCK
    # =========================
    for stock in STOCKS:

        try:

            # =========================
            # DOWNLOAD DATA
            # =========================
            df = yf.download(
                stock,
                period="5d",
                interval="1h",
                progress=False
            )

            # =========================
            # VALIDATION
            # =========================
            if df is None:

                log(f"SKIP {stock}")

                continue

            if df.empty:

                log(f"EMPTY {stock}")

                continue

            if len(df) < 20:

                log(f"DATA KURANG {stock}")

                continue

            # =========================
            # INDICATORS
            # =========================
            df = apply_indicators(df)

            # =========================
            # SIGNAL
            # =========================
            signal, price, confidence = (
                generate_signal(df)
            )

            # =========================
            # MARKET REGIME
            # =========================
            regime = detect_market_regime(df)

            # =========================
            # FLOAT FIX
            # =========================
            try:

                price = float(price)

            except:

                close = df["Close"]

                if hasattr(close, "iloc"):

                    if len(close.shape) > 1:

                        price = float(
                            close.iloc[-1, 0]
                        )

                    else:

                        price = float(
                            close.iloc[-1]
                        )

                else:

                    price = 0

            # =========================
            # SAVE PRICE
            # =========================
            latest_prices[stock] = price

            # =========================
            # SAVE SIGNAL
            # =========================
            trade_data = {

                "time":
                    datetime.utcnow()
                    .strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),

                "stock": stock,

                "signal": signal,

                "price": round(price, 0),

                "confidence": confidence,

                "regime": regime
            }

            save_trade(
                DATA_PATH,
                trade_data
            )

            # =========================
            # OPEN POSITION
            # =========================
            if signal in ["BUY", "SELL"]:

                open_position(
                    stock=stock,
                    side=signal,
                    entry=price
                )

            # =========================
            # TELEGRAM MESSAGE
            # =========================
            msg = (
                f"{stock} "
                f"{signal} "
                f"@ {price:.0f}\n"
                f"🧠 Confidence: "
                f"{confidence}%\n"
                f"📈 Regime: "
                f"{regime}"
            )

            send_telegram(msg)

            # =========================
            # LOG
            # =========================
            log(msg)

        except Exception as e:

            log(
                f"❌ ERROR: "
                f"{stock} {e}"
            )

    # =========================
    # UPDATE POSITIONS
    # =========================
    try:

        update_positions(
            latest_prices
        )

    except Exception as e:

        log(
            f"UPDATE POSITION ERROR: "
            f"{e}"
        )

# =========================
# RUN DIRECT
# =========================
if __name__ == "__main__":

    run()
