import yfinance as yf
import pandas as pd
import time

from app.config import (
    STOCKS,
    MIN_CONFIDENCE
)

from app.indicators import (
    apply_indicators
)

from app.strategy import (
    generate_signal,
    detect_market_regime
)

from app.portfolio import (
    open_position,
    update_positions
)

from app.telegram import (
    send_telegram
)

from app.telegram_reports import (
    send_high_confidence_alert
)

# =========================
# LOGGER
# =========================
def log(message):

    print(f"[LOG] {message}")

# =========================
# DOWNLOAD MARKET DATA
# =========================
def get_data(stock):

    try:

        df = yf.download(

            stock,

            period="60d",

            interval="5m",

            auto_adjust=True,

            progress=False
        )

        if df.empty:

            return pd.DataFrame()

        df = apply_indicators(df)

        return df

    except Exception as e:

        print(
            f"DATA ERROR {stock}: {e}"
        )

        return pd.DataFrame()

# =========================
# MAIN SCANNER
# =========================
def run():

    log(
        "🚀 SCANNER START (TRADE RANKING AI)"
    )

    send_telegram(
        "🔥 AI Scanner Online"
    )

    latest_prices = {}

    # =========================
    # LOOP STOCKS
    # =========================
    for stock in STOCKS:

        try:

            df = get_data(stock)

            if df.empty:

                continue

            # =========================
            # SIGNAL
            # =========================
            (
                signal,
                price,
                confidence
            ) = generate_signal(df)

            # =========================
            # MARKET REGIME
            # =========================
            regime = detect_market_regime(
                df
            )

            # =========================
            # SAVE PRICE
            # =========================
            latest_prices[stock] = price

            # =========================
            # LOG TERMINAL
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
            # TELEGRAM UPDATE
            # =========================
            send_telegram(

                f"🧠 MARKET UPDATE\n\n"

                f"{stock}\n\n"

                f"Signal: "
                f"{signal}\n"

                f"Price: "
                f"{price:.2f}\n"

                f"Confidence: "
                f"{confidence}%\n"

                f"Regime: "
                f"{regime}"
            )

            # =========================
            # HIGH CONFIDENCE ALERT
            # =========================
            if confidence >= 80:

                send_high_confidence_alert(

                    stock=stock,

                    signal=signal,

                    confidence=confidence,

                    regime=regime,

                    price=price
                )

            # =========================
            # OPEN POSITION
            # =========================
            if (

                signal in [
                    "BUY",
                    "SELL"
                ]

                and

                confidence >= MIN_CONFIDENCE
            ):

                open_position(

                    stock=stock,

                    side=signal,

                    entry=price
                )

        except Exception as e:

            print(
                f"SCANNER ERROR {stock}: {e}"
            )

    # =========================
    # UPDATE PORTFOLIO
    # =========================
    update_positions(
        latest_prices
    )

    log(
        "✅ SCANNER FINISHED"
    )
