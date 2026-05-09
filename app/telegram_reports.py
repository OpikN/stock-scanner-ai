import os
import requests

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN"
)

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID"
)


def send_market_update(

    stock,

    signal,

    price,

    confidence,

    regime

):

    if not TELEGRAM_BOT_TOKEN:

        print(
            "NO TELEGRAM TOKEN"
        )

        return

    text = f"""
🧠 MARKET UPDATE

{stock}

Signal:
{signal}

Price:
{price}

Confidence:
{confidence}%

Regime:
{regime}
"""

    url = (

        f"https://api.telegram.org/bot"

        f"{TELEGRAM_BOT_TOKEN}"

        f"/sendMessage"

    )

    payload = {

        "chat_id": TELEGRAM_CHAT_ID,

        "text": text

    }

    try:

        requests.post(

            url,

            json=payload,

            timeout=10

        )

        print(
            f"[TELEGRAM SENT] {stock}"
        )

    except Exception as e:

        print(
            f"TELEGRAM ERROR: {e}"
        )
