from typing import Optional


MIN_RISCO_RETORNO = 2.0


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

    # Para compra, escolhe o stop mais próximo entre
    # a estrutura e o limite de 2 ATR. Isso impede que
    # o risco seja ampliado artificialmente.
    stop = max(
        stop_limite,
        stop_estrutural,
    )

    risco = preco - stop

    if risco <= 0:
        return (
            None,
            None,
            None,
            False,
        )

    alvo_projetado = not (
        resistencia > preco
    )

    if alvo_projetado:
        alvo = (
            preco
            + MIN_RISCO_RETORNO
            * risco
        )
    else:
        # Quando existe resistência objetiva, ela é
        # preservada como alvo. O motor não "empurra"
        # o alvo para além dela só para exibir 2R.
        alvo = resistencia

    retorno = alvo - preco
    risco_retorno = (
        retorno / risco
    )

    if (
        not alvo_projetado
        and risco_retorno
        < MIN_RISCO_RETORNO
    ):
        alertas.append(
            "A resistência está antes de 2R. "
            "O alvo estrutural foi preservado; "
            "o setup não deve ser tratado como "
            "operação 2:1."
        )

    if alvo_projetado:
        alertas.append(
            "Não há resistência de 20 pregões "
            "acima do preço. O alvo é uma "
            "projeção de 2R, não um nível "
            "estrutural confirmado."
        )

    return (
        stop,
        alvo,
        risco_retorno,
        alvo_projetado,
    )


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
        return (
            None,
            None,
            None,
            False,
        )

    alvo_projetado = not (
        0 < suporte < preco
    )

    if alvo_projetado:
        alvo = max(
            (
                preco
                - MIN_RISCO_RETORNO
                * risco
            ),
            0.01,
        )
    else:
        alvo = suporte

    retorno = preco - alvo
    risco_retorno = (
        retorno / risco
    )

    if (
        not alvo_projetado
        and risco_retorno
        < MIN_RISCO_RETORNO
    ):
        alertas.append(
            "O suporte está antes de 2R. "
            "O alvo estrutural foi preservado; "
            "o setup não deve ser tratado como "
            "operação 2:1."
        )

    if alvo_projetado:
        alertas.append(
            "Não há suporte de 20 pregões "
            "abaixo do preço. O alvo é uma "
            "projeção de 2R, não um nível "
            "estrutural confirmado."
        )

    return (
        stop,
        alvo,
        risco_retorno,
        alvo_projetado,
    )


