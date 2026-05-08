import os
import json
import pandas as pd
import yfinance as yf

from app.strategy import generate_signal

from app.portfolio import (
    open_position,
    update_positions,
    get_open_positions,
    calculate_equity
)

from app.telegram_reports import (
    send_market_update,
    send_position_summary
)

WATCHLIST = [
    "BBCA.JK",
    "BBRI.JK",
    "TLKM.JK"
]


def run():

    print(
        "[LOG] 🚀 SCANNER START (TRADE RANKING AI)"
    )

    market_regime = "TRENDING"

    # =========================
    # PROCESS STOCKS
    # =========================

    for stock in WATCHLIST:

        try:

            data = yf.download(

                stock,

                period="5d",

                interval="5m",

                progress=False

            )

            if data.empty:

                print(
                    f"[LOG] EMPTY DATA: {stock}"
                )

                continue

            close_data = data["Close"]

            # FIX DATAFRAME / SERIES
            if hasattr(close_data, "columns"):

                close_price = float(
                    close_data.iloc[-1, 0]
                )

            else:

                close_price = float(
                    close_data.iloc[-1]
                )

            signal_data = generate_signal(
                data
            )

            signal = signal_data["signal"]

            confidence = signal_data["confidence"]

            # =========================
            # UPDATE EXISTING POSITIONS
            # =========================

            update_positions(
                stock,
                close_price
            )

            # =========================
            # OPEN NEW POSITION
            # =========================

            if signal in ["BUY", "SELL"]:

                print(

                    f"[OPENING POSITION] "
                    f"{stock} "
                    f"{signal}"

                )

                open_position(

                    stock,

                    signal,

                    close_price,

                    round(

                        close_price * 1.01,

                        2

                    ) if signal == "SELL" else round(

                        close_price * 0.99,

                        2

                    ),

                    round(

                        close_price * 0.98,

                        2

                    ) if signal == "SELL" else round(

                        close_price * 1.02,

                        2

                    ),

                    round(

                        close_price * 0.96,

                        2

                    ) if signal == "SELL" else round(

                        close_price * 1.04,

                        2

                    )

                )

                print(

                    f"[POSITION SAVED] "
                    f"{stock}"

                )

            # =========================
            # TELEGRAM MARKET UPDATE
            # =========================

            send_market_update(

                stock=stock,

                signal=signal,

                price=close_price,

                confidence=confidence,

                regime=market_regime

            )

        except Exception as e:

            print(
                f"[LOG] ERROR {stock}: {e}"
            )

    # =========================
    # LOAD POSITIONS
    # =========================

    open_positions = get_open_positions()

    # =========================
    # CALCULATE EQUITY
    # =========================

    account_data = calculate_equity()

    live_equity = account_data["live_equity"]

    floating_pnl = account_data["floating_pnl"]

    # =========================
    # LIVE DASHBOARD JSON
    # =========================

    positions_data = []

    if not open_positions.empty:

        for _, row in open_positions.iterrows():

            positions_data.append({

                "stock": row["stock"],

                "side": row["side"],

                "entry": float(
                    row["entry_price"]
                ),

                "current": float(
                    row["current_price"]
                ),

                "pnl": float(
                    row["pnl"]
                ),

                "sl": float(
                    row["sl"]
                ),

                "tp1": float(
                    row["tp1"]
                ),

                "tp2": float(
                    row["tp2"]
                )

            })

    live_dashboard = {

        "equity": live_equity,

        "floating_pnl": floating_pnl,

        "open_positions": len(
            open_positions
        ),

        "market_regime": market_regime,

        "positions": positions_data

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

            live_dashboard,

            f,

            indent=4

        )

    print(
        "[LIVE JSON UPDATED]"
    )

    # =========================
    # TELEGRAM POSITION SUMMARY
    # =========================

    send_position_summary(

        open_count=len(
            open_positions
        ),

        floating_pnl=floating_pnl,

        equity=live_equity

    )

    print(
        "[LOG] ✅ SCANNER FINISHED"
    )


if __name__ == "__main__":

    run()
