import os

from google import genai
from google.genai import types


API_KEY = os.getenv("GOOGLE_API_KEY")

MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash",
)

if not API_KEY:
    raise RuntimeError(
        "GOOGLE_API_KEY não configurada"
    )

client = genai.Client(
    api_key=API_KEY,
)


def gerar_relatorio(prompt: str) -> str:
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=700,
            thinking_config=types.ThinkingConfig(
                thinking_budget=0,
            ),
        ),
    )

    texto = (response.text or "").strip()

    if not texto:
        raise RuntimeError(
            "A IA retornou uma resposta vazia."
        )

    return texto
