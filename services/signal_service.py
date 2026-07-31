import math


def _numero(valor, padrao=0.0):
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return float(padrao)

    if not math.isfinite(numero):
        return float(padrao)

    return numero


def _plano_operacional(
    sinal: str,
    indicadores: dict,
):
    preco = _numero(
        indicadores.get("preco")
    )

    atr = max(
        _numero(
            indicadores.get("atr14")
        ),
        preco * 0.01,
    )

    suporte = _numero(
        indicadores.get("suporte20")
    )

    resistencia = _numero(
        indicadores.get("resistencia20")
    )

    if preco <= 0 or sinal == "NEUTRO":
        return None, None, None, None

    if sinal == "COMPRA":
        stop_atr = preco - (2 * atr)

        stop = (
            max(suporte, stop_atr)
            if 0 < suporte < preco
            else stop_atr
        )

        if stop >= preco:
            stop = preco - max(
                atr,
                preco * 0.01,
            )

        risco = preco - stop
        alvo_minimo = preco + (2 * risco)

        alvo = (
            max(resistencia, alvo_minimo)
            if resistencia > preco
            else alvo_minimo
        )

        retorno = alvo - preco

    else:
        stop_atr = preco + (2 * atr)

        stop = (
            min(resistencia, stop_atr)
            if resistencia > preco
            else stop_atr
        )

        if stop <= preco:
            stop = preco + max(
                atr,
                preco * 0.01,
            )

        risco = stop - preco
        alvo_maximo = preco - (2 * risco)

        alvo = (
            min(suporte, alvo_maximo)
            if 0 < suporte < preco
            else alvo_maximo
        )

        retorno = preco - alvo

    if risco <= 0 or retorno <= 0:
        return (
            round(preco, 2),
            None,
            None,
            None,
        )

    return (
        round(preco, 2),
        round(stop, 2),
        round(alvo, 2),
        round(retorno / risco, 2),
    )


def calcular_sinal_tecnico(
    indicadores: dict,
) -> dict:
    preco = _numero(
        indicadores.get("preco")
    )

    ema9 = _numero(
        indicadores.get("ema9")
    )

    ema21 = _numero(
        indicadores.get("ema21")
    )

    sma50 = _numero(
        indicadores.get("sma50")
    )

    sma200 = _numero(
        indicadores.get("sma200")
    )

    rsi = _numero(
        indicadores.get("rsi14"),
        50.0,
    )

    macd_histograma = _numero(
        indicadores.get("macd_histograma")
    )

    volume_ratio = _numero(
        indicadores.get("volume_ratio"),
        1.0,
    )

    retorno20 = _numero(
        indicadores.get("retorno20")
    )

    volatilidade = _numero(
        indicadores.get("volatilidade20")
    )

    pontos = 0
    motivos = []
    alertas = []

    if ema9 > ema21:
        pontos += 1
        motivos.append(
            "EMA 9 acima da EMA 21, indicando força no curto prazo."
        )

    elif ema9 < ema21:
        pontos -= 1
        motivos.append(
            "EMA 9 abaixo da EMA 21, indicando fraqueza no curto prazo."
        )

    if sma50 > 0:
        if preco > sma50:
            pontos += 1
            motivos.append(
                "Preço acima da média móvel de 50 pregões."
            )

        elif preco < sma50:
            pontos -= 1
            motivos.append(
                "Preço abaixo da média móvel de 50 pregões."
            )

    if sma50 > 0 and sma200 > 0:
        if sma50 > sma200:
            pontos += 1
            motivos.append(
                "SMA 50 acima da SMA 200, confirmando tendência estrutural de alta."
            )

        elif sma50 < sma200:
            pontos -= 1
            motivos.append(
                "SMA 50 abaixo da SMA 200, confirmando tendência estrutural de baixa."
            )

    if 52 <= rsi <= 70:
        pontos += 1
        motivos.append(
            "RSI em zona favorável à continuidade compradora."
        )

    elif 30 <= rsi <= 48:
        pontos -= 1
        motivos.append(
            "RSI em zona favorável à continuidade vendedora."
        )

    elif rsi > 70:
        alertas.append(
            "RSI acima de 70: ativo pode estar sobrecomprado."
        )

    elif rsi < 30:
        alertas.append(
            "RSI abaixo de 30: ativo pode estar sobrevendido."
        )

    if macd_histograma > 0:
        pontos += 1
        motivos.append(
            "Histograma do MACD positivo."
        )

    elif macd_histograma < 0:
        pontos -= 1
        motivos.append(
            "Histograma do MACD negativo."
        )

    if volume_ratio >= 1.20:
        if retorno20 > 0:
            pontos += 1
            motivos.append(
                "Volume acima da média confirma o movimento de alta."
            )

        elif retorno20 < 0:
            pontos -= 1
            motivos.append(
                "Volume acima da média confirma o movimento de baixa."
            )

    elif volume_ratio < 0.70:
        alertas.append(
            "Volume abaixo da média reduz a confiabilidade do movimento."
        )

    if retorno20 >= 0.03:
        pontos += 1
        motivos.append(
            "Retorno positivo nos últimos 20 pregões."
        )

    elif retorno20 <= -0.03:
        pontos -= 1
        motivos.append(
            "Retorno negativo nos últimos 20 pregões."
        )

    if volatilidade >= 0.60:
        alertas.append(
            "Volatilidade anualizada elevada; risco operacional ampliado."
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

    (
        preco_referencia,
        stop,
        alvo,
        risco_retorno,
    ) = _plano_operacional(
        sinal,
        indicadores,
    )

    if sinal == "NEUTRO":
        motivos.append(
            "A pontuação não atingiu o mínimo necessário para um sinal direcional."
        )

    return {
        "sinal": sinal,
        "pontos": pontos,
        "confianca": confianca,
        "preco_referencia": preco_referencia,
        "stop": stop,
        "alvo": alvo,
        "risco_retorno": risco_retorno,
        "motivos": motivos,
        "alertas": alertas,
    }
