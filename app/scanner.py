import json
import os

import yfinance as yf

from app.strategy import (
    generate_signal
)

from app.telegram_reports import (
    send_market_update
)

WATCHLIST = [

    "BBCA.JK",

    "BBRI.JK",

    "TLKM.JK"

]


def run():

    print(
        "[SCANNER START]"
    )

    positions = []

    floating_pnl = 0

    market_regime = (
        "TRENDING"
    )

    for stock in WATCHLIST:

        try:

            data = yf.download(

                stock,

                period="5d",

                interval="5m",

                progress=False

            )

            if data.empty:

                continue

            close_price = float(

                data["Close"].iloc[-1]

            )

            result = generate_signal(
                data
            )

            signal = result[
                "signal"
            ]

            confidence = result[
                "confidence"
            ]

            # =========================
            # TELEGRAM
            # =========================

            send_market_update(

                stock=stock,

                signal=signal,

                price=close_price,

                confidence=confidence,

                regime=market_regime

            )

            # =========================
            # SAVE POSITION
            # =========================

            if signal in [

                "BUY",

                "SELL"

            ]:

                positions.append({

                    "stock": stock,

                    "side": signal,

                    "entry_price": round(
                        close_price,
                        2
                    ),

                    "current_price": round(
                        close_price,
                        2
                    ),

                    "pnl": 0,

                    "sl": round(
                        close_price * 0.99,
                        2
                    ),

                    "tp1": round(
                        close_price * 1.02,
                        2
                    )

                })

        except Exception as e:

            print(
                f"ERROR {stock}: {e}"
            )

    # =========================
    # LIVE JSON
    # =========================

    live_data = {

        "equity": 100000000,

        "floating_pnl": floating_pnl,

        "open_positions": positions,

        "market_regime": market_regime

    }

    os.makedirs(
        "data",
        exist_ok=True
    )

    with open(

        "data/live_data.json",

        "w"

    ) as f:

        json.dump(

            live_data,

            f,

            indent=4

        )

    print(
        "[LIVE JSON UPDATED]"
    )

    print(
        "[SCANNER FINISHED]"
    )


if __name__ == "__main__":

    run()
