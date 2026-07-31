import main


def test_pagina_historico(
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        main,
        "listar_analises",
        lambda ticker, limite: [],
    )

    monkeypatch.setattr(
        main,
        "obter_estatisticas",
        lambda ticker: {
            "total": 0,
            "compras": 0,
            "vendas": 0,
            "neutros": 0,
            "tickers": 0,
        },
    )

    resposta = client.get(
        "/historico"
    )

    assert resposta.status_code == 200

    html = resposta.get_data(
        as_text=True
    )

    assert "Histórico de análises" in html


def test_detalhe_inexistente(
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        main,
        "obter_analise",
        lambda analise_id: None,
    )

    resposta = client.get(
        "/historico/999"
    )

    assert resposta.status_code == 404
