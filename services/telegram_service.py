import logging
import os

import requests


logger = logging.getLogger(__name__)


def enviar_para_telegram(
    ticker: str,
    sinal: str,
    *,
    setup_aprovado: bool | None = None,
    qualidade_plano: str | None = None,
) -> bool:
    token = os.getenv(
        "TELEGRAM_BOT_TOKEN"
    )

    chat_id = os.getenv(
        "TELEGRAM_CHAT_ID"
    )

    if not token or not chat_id:
        return False

    linhas = [
        f"📈 {ticker}",
        "",
        f"Viés técnico: {sinal}",
    ]

    if (
        setup_aprovado is not None
        and sinal != "NEUTRO"
    ):
        linhas.append(
            "Plano 2R: "
            + (
                "APROVADO"
                if setup_aprovado
                else "NÃO APROVADO"
            )
        )

    if qualidade_plano:
        linhas.append(
            "Qualidade do plano: "
            f"{qualidade_plano}"
        )

    linhas.extend(
        [
            "",
            (
                "Conteúdo informativo; "
                "não é recomendação de investimento."
            ),
        ]
    )

    try:
        response = requests.post(
            (
                "https://api.telegram.org/"
                f"bot{token}/sendMessage"
            ),
            data={
                "chat_id": chat_id,
                "text": "\n".join(
                    linhas
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
