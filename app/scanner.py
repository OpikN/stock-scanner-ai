import yfinance as yf
import pandas as pd

from app.config import (
    STOCKS,
    MIN_CONFIDENCE,
    TP1_PERCENT,
    TP2_PERCENT,
    SL_PERCENT
)

from app.strategy import (
    generate_signal
)

from app.portfolio import (
    open_position,
    load_positions,
    get_live_equity
)

from app.telegram_reports import (
    send_market_update,
    send_new_position
)


def run():

    print(
        "[LOG] 🚀 SCANNER START (TRADE RANKING AI)"
    )

    positions = load_positions()

    for stock in STOCKS:

        try:

            df = yf.download(

                stock,

                period="60d",

                interval="5m",

                progress=False
            )

            if df.empty:

                print(
                    f"[LOG] EMPTY DATA {stock}"
                )

                continue

            signal_data = generate_signal(df)

            signal = signal_data["signal"]

            confidence = signal_data["confidence"]

            regime = signal_data["regime"]

            price = float(
            df["Close"].squeeze().iloc[-1]
            )
            
            

            print(

                f"[LOG] "

                f"{stock} "

                f"{signal} "

                f"@ {price:.2f} "

                f"| Confidence {confidence}% "

                f"| {regime}"
            )

            equity = get_live_equity()

            send_market_update(

                stock=stock,

                signal=signal,

                price=price,

                confidence=confidence,

                regime=regime,

                equity=equity
            )

            if confidence < MIN_CONFIDENCE:

                continue

            if signal not in ["BUY", "SELL"]:

                continue

            existing = positions[

                (
                    positions["stock"] == stock
                )

                &

                (
                    positions["status"] == "OPEN"
                )
            ]

            if not existing.empty:

                continue

            tp1 = (

                price *
                (
                    1 + TP1_PERCENT
                )

                if signal == "BUY"

                else

                price *
                (
                    1 - TP1_PERCENT
                )
            )

            tp2 = (

                price *
                (
                    1 + TP2_PERCENT
                )

                if signal == "BUY"

                else

                price *
                (
                    1 - TP2_PERCENT
                )
            )

            sl = (

                price *
                (
                    1 - SL_PERCENT
                )

                if signal == "BUY"

                else

                price *
                (
                    1 + SL_PERCENT
                )
            )

            open_position(

                stock=stock,

                side=signal,

                entry=price
            )

            send_new_position(

                stock=stock,

                side=signal,

                entry=price,

                tp1=tp1,

                tp2=tp2,

                sl=sl,

                equity=equity
            )

        except Exception as e:

            print(
                f"[LOG] ERROR {stock}: {e}"
            )

    print(
        "[LOG] ✅ SCANNER FINISHED"
    )
