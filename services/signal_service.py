from typing import Optional


def _arredondar(
    valor: Optional[float],
    casas: int = 2,
):
    if valor is None:
        return None

    return round(
        float(valor),
        casas,
    )


def _plano_compra(
    preco: float,
    suporte: float,
    resistencia: float,
    atr: float,
    alertas: list[str],
):
    stop_limite = (
        preco - (2 * atr)
    )

    stop_estrutural = (
        suporte - (0.25 * atr)
        if 0 < suporte < preco
        else stop_limite
    )

    stop = max(
        stop_limite,
        stop_estrutural,
    )

    risco = preco - stop

    if risco <= 0:
        return None, None, None

    alvo = (
        resistencia
        if resistencia > preco
        else preco + (2 * risco)
    )

    retorno = alvo - preco
    risco_retorno = retorno / risco

    if risco_retorno < 2:
        alvo = preco + (2 * risco)
        risco_retorno = 2.0

        alertas.append(
            "A resistência atual não oferece "
            "relação risco-retorno de 2 para 1. "
            "O alvo exibido é uma projeção."
        )

    return stop, alvo, risco_retorno


def _plano_venda(
    preco: float,
    suporte: float,
    resistencia: float,
    atr: float,
    alertas: list[str],
):
    stop_limite = (
        preco + (2 * atr)
    )

    stop_estrutural = (
        resistencia + (0.25 * atr)
        if resistencia > preco
        else stop_limite
    )

    stop = min(
        stop_limite,
        stop_estrutural,
    )

    risco = stop - preco

    if risco <= 0:
        return None, None, None

    alvo = (
        suporte
        if 0 < suporte < preco
        else preco - (2 * risco)
    )

    alvo = max(
        alvo,
        0.01,
    )

    retorno = preco - alvo
    risco_retorno = retorno / risco

    if risco_retorno < 2:
        alvo = max(
            preco - (2 * risco),
            0.01,
        )

        risco_retorno = 2.0

        alertas.append(
            "O suporte atual não oferece "
            "relação risco-retorno de 2 para 1. "
            "O alvo exibido é uma projeção."
        )

    return stop, alvo, risco_retorno


def calcular_sinal_tecnico(
    indicadores: dict,
) -> dict:
    preco = float(
        indicadores["preco"]
    )

    ema9 = float(
        indicadores["ema9"]
    )

    ema21 = float(
        indicadores["ema21"]
    )

    sma50 = float(
        indicadores["sma50"]
    )

    sma200 = float(
        indicadores.get(
            "sma200",
            0,
        )
    )

    rsi = float(
        indicadores["rsi14"]
    )

    macd_histograma = float(
        indicadores[
            "macd_histograma"
        ]
    )

    volume_ratio = float(
        indicadores.get(
            "volume_ratio",
            0,
        )
    )

    retorno20 = float(
        indicadores.get(
            "retorno20",
            0,
        )
    )

    suporte = float(
        indicadores["suporte20"]
    )

    resistencia = float(
        indicadores[
            "resistencia20"
        ]
    )

    atr = float(
        indicadores.get(
            "atr14",
            0,
        )
    )

    pontos = 0
    motivos = []
    alertas = []

    if preco > ema9 > ema21:
        pontos += 2

        motivos.append(
            "Preço acima das EMA 9 e 21, "
            "com alinhamento de alta."
        )

    elif preco < ema9 < ema21:
        pontos -= 2

        motivos.append(
            "Preço abaixo das EMA 9 e 21, "
            "com alinhamento de baixa."
        )

    else:
        motivos.append(
            "Médias curtas sem alinhamento "
            "direcional claro."
        )

    if preco > sma50:
        pontos += 1

        motivos.append(
            "Preço acima da SMA 50."
        )

    else:
        pontos -= 1

        motivos.append(
            "Preço abaixo da SMA 50."
        )

    if sma200 > 0:
        if preco > sma200:
            pontos += 1

            motivos.append(
                "Preço acima da SMA 200."
            )

        else:
            pontos -= 1

            motivos.append(
                "Preço abaixo da SMA 200."
            )

    if macd_histograma > 0:
        pontos += 1

        motivos.append(
            "Histograma do MACD positivo."
        )

    else:
        pontos -= 1

        motivos.append(
            "Histograma do MACD negativo."
        )

    if 55 <= rsi <= 70:
        pontos += 1

        motivos.append(
            "RSI confirma momento comprador "
            "sem sobrecompra extrema."
        )

    elif 30 <= rsi <= 45:
        pontos -= 1

        motivos.append(
            "RSI confirma fraqueza compradora."
        )

    elif rsi > 70:
        alertas.append(
            "RSI em região de sobrecompra."
        )

    elif rsi < 30:
        alertas.append(
            "RSI em região de sobrevenda."
        )

    if retorno20 >= 0.03:
        pontos += 1

        motivos.append(
            "Retorno de 20 pregões positivo."
        )

    elif retorno20 <= -0.03:
        pontos -= 1

        motivos.append(
            "Retorno de 20 pregões negativo."
        )

    if volume_ratio >= 1.20:
        if pontos > 0:
            pontos += 1

            motivos.append(
                "Volume acima da média confirma "
                "o movimento comprador."
            )

        elif pontos < 0:
            pontos -= 1

            motivos.append(
                "Volume acima da média confirma "
                "o movimento vendedor."
            )

    elif 0 < volume_ratio < 0.70:
        alertas.append(
            "Movimento com volume abaixo "
            "da média de 20 pregões."
        )

    if pontos >= 4:
        sinal = "COMPRA"

    elif pontos <= -4:
        sinal = "VENDA"

    else:
        sinal = "NEUTRO"

    intensidade = abs(pontos)

    if intensidade >= 6:
        confianca = "ALTA"

    elif intensidade >= 4:
        confianca = "MÉDIA"

    else:
        confianca = "BAIXA"

    preco_referencia = None
    stop = None
    alvo = None
    risco_retorno = None

    if sinal != "NEUTRO":
        preco_referencia = preco

        if atr <= 0:
            alertas.append(
                "ATR indisponível. Não foi "
                "possível calcular stop e alvo."
            )

        elif sinal == "COMPRA":
            (
                stop,
                alvo,
                risco_retorno,
            ) = _plano_compra(
                preco,
                suporte,
                resistencia,
                atr,
                alertas,
            )

        else:
            (
                stop,
                alvo,
                risco_retorno,
            ) = _plano_venda(
                preco,
                suporte,
                resistencia,
                atr,
                alertas,
            )

    distancia_suporte = float(
        indicadores.get(
            "distancia_suporte",
            0,
        )
    )

    distancia_resistencia = float(
        indicadores.get(
            "distancia_resistencia",
            0,
        )
    )

    if (
        sinal == "COMPRA"
        and 0
        < distancia_resistencia
        < 0.02
    ):
        alertas.append(
            "Preço a menos de 2% da resistência."
        )

    if (
        sinal == "VENDA"
        and 0
        < distancia_suporte
        < 0.02
    ):
        alertas.append(
            "Preço a menos de 2% do suporte."
        )

    return {
        "sinal": sinal,
        "pontos": pontos,
        "confianca": confianca,
        "preco_referencia": _arredondar(
            preco_referencia
        ),
        "stop": _arredondar(stop),
        "alvo": _arredondar(alvo),
        "risco_retorno": _arredondar(
            risco_retorno
        ),
        "motivos": motivos,
        "alertas": alertas,
    }