def _qualidade_plano(
    risco_retorno: Optional[float],
) -> str:
    if risco_retorno is None:
        return "NÃO APLICÁVEL"

    if (
        risco_retorno
        >= MIN_RISCO_RETORNO
    ):
        return "APROVADO"

    if risco_retorno >= 1.5:
        return "ATENÇÃO"

    return "FRACO"


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

    sma200_disponivel = bool(
        indicadores.get(
            "sma200_disponivel",
            sma200 > 0,
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

    atr_percentual = float(
        indicadores.get(
            "atr_percentual",
            (
                atr / preco
                if preco > 0
                else 0
            ),
        )
    )

    rompimento20 = (
        indicadores.get(
            "rompimento20",
            "nenhum",
        )
    )

    clv = float(
        indicadores.get(
            "clv",
            0,
        )
    )

    range_atr = float(
        indicadores.get(
            "range_atr",
            0,
        )
    )

    pontos = 0
    motivos = []
    alertas = []

    # 1) Estrutura curta.
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

    # 2) Tendência intermediária.
    tolerancia_preco = (
        max(preco, 1.0) * 1e-6
    )

    if preco > (
        sma50 + tolerancia_preco
    ):
        pontos += 1

        motivos.append(
            "Preço acima da SMA 50."
        )

    elif preco < (
        sma50 - tolerancia_preco
    ):
        pontos -= 1

        motivos.append(
            "Preço abaixo da SMA 50."
        )

    else:
        motivos.append(
            "Preço praticamente sobre a SMA 50."
        )

    # 3) Tendência longa, apenas quando há
    # histórico suficiente para uma SMA 200 real.
    if (
        sma200_disponivel
        and sma200 > 0
    ):
        if preco > sma200:
            pontos += 1

            motivos.append(
                "Preço acima da SMA 200."
            )

        elif preco < sma200:
            pontos -= 1

            motivos.append(
                "Preço abaixo da SMA 200."
            )
    else:
        alertas.append(
            "SMA 200 indisponível: histórico "
            "ainda insuficiente para confirmar "
            "a tendência de longo prazo."
        )

    # 4) Momentum pelo MACD. Zero é neutro.
    tolerancia_macd = (
        max(
            abs(preco),
            1.0,
        )
        * 1e-10
    )

    if (
        macd_histograma
        > tolerancia_macd
    ):
        pontos += 1

        motivos.append(
            "Histograma do MACD positivo."
        )

    elif (
        macd_histograma
        < -tolerancia_macd
    ):
        pontos -= 1

        motivos.append(
            "Histograma do MACD negativo."
        )

    else:
        motivos.append(
            "Histograma do MACD neutro."
        )

    # 5) RSI é usado como confirmação, não como
    # gatilho isolado.
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

    # 6) Persistência de preço.
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

    # 7) Volume confirma a direção já formada.
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
            "da média dos 20 pregões anteriores."
        )

    # 8) Contexto de price action: um rompimento só
    # ganha ponto quando a barra fecha na direção do
    # movimento e tem tamanho minimamente relevante.
    if rompimento20 == "alta":
        if (
            clv >= 0.50
            and range_atr >= 0.80
        ):
            pontos += 1

            motivos.append(
                "Rompimento da máxima de 20 pregões "
                "com fechamento forte na barra."
            )
        else:
            alertas.append(
                "Houve rompimento de alta, mas a "
                "barra não fechou com força suficiente."
            )

    elif rompimento20 == "baixa":
        if (
            clv <= -0.50
            and range_atr >= 0.80
        ):
            pontos -= 1

            motivos.append(
                "Rompimento da mínima de 20 pregões "
                "com fechamento forte na barra."
            )
        else:
            alertas.append(
                "Houve rompimento de baixa, mas a "
                "barra não fechou com força suficiente."
            )

    if atr_percentual >= 0.06:
        alertas.append(
            "ATR acima de 6% do preço: "
            "volatilidade técnica elevada."
        )

    valor_financeiro_medio = float(
        indicadores.get(
            "valor_financeiro_medio20",
            0,
        )
    )

    if 0 < valor_financeiro_medio < 1_000_000:
        alertas.append(
            "Liquidez financeira muito baixa nos últimos 20 pregões. "
            "Entradas e saídas podem ocorrer com maior diferença de preço."
        )
    elif 0 < valor_financeiro_medio < 5_000_000:
        alertas.append(
            "Liquidez financeira reduzida nos últimos 20 pregões. "
            "Considere esse risco antes de interpretar o sinal."
        )

    # Máximo teórico: 9 pontos com SMA 200;
    # 8 quando ela ainda não existe.
    score_maximo = (
        9
        if sma200_disponivel
        else 8
    )

    forca_percentual = (
        abs(pontos)
        / score_maximo
        if score_maximo > 0
        else 0.0
    )

    if pontos >= 4:
        sinal = "COMPRA"

    elif pontos <= -4:
        sinal = "VENDA"

    else:
        sinal = "NEUTRO"

    # "Confiança" aqui significa força/confluência
    # técnica, não probabilidade estatística de acerto.
    if (
        sinal != "NEUTRO"
        and forca_percentual >= 0.67
    ):
        confianca = "ALTA"

    elif (
        sinal != "NEUTRO"
        and forca_percentual >= 0.45
    ):
        confianca = "MÉDIA"

    else:
        confianca = "BAIXA"

    preco_referencia = None
    stop = None
    alvo = None
    risco_retorno = None
    alvo_projetado = False

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
                alvo_projetado,
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
                alvo_projetado,
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

    qualidade_plano = (
        _qualidade_plano(
            risco_retorno
        )
    )

    setup_aprovado = (
        sinal != "NEUTRO"
        and risco_retorno is not None
        and risco_retorno
        >= MIN_RISCO_RETORNO
    )

    if (
        sinal != "NEUTRO"
        and risco_retorno is not None
        and not setup_aprovado
    ):
        alertas.append(
            "O viés direcional existe, mas o "
            "plano não atende ao mínimo de 2R. "
            "Trate o sinal como observação, "
            "não como setup aprovado."
        )

    return {
        "sinal": sinal,
        "pontos": pontos,
        "score_maximo": score_maximo,
        "forca_percentual": _arredondar(
            forca_percentual,
            4,
        ),
        "confianca": confianca,
        "preco_referencia": _arredondar(
            preco_referencia
        ),
        "stop": _arredondar(stop),
        "alvo": _arredondar(alvo),
        "risco_retorno": _arredondar(
            risco_retorno
        ),
        "alvo_projetado": alvo_projetado,
        "setup_aprovado": (
            setup_aprovado
        ),
        "qualidade_plano": (
            qualidade_plano
        ),
        "motivos": motivos,
        "alertas": alertas,
    }
