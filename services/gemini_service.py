import os
from functools import lru_cache

from google import genai
from google.genai import types


@lru_cache(maxsize=1)
def _obter_cliente():
    api_key = os.getenv(
        "GOOGLE_API_KEY"
    )

    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY não configurada."
        )

    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            timeout=15_000,
        ),
    )


def _configuracao_modelo(
    modelo: str,
):
    # Gemini 3 usa thinking_level. A série 2.5
    # usa thinking_budget. Mantemos compatibilidade
    # caso o usuário escolha um modelo 2.5 no .env.
    if modelo.startswith(
        "gemini-3"
    ):
        thinking_config = (
            types.ThinkingConfig(
                thinking_level="low",
            )
        )
    else:
        thinking_config = (
            types.ThinkingConfig(
                thinking_budget=0,
            )
        )

    return types.GenerateContentConfig(
        max_output_tokens=700,
        thinking_config=thinking_config,
    )


def gerar_relatorio(
    prompt: str,
) -> str:
    modelo = os.getenv(
        "GEMINI_MODEL",
        "gemini-3.6-flash",
    )

    cliente = _obter_cliente()

    response = cliente.models.generate_content(
        model=modelo,
        contents=prompt,
        config=_configuracao_modelo(
            modelo
        ),
    )

    texto = (
        response.text or ""
    ).strip()

    if not texto:
        raise RuntimeError(
            "A IA retornou uma resposta vazia."
        )

    return texto
