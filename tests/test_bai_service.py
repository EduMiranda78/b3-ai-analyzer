import pytest

from services import bai_service


class RespostaFake:
    status_code = 200

    def json(self):
        return {
            "choices": [
                {
                    "message": {
                        "content": "Relatório B.AI simulado."
                    }
                }
            ]
        }


def test_bai_gera_relatorio_sem_rede(
    monkeypatch,
):
    monkeypatch.setenv(
        "BAI_ENABLED",
        "1",
    )
    monkeypatch.setenv(
        "BAI_API_KEY",
        "chave-de-teste",
    )

    chamadas = {}

    def post_fake(
        url,
        headers,
        json,
        timeout,
    ):
        chamadas["url"] = url
        chamadas["headers"] = headers
        chamadas["json"] = json
        chamadas["timeout"] = timeout

        return RespostaFake()

    monkeypatch.setattr(
        bai_service.requests,
        "post",
        post_fake,
    )

    texto = bai_service.gerar_relatorio(
        "Prompt de teste."
    )

    assert texto == "Relatório B.AI simulado."
    assert chamadas["url"].endswith(
        "/chat/completions"
    )
    assert (
        chamadas["json"]["model"]
        == "deepseek-v4-flash"
    )
    assert (
        chamadas["headers"]["Authorization"]
        == "Bearer chave-de-teste"
    )


def test_bai_desativada_nao_chama_api(
    monkeypatch,
):
    monkeypatch.setenv(
        "BAI_ENABLED",
        "0",
    )

    with pytest.raises(
        RuntimeError,
        match="desativada",
    ):
        bai_service.gerar_relatorio(
            "Prompt."
        )
