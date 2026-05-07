import yfinance as yf
from datetime import datetime
import requests
import pandas as pd

from app.config import (
    STOCKS,
    DATA_PATH,
    TELEGRAM_TOKEN,
    TELEGRAM_CHAT_ID,
    MAX_TOP_TRADES,
    MIN_CONFIDENCE
)

from app.indicators import (
    apply_indicators
)

from app.strategy import (
    generate_signal,
    detect_market_regime
)

from app.storage import (
    save_trade
)

from app.logger import log

from app.portfolio import (
    open_position,
    update_positions
)

# =========================
# SAFE FLOAT
# =========================
def safe_float(value):

    try:

        if isinstance(value, pd.Series):

            return float(value.iloc[0])

        return float(value)

    except:

        return 0

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

        print(
            f"TELEGRAM ERROR: {e}"
        )

# =========================
# MAIN ENGINE
# =========================
def run():

    log(
        "🚀 SCANNER START "
        "(TRADE RANKING AI)"
    )

    send_telegram(
    "🔥 AI Scanner Online"
    )
    
    latest_prices = {}

    candidates = []

    # =========================
    # SCAN STOCKS
    # =========================
    for stock in STOCKS:

        try:

            # =========================
            # DOWNLOAD MARKET DATA
            # =========================
            df = yf.download(

                stock,

                period="3mo",

                interval="1d",

                auto_adjust=True,

                progress=False
            )

            # =========================
            # VALIDATION
            # =========================
            if df is None:

                log(
                    f"{stock} "
                    f"NO DATA"
                )

                continue

            if df.empty:

                log(
                    f"{stock} "
                    f"EMPTY"
                )

                continue

            if len(df) < 30:

                log(
                    f"{stock} "
                    f"NOT ENOUGH DATA"
                )

                continue

            # =========================
            # APPLY INDICATORS
            # =========================
            df = apply_indicators(df)

            if df.empty:

                log(
                    f"{stock} "
                    f"INDICATOR EMPTY"
                )

                continue

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
            # SAFE PRICE
            # =========================
            if price <= 0:

                last = df.iloc[-1]

                price = safe_float(
                    last["Close"]
                )

            # =========================
            # FINAL VALIDATION
            # =========================
            if price <= 0:

                log(
                    f"{stock} "
                    f"INVALID PRICE"
                )

                continue

            latest_prices[stock] = price

            # =========================
            # SAVE TRADE
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
                    round(price, 2),

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
            # LOG
            # =========================
            log(

                f"{stock} "

                f"{signal} "

                f"@ {price:.2f} "

                f"| Confidence "

                f"{confidence}% "

                f"| {regime}"
            )

            # =========================
            # CANDIDATES
            # =========================
            if (

                signal in
                ["BUY", "SELL"]

                and

                confidence >=
                MIN_CONFIDENCE
            ):

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
    # AI RANKING
    # =========================
    ranked = sorted(

        candidates,

        key=lambda x:
            x["confidence"],

        reverse=True
    )

    # =========================
    # TOP AI TRADES
    # =========================
    top_trades = ranked[
        :MAX_TOP_TRADES
    ]

    # =========================
    # EXECUTE
    # =========================
    for trade in top_trades:

        try:

            stock = trade["stock"]

            signal = trade["signal"]

            price = trade["price"]

            confidence = (
                trade["confidence"]
            )

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
            # TELEGRAM
            # =========================
            msg = (

                f"🔥 TOP AI TRADE\n\n"

                f"{stock}\n"

                f"{signal} "
                f"@ {price:.2f}\n\n"

                f"🧠 Neural Score: "
                f"{confidence}%\n"

                f"📈 Regime: "
                f"{regime}"
            )

            send_telegram(msg)

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
# RUN
# =========================
if __name__ == "__main__":

    run()
