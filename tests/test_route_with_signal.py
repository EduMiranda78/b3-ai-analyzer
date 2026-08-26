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


def test_relatorio_exibe_motor_de_sinal(
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
        "gerar_relatorio_ia",
        lambda prompt: (
            "## Leitura técnica\n\n"
            "Movimento comprador.\n\n"
            "## SINALIZAÇÃO FINAL: COMPRA\n\n"
            "Justificativa: tendência positiva."
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
        lambda ticker, sinal, **kwargs: True,
    )

    main.app.config["TESTING"] = True

    with main.app.test_client() as client:
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
    assert "Plano técnico" in html
    assert "1 para" in html


def test_relatorio_calcula_atr_percentual_quando_campo_nao_existe(monkeypatch):
    """O template não pode retornar 500 se um payload legado não trouxer atr_percentual."""
    monkeypatch.setattr(
        main,
        "buscar_dados_ativo",
        lambda ticker: ({"historico": object()}, None),
    )
    monkeypatch.setattr(
        main,
        "calcular_indicadores",
        lambda historico: indicadores_validos(),
    )
    monkeypatch.setattr(
        main,
        "gerar_relatorio_ia",
        lambda prompt: "## SINALIZAÇÃO FINAL: COMPRA",
    )
    monkeypatch.setattr(main, "salvar_analise", lambda **kwargs: 1)
    monkeypatch.setattr(main, "enviar_para_telegram", lambda *args, **kwargs: True)

    main.app.config["TESTING"] = True
    with main.app.test_client() as client:
        resposta = client.post("/gerar_relatorio", data={"ticker": "PETR4"})

    html = resposta.get_data(as_text=True)
    assert resposta.status_code == 200
    assert "ATR/preço" in html
    assert "2.73%" in html
