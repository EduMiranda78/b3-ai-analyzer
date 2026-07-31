import main


def indicadores_validos():
    return {
        "preco": 110.0,
        "variacao_dia": 0.01,
        "ema9": 108.0,
        "ema21": 105.0,
        "sma50": 100.0,
        "sma200": 92.0,
        "rsi14": 61.0,
        "macd": 1.2,
        "macd_sinal": 0.8,
        "macd_histograma": 0.4,
        "atr14": 3.0,
        "volatilidade20": 0.25,
        "suporte20": 102.0,
        "resistencia20": 125.0,
        "volume": 1_400_000.0,
        "volume_medio20": 1_000_000.0,
        "volume_ratio": 1.4,
        "retorno20": 0.08,
        "retorno60": 0.15,
        "distancia_suporte": 0.07,
        "distancia_resistencia": 0.14,
        "tendencia_curta": "alta",
        "macd_status": "positivo",
    }


def analise_compra():
    return {
        "sinal": "COMPRA",
        "pontos": 7,
        "confianca": "ALTA",
        "preco_referencia": 110.0,
        "stop": 104.0,
        "alvo": 125.0,
        "risco_retorno": 2.5,
        "motivos": [
            "Preço acima das médias.",
            "MACD positivo.",
        ],
        "alertas": [],
    }


def preparar_dependencias(
    monkeypatch,
):
    monkeypatch.setattr(
        main,
        "buscar_dados_ativo",
        lambda ticker: (
            {
                "historico": object(),
            },
            None,
        ),
    )

    monkeypatch.setattr(
        main,
        "calcular_indicadores",
        lambda historico: (
            indicadores_validos()
        ),
    )

    monkeypatch.setattr(
        main,
        "calcular_sinal_tecnico",
        lambda indicadores: (
            analise_compra()
        ),
    )

    monkeypatch.setattr(
        main,
        "salvar_analise",
        lambda **kwargs: 1,
    )

    monkeypatch.setattr(
        main,
        "enviar_para_telegram",
        lambda ticker, sinal: True,
    )


def test_health(client):
    resposta = client.get(
        "/health"
    )

    assert resposta.status_code == 200

    dados = resposta.get_json()

    assert dados["status"] == "ok"
    assert dados["motor_sinal"] == "ativo"


def test_pagina_inicial(client):
    resposta = client.get("/")

    assert resposta.status_code == 200

    html = resposta.get_data(
        as_text=True
    )

    assert "Analisador de Mercado" in html
    assert 'name="ticker"' in html


def test_rejeita_ticker_invalido(
    client,
):
    resposta = client.post(
        "/gerar_relatorio",
        data={
            "ticker": "@@@",
        },
    )

    assert resposta.status_code == 400

    assert "Ticker inválido" in (
        resposta.get_data(
            as_text=True
        )
    )


def test_erro_de_mercado(
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        main,
        "buscar_dados_ativo",
        lambda ticker: (
            None,
            "Falha simulada.",
        ),
    )

    resposta = client.post(
        "/gerar_relatorio",
        data={
            "ticker": "PETR4",
        },
    )

    assert resposta.status_code == 502
    assert "Falha simulada" in (
        resposta.get_data(
            as_text=True
        )
    )


def test_relatorio_com_gemini(
    client,
    monkeypatch,
):
    preparar_dependencias(
        monkeypatch
    )

    monkeypatch.setattr(
        main,
        "gerar_relatorio_ia",
        lambda prompt: (
            "## Leitura técnica\n\n"
            "Tendência compradora.\n\n"
            "## SINALIZAÇÃO FINAL: COMPRA\n\n"
            "Justificativa: médias positivas."
        ),
    )

    resposta = client.post(
        "/gerar_relatorio",
        data={
            "ticker": "PETR4",
        },
    )

    html = resposta.get_data(
        as_text=True
    )

    assert resposta.status_code == 200
    assert "PETR4" in html
    assert "COMPRA" in html

    assert (
        "motor técnico local"
        not in html
    )


def test_relatorio_local_quando_gemini_falha(
    client,
    monkeypatch,
):
    preparar_dependencias(
        monkeypatch
    )

    def falhar(prompt):
        raise ConnectionError(
            "Falha simulada no Gemini."
        )

    monkeypatch.setattr(
        main,
        "gerar_relatorio_ia",
        falhar,
    )

    resposta = client.post(
        "/gerar_relatorio",
        data={
            "ticker": "PETR4",
        },
    )

    html = resposta.get_data(
        as_text=True
    )

    assert resposta.status_code == 200
    assert "PETR4" in html
    assert "COMPRA" in html
    assert "motor técnico local" in html
    assert "Plano técnico" in html
