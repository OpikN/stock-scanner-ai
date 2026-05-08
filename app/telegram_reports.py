from app.telegram import send_telegram


def send_market_update(
    stock,
    signal,
    price,
    confidence,
    regime,
    equity
):

    send_telegram(

        f"🧠 MARKET UPDATE\n\n"

        f"{stock}\n\n"

        f"Signal: {signal}\n"

        f"Price: {price:.2f}\n"

        f"Confidence: {confidence}%\n"

        f"Regime: {regime}\n\n"

        f"💰 Equity:\n"

        f"{equity:,.0f}"
    )


def send_new_position(
    stock,
    side,
    entry,
    tp1,
    tp2,
    sl,
    equity
):

    send_telegram(

        f"🚀 NEW POSITION\n\n"

        f"{stock}\n"

        f"{side}\n\n"

        f"Entry: {entry:.2f}\n\n"

        f"TP1: {tp1:.2f}\n"

        f"TP2: {tp2:.2f}\n\n"

        f"SL: {sl:.2f}\n\n"

        f"💰 Equity: {equity:,.0f}"
    )


def send_trailing_update(
    stock,
    new_sl
):

    send_telegram(

        f"📈 TRAILING UPDATE\n\n"

        f"{stock}\n\n"

        f"New SL: {new_sl:.2f}"
    )


def send_partial_close(
    stock,
    pnl
):

    send_telegram(

        f"💰 PARTIAL CLOSE\n\n"

        f"{stock}\n\n"

        f"PnL: {pnl:,.0f}"
    )


def send_position_closed(
    stock,
    reason,
    pnl,
    equity
):

    send_telegram(

        f"🔥 POSITION CLOSED\n\n"

        f"{stock}\n\n"

        f"{reason}\n\n"

        f"PnL: {pnl:,.0f}\n\n"

        f"💰 Equity: {equity:,.0f}"
    )
