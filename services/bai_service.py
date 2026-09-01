import os

import requests


DEFAULT_BASE_URL = "https://api.b.ai/v1"
DEFAULT_MODEL = "deepseek-v4-flash"

SYSTEM_PROMPT = """
Você é a camada explicativa de um analisador técnico
do mercado acionário brasileiro.

O sinal de COMPRA, VENDA ou NEUTRO já foi calculado
pelo motor técnico do sistema.

Regras obrigatórias:
- Não altere o sinal calculado.
- Não recalcule o sinal.
- Não invente dados, notícias, fundamentos ou preços.
- Use exclusivamente as informações fornecidas.
- Diferencie fatos de interpretações.
- Responda em português do Brasil.
- Produza somente o relatório final solicitado.
""".strip()


def _esta_habilitada() -> bool:
    valor = os.getenv(
        "BAI_ENABLED",
        "1",
    ).strip().lower()

    return valor not in {
        "0",
        "false",
        "no",
        "off",
    }


def gerar_relatorio(
    prompt: str,
) -> str:
    if not _esta_habilitada():
        raise RuntimeError(
            "B.AI desativada."
        )

    api_key = os.getenv(
        "BAI_API_KEY",
        "",
    ).strip()

    if not api_key:
        raise RuntimeError(
            "BAI_API_KEY não configurada."
        )

    base_url = os.getenv(
        "BAI_BASE_URL",
        DEFAULT_BASE_URL,
    ).rstrip("/")

    modelo = os.getenv(
        "BAI_MODEL",
        DEFAULT_MODEL,
    ).strip()

    try:
        max_tokens = int(
            os.getenv(
                "BAI_MAX_TOKENS",
                "900",
            )
        )
    except ValueError:
        max_tokens = 900

    try:
        timeout = float(
            os.getenv(
                "BAI_TIMEOUT",
                "20",
            )
        )
    except ValueError:
        timeout = 20.0

    payload = {
        "model": modelo,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "max_tokens": max_tokens,
        "temperature": 0.2,
    }

    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": (
                    f"Bearer {api_key}"
                ),
                "Content-Type": (
                    "application/json"
                ),
            },
            json=payload,
            timeout=timeout,
        )
    except requests.RequestException as exc:
        raise RuntimeError(
            "Falha de conexão com a B.AI."
        ) from exc

    if response.status_code != 200:
        raise RuntimeError(
            "B.AI respondeu HTTP "
            f"{response.status_code}."
        )

    try:
        dados = response.json()
    except ValueError as exc:
        raise RuntimeError(
            "B.AI retornou JSON inválido."
        ) from exc

    try:
        texto = (
            dados["choices"][0]
            ["message"]
            .get("content", "")
            .strip()
        )
    except (
        KeyError,
        IndexError,
        TypeError,
        AttributeError,
    ) as exc:
        raise RuntimeError(
            "Resposta inesperada da B.AI."
        ) from exc

    if not texto:
        raise RuntimeError(
            "B.AI retornou conteúdo vazio."
        )

    return texto
