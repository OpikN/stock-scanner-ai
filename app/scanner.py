import yfinance as yf
from datetime import datetime
import requests

from app.config import (
    STOCKS,
    DATA_PATH,
    TELEGRAM_TOKEN,
    TELEGRAM_CHAT_ID,
    MAX_TOP_TRADES,
    MIN_CONFIDENCE
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

                "chat_id":
                    TELEGRAM_CHAT_ID,

                "text":
                    msg
            },

            timeout=10
        )

    except Exception as e:

        print(e)

# =========================
# MAIN ENGINE
# =========================
def run():

    log(
        "🚀 SCANNER START "
        "(TRADE RANKING AI)"
    )

    latest_prices = {}

    candidates = []

    # =========================
    # SCAN ALL STOCKS
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

                log(f"NOT ENOUGH DATA {stock}")

                continue

            # =========================
            # APPLY INDICATORS
            # =========================
            df = apply_indicators(df)

            # =========================
            # SIGNAL ENGINE
            # =========================
            signal, price, confidence = (
                generate_signal(df)
            )

            # =========================
            # MARKET REGIME
            # =========================
            regime = detect_market_regime(df)

            # =========================
            # FIX FLOAT
            # =========================
            try:

                price = float(price)

            except:

                close = df["Close"]

                if len(close.shape) > 1:

                    price = float(
                        close.iloc[-1, 0]
                    )

                else:

                    price = float(
                        close.iloc[-1]
                    )

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

                "stock":
                    stock,

                "signal":
                    signal,

                "price":
                    round(price, 0),

                "confidence":
                    confidence,

                "regime":
                    regime
            }

            save_trade(
                DATA_PATH,
                trade_data
            )

            # =========================
            # LOG SIGNAL
            # =========================
            log(

                f"{stock} "

                f"{signal} "

                f"@ {price:.0f} "

                f"| Confidence "

                f"{confidence}% "

                f"| {regime}"
            )

            # =========================
            # STORE CANDIDATE
            # =========================
            if signal in ["BUY", "SELL"]:

                if confidence >= MIN_CONFIDENCE:

                    candidates.append({

                        "stock":
                            stock,

                        "signal":
                            signal,

                        "price":
                            price,

                        "confidence":
                            confidence,

                        "regime":
                            regime
                    })

        except Exception as e:

            log(
                f"❌ ERROR: "
                f"{stock} {e}"
            )

    # =========================
    # AI TRADE RANKING
    # =========================
    ranked = sorted(

        candidates,

        key=lambda x: x["confidence"],

        reverse=True
    )

    # =========================
    # TOP AI TRADES
    # =========================
    top_trades = ranked[:MAX_TOP_TRADES]

    # =========================
    # EXECUTE
    # =========================
    for trade in top_trades:

        try:

            stock = trade["stock"]

            signal = trade["signal"]

            price = trade["price"]

            confidence = trade["confidence"]

            regime = trade["regime"]

            # =========================
            # OPEN POSITION
            # =========================
            open_position(

                stock=stock,

                side=signal,

                entry=price
            )

            # =========================
            # TELEGRAM MESSAGE
            # =========================
            msg = (

                f"🔥 TOP AI TRADE\n\n"

                f"{stock}\n"

                f"{signal} @ {price:.0f}\n\n"

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
                f"OPEN ERROR: {e}"
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
            f"UPDATE ERROR: {e}"
        )

# =========================
# RUN DIRECT
# =========================
if __name__ == "__main__":

    run()
