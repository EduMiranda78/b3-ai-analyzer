import logging
import os

import requests


logger = logging.getLogger(__name__)


def enviar_para_telegram(
    ticker: str,
    sinal: str,
) -> bool:
    token = os.getenv(
        "TELEGRAM_BOT_TOKEN"
    )

    chat_id = os.getenv(
        "TELEGRAM_CHAT_ID"
    )

    if not token or not chat_id:
        return False

    try:
        response = requests.post(
            (
                "https://api.telegram.org/"
                f"bot{token}/sendMessage"
            ),
            data={
                "chat_id": chat_id,
                "text": (
                    f"📈 {ticker}\n\n"
                    f"Sinal técnico: {sinal}"
                ),
            },
            timeout=3,
        )

        response.raise_for_status()

        return True

    except requests.RequestException:
        logger.warning(
            "Falha ao enviar mensagem ao Telegram.",
            exc_info=True,
        )

        return False
