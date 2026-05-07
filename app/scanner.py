import yfinance as yf
import pandas as pd

from app.config import (
    STOCKS,
    DATA_PATH,
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

from app.telegram import (
    send_telegram
)

# =========================
# SAFE FLOAT
# =========================
def safe_float(value):

    try:

        if isinstance(
            value,
            pd.Series
        ):

            return float(
                value.iloc[0]
            )

        return float(value)

    except:

        return 0

# =========================
# MAIN
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

    for stock in STOCKS:

        try:

            df = yf.download(

                stock,

                period="3mo",

                interval="1d",

                auto_adjust=True,

                progress=False
            )

            if df.empty:
                continue

            df = apply_indicators(df)

            if df.empty:
                continue

            signal, price, confidence = (
                generate_signal(df)
            )

            regime = (
                detect_market_regime(df)
            )

            if price <= 0:

                price = safe_float(

                    df["Close"]
                    .iloc[-1]
                )

            latest_prices[stock] = price

            log(

                f"{stock} "

                f"{signal} "

                f"@ {price:.2f} "

                f"| Confidence "

                f"{confidence}% "

                f"| {regime}"
            )

            send_telegram(

                f"🧠 MARKET UPDATE\n\n"

                f"{stock}\n"

                f"Signal: {signal}\n"

                f"Price: {price:.2f}\n"

                f"Confidence: "
                f"{confidence}%\n"

                f"Regime: {regime}"
            )

            trade_data = {

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
            }

            save_trade(
                DATA_PATH,
                trade_data
            )

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
                f"{stock} ERROR {e}"
            )

    ranked = sorted(

        candidates,

        key=lambda x:
            x["confidence"],

        reverse=True
    )

    top = ranked[:MAX_TOP_TRADES]

    for trade in top:

        open_position(

            stock=trade["stock"],

            side=trade["signal"],

            entry=trade["price"]
        )

    update_positions(
        latest_prices
    )

if __name__ == "__main__":

    run()
