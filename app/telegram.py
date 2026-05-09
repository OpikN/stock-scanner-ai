import requests

from app.config import (
    TELEGRAM_TOKEN,
    TELEGRAM_CHAT_ID
)

# =========================
# SEND TELEGRAM
# =========================
def send_telegram(message):

    try:

        if not TELEGRAM_TOKEN:

            return

        if not TELEGRAM_CHAT_ID:

            return

        url = (

            f"https://api.telegram.org/bot"
            f"{TELEGRAM_TOKEN}"
            f"/sendMessage"
        )

        requests.post(

            url,

            data={

                "chat_id":
                    TELEGRAM_CHAT_ID,

                "text":
                    message
            },

            timeout=10
        )

    except Exception as e:

        print(
            f"TELEGRAM ERROR: {e}"
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
