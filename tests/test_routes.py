import main


def _indicadores_validos():
    return {
        "preco": 40.25,
        "variacao_dia": 0.012,
        "ema9": 39.80,
        "ema21": 38.90,
        "sma50": 37.50,
        "rsi14": 58.20,
        "macd": 0.65,
        "macd_sinal": 0.45,
        "macd_histograma": 0.20,
        "volatilidade20": 0.28,
        "suporte20": 36.90,
        "resistencia20": 41.40,
        "volume": 12_000_000,
        "volume_medio20": 10_000_000,
        "tendencia_curta": "alta",
        "macd_status": "positivo",
    }


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "ok",
    }


def test_pagina_inicial(client):
    response = client.get("/")

    assert response.status_code == 200

    conteudo = response.get_data(
        as_text=True
    )

    assert "Analisador de Mercado" in conteudo
    assert 'name="ticker"' in conteudo


def test_rejeita_ticker_invalido(client):
    response = client.post(
        "/gerar_relatorio",
        data={
            "ticker": "@@@",
        },
    )

    assert response.status_code == 400
    assert "Ticker inválido" in response.get_data(
        as_text=True
    )


def test_erro_na_consulta_de_mercado(
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        main,
        "buscar_dados_ativo",
        lambda ticker: (
            None,
            "Falha simulada na consulta.",
        ),
    )

    response = client.post(
        "/gerar_relatorio",
        data={
            "ticker": "PETR4",
        },
    )

    assert response.status_code == 502
    assert "Falha simulada" in response.get_data(
        as_text=True
    )


def test_relatorio_com_sucesso(
    client,
    monkeypatch,
):
    chamadas = {
        "ticker": None,
        "telegram": [],
    }

    def buscar_dados(ticker):
        chamadas["ticker"] = ticker

        return {
            "historico": object(),
        }, None

    monkeypatch.setattr(
        main,
        "buscar_dados_ativo",
        buscar_dados,
    )

    monkeypatch.setattr(
        main,
        "calcular_indicadores",
        lambda historico: _indicadores_validos(),
    )

    monkeypatch.setattr(
        main,
        "gerar_relatorio_ia",
        lambda prompt: (
            "## Resumo técnico\n\n"
            "Tendência de alta.\n\n"
            "## SINALIZAÇÃO FINAL: COMPRA\n\n"
            "Justificativa: médias alinhadas."
        ),
    )

    monkeypatch.setattr(
        main,
        "enviar_para_telegram",
        lambda ticker, sinal: chamadas[
            "telegram"
        ].append(
            (ticker, sinal)
        ),
    )

    response = client.post(
        "/gerar_relatorio",
        data={
            "ticker": "petr4",
        },
    )

    conteudo = response.get_data(
        as_text=True
    )

    assert response.status_code == 200
    assert "Resumo técnico" in conteudo
    assert "COMPRA" in conteudo

    assert chamadas["ticker"] == "PETR4.SA"

    assert chamadas["telegram"] == [
        ("PETR4", "COMPRA"),
    ]
