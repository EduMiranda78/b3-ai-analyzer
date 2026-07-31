from services.signal_service import (
    calcular_sinal_tecnico,
)


def indicadores_base():
    return {
        "preco": 100.0,
        "ema9": 100.0,
        "ema21": 100.0,
        "sma50": 100.0,
        "sma200": 100.0,
        "rsi14": 50.0,
        "macd_histograma": 0.0,
        "volume_ratio": 1.0,
        "retorno20": 0.0,
        "suporte20": 90.0,
        "resistencia20": 110.0,
        "atr14": 3.0,
        "distancia_suporte": 0.10,
        "distancia_resistencia": 0.10,
    }


def test_sinal_de_compra():
    dados = indicadores_base()

    dados.update(
        {
            "preco": 110.0,
            "ema9": 108.0,
            "ema21": 105.0,
            "sma50": 100.0,
            "sma200": 92.0,
            "rsi14": 61.0,
            "macd_histograma": 0.8,
            "volume_ratio": 1.40,
            "retorno20": 0.08,
            "suporte20": 102.0,
            "resistencia20": 125.0,
            "atr14": 3.0,
        }
    )

    resultado = calcular_sinal_tecnico(
        dados
    )

    assert resultado["sinal"] == "COMPRA"
    assert resultado["pontos"] >= 4
    assert resultado["stop"] < 110.0
    assert resultado["alvo"] > 110.0

    assert (
        resultado["risco_retorno"]
        >= 2
    )


def test_sinal_de_venda():
    dados = indicadores_base()

    dados.update(
        {
            "preco": 90.0,
            "ema9": 92.0,
            "ema21": 95.0,
            "sma50": 100.0,
            "sma200": 108.0,
            "rsi14": 39.0,
            "macd_histograma": -0.8,
            "volume_ratio": 1.40,
            "retorno20": -0.08,
            "suporte20": 75.0,
            "resistencia20": 98.0,
            "atr14": 3.0,
        }
    )

    resultado = calcular_sinal_tecnico(
        dados
    )

    assert resultado["sinal"] == "VENDA"
    assert resultado["pontos"] <= -4
    assert resultado["stop"] > 90.0
    assert resultado["alvo"] < 90.0

    assert (
        resultado["risco_retorno"]
        >= 2
    )


def test_sinal_neutro():
    dados = indicadores_base()

    resultado = calcular_sinal_tecnico(
        dados
    )

    assert resultado["sinal"] == "NEUTRO"

    assert (
        resultado["preco_referencia"]
        is None
    )

    assert resultado["stop"] is None
    assert resultado["alvo"] is None
