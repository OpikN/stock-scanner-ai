import requests

import os

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN"
)

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID"
)

# =========================
# SEND TELEGRAM MESSAGE
# =========================

def send_telegram_message(message):

    try:

        url = (

            f"https://api.telegram.org/bot"
            f"{TELEGRAM_BOT_TOKEN}"
            f"/sendMessage"

        )

        payload = {

            "chat_id": TELEGRAM_CHAT_ID,

            "text": message

        }

        requests.post(

            url,

            data=payload,

            timeout=10

        )

    except Exception as e:

        print(
            f"TELEGRAM ERROR: {e}"
        )


# =========================
# MARKET UPDATE
# =========================

def send_market_update(

    stock,

    signal,

    price,

    confidence,

    regime

):

    message = f"""

🧠 MARKET UPDATE

{stock}

Signal: {signal}

Price: {price:.2f}

Confidence: {confidence}%

Regime: {regime}

"""

    send_telegram_message(
        message
    )


# =========================
# LIVE POSITION
# =========================

def send_live_position(

    stock,

    side,

    entry,

    current,

    pnl,

    sl,

    tp1

):

    message = f"""

📊 LIVE POSITION

{stock}

{side}

Entry: {entry}

Current: {current}

PnL:
{pnl:,.0f}

SL:
{sl}

TP1:
{tp1}

"""

    send_telegram_message(
        message
    )


# =========================
# POSITION SUMMARY
# =========================

def send_position_summary(

    open_count,

    floating_pnl,

    equity

):

    message = f"""

📡 OPEN POSITIONS

{open_count} OPEN

💰 Floating:
{floating_pnl:,.0f}

💰 Equity:
{equity:,.0f}

"""

    send_telegram_message(
        message
    )
