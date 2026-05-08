import yfinance as yf

from app.config import (
    STOCKS,
    MIN_CONFIDENCE,
    MAX_TOP_TRADES
)

from app.strategy import (
    generate_signal
)

from app.portfolio import (

    open_position,

    update_positions,

    load_positions
)

from app.telegram import (
    send_telegram
)

# =========================
# RUN SCANNER
# =========================

def run():

    print(
        "[LOG] 🚀 SCANNER START (TRADE RANKING AI)"
    )

    ranked_trades = []

    for stock in STOCKS:

        try:

            # =========================
            # DOWNLOAD DATA
            # =========================

            df = yf.download(

                stock,

                period="3mo",

                interval="1d",

                auto_adjust=True,

                progress=False
            )

            if df.empty:

                continue

            # =========================
            # GENERATE SIGNAL
            # =========================

            signal_data = generate_signal(
                df
            )

            signal = signal_data[
                "signal"
            ]

            confidence = signal_data[
                "confidence"
            ]

            regime = signal_data[
                "regime"
            ]

            # =========================
            # SAFE PRICE FIX
            # =========================

            price = float(
                df["Close"].iloc[-1].squeeze()
            )

            # =========================
            # LOG
            # =========================

            print(

                f"[LOG] {stock} "

                f"{signal} @ {price:.2f} "

                f"| Confidence {confidence}% "

                f"| {regime}"
            )

            # =========================
            # UPDATE LIVE PNL
            # =========================

            update_positions(
                stock,
                price
            )

            # =========================
            # LIVE POSITION TELEGRAM
            # =========================

            positions = load_positions()

            for _, pos in positions.iterrows():

                if pos["status"] != "OPEN":

                    continue

                if pos["stock"] != stock:

                    continue

                pnl = round(
                    pos["pnl"],
                    0
                )

                send_telegram(

                    f"📊 LIVE POSITION\n\n"

                    f"{stock}\n"

                    f"{pos['side']}\n\n"

                    f"Entry: {pos['entry']}\n"

                    f"Current: {price:.2f}\n\n"

                    f"PnL:\n"

                    f"{pnl:,.0f}\n\n"

                    f"SL:\n"

                    f"{pos['sl']}\n\n"

                    f"TP1:\n"

                    f"{pos['tp1']}"
                )

            # =========================
            # TELEGRAM MARKET UPDATE
            # =========================

            send_telegram(

                f"🧠 MARKET UPDATE\n\n"

                f"{stock}\n\n"

                f"Signal: {signal}\n"

                f"Price: {price:.2f}\n"

                f"Confidence: {confidence}%\n"

                f"Regime: {regime}\n\n"

                f"💰 Equity:\n"

                f"100,000,000"
            )

            # =========================
            # SKIP HOLD
            # =========================

            if signal == "HOLD":

                continue

            # =========================
            # MIN CONFIDENCE
            # =========================

            if confidence < MIN_CONFIDENCE:

                continue

            ranked_trades.append({

                "stock": stock,

                "signal": signal,

                "price": price,

                "confidence": confidence,

                "regime": regime
            })

        except Exception as e:

            print(
                f"[LOG] ERROR {stock}: {e}"
            )

    # =========================
    # SORT BY CONFIDENCE
    # =========================

    ranked_trades = sorted(

        ranked_trades,

        key=lambda x: x[
            "confidence"
        ],

        reverse=True
    )

    # =========================
    # TOP AI TRADES
    # =========================

    ranked_trades = ranked_trades[
        :MAX_TOP_TRADES
    ]

    # =========================
    # OPEN POSITION
    # =========================

    for trade in ranked_trades:

        stock = trade["stock"]

        signal = trade["signal"]

        price = trade["price"]

        # =========================
        # BUY
        # =========================

        if signal == "BUY":

            tp1 = round(
                price * 1.02,
                2
            )

            tp2 = round(
                price * 1.04,
                2
            )

            sl = round(
                price * 0.98,
                2
            )

        # =========================
        # SELL
        # =========================

        else:

            tp1 = round(
                price * 0.98,
                2
            )

            tp2 = round(
                price * 0.96,
                2
            )

            sl = round(
                price * 1.02,
                2
            )

        # =========================
        # DEBUG OPEN POSITION
        # =========================

        print(

            f"[OPENING POSITION] "

            f"{stock} "

            f"{signal}"
        )

        # =========================
        # SAVE POSITION
        # =========================

        open_position(

            stock=stock,

            side=signal,

            entry=price,

            tp1=tp1,

            tp2=tp2,

            sl=sl
        )

        # =========================
        # DEBUG POSITION SAVED
        # =========================

        print(

            f"[POSITION SAVED] "

            f"{stock}"
        )

        # =========================
        # TELEGRAM ENTRY
        # =========================

        send_telegram(

            f"🚀 NEW POSITION\n\n"

            f"{stock}\n"

            f"{signal}\n\n"

            f"Entry: {price:.2f}\n"

            f"TP1: {tp1:.2f}\n"

            f"TP2: {tp2:.2f}\n"

            f"SL: {sl:.2f}\n\n"

            f"💰 Equity:\n"

            f"100,000,000"
        )

    # =========================
    # POSITION SUMMARY
    # =========================

    positions = load_positions()

    open_positions = positions[
        positions["status"] == "OPEN"
    ]

    floating = round(

        open_positions[
            "pnl"
        ].sum(),

        0
    )

    equity = (
        100000000 + floating
    )

    send_telegram(

        f"📡 OPEN POSITIONS\n\n"

        f"{len(open_positions)} OPEN\n\n"

        f"💰 Floating:\n"

        f"{floating:,.0f}\n\n"

        f"💰 Equity:\n"

        f"{equity:,.0f}"
    )

    print(
        "[LOG] ✅ SCANNER FINISHED"
    )
