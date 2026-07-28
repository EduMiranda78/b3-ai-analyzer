import os
import requests


def enviar_para_telegram(
    ticker,
    sinal
):

    token = os.getenv(
        "TELEGRAM_BOT_TOKEN"
    )

    chat_id = os.getenv(
        "TELEGRAM_CHAT_ID"
    )

    if not token or not chat_id:
        return

    try:

        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={
                "chat_id": chat_id,
                "text": f"{ticker}\n\n{sinal}"
            },
            timeout=10
        )

    except Exception:
        pass