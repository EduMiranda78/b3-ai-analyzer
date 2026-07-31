def _moeda(valor):
    if valor is None:
        return "Não aplicável"

    return f"R$ {float(valor):.2f}"


def _percentual(valor):
    if valor is None:
        return "Não disponível"

    return f"{float(valor):.2%}"


def gerar_relatorio_local(
    ticker: str,
    indicadores: dict,
    analise: dict,
) -> str:
    sinal = analise["sinal"]
    confianca = analise["confianca"]
    pontos = analise["pontos"]

    motivos = analise.get(
        "motivos",
        [],
    )

    alertas = analise.get(
        "alertas",
        [],
    )

    motivos_texto = "\n".join(
        f"- {motivo}"
        for motivo in motivos[:5]
    )

    if not motivos_texto:
        motivos_texto = (
            "- Não houve confirmação "
            "direcional suficiente."
        )

    alertas_texto = "\n".join(
        f"- {alerta}"
        for alerta in alertas[:3]
    )

    if not alertas_texto:
        alertas_texto = (
            "- Nenhum alerta técnico adicional."
        )

    if sinal == "COMPRA":
        leitura = (
            "O conjunto de indicadores apresenta "
            "predominância compradora."
        )

    elif sinal == "VENDA":
        leitura = (
            "O conjunto de indicadores apresenta "
            "predominância vendedora."
        )

    else:
        leitura = (
            "Os indicadores estão conflitantes ou "
            "não atingiram pontuação suficiente para "
            "uma direção clara."
        )

    if sinal == "NEUTRO":
        plano = (
            "Como o sinal está neutro, o sistema não "
            "definiu preço de referência, stop ou alvo. "
            "Uma nova confirmação técnica deve ocorrer "
            "antes de considerar uma operação."
        )

    else:
        plano = (
            f"Preço de referência: "
            f"{_moeda(analise.get('preco_referencia'))}. "
            f"Stop técnico: "
            f"{_moeda(analise.get('stop'))}. "
            f"Alvo técnico: "
            f"{_moeda(analise.get('alvo'))}. "
            f"Relação risco-retorno: "
            f"1 para "
            f"{float(analise.get('risco_retorno') or 0):.2f}."
        )

    justificativa = (
        motivos[0]
        if motivos
        else "Indicadores sem confirmação suficiente."
    )

    return f"""## Leitura técnica

{leitura}

O ativo {ticker} recebeu pontuação {pontos}, com confiança {confianca}. O preço está em {_moeda(indicadores.get('preco'))}, com variação diária de {_percentual(indicadores.get('variacao_dia'))}. O RSI está em {float(indicadores.get('rsi14', 0)):.2f} e o volume representa {float(indicadores.get('volume_ratio', 0)):.2f} vez a média dos últimos 20 pregões.

## Níveis e risco

Suporte técnico: {_moeda(indicadores.get('suporte20'))}.

Resistência técnica: {_moeda(indicadores.get('resistencia20'))}.

{plano}

## Pontos de atenção

{alertas_texto}

## Motivos considerados

{motivos_texto}

## SINALIZAÇÃO FINAL: {sinal}

Justificativa: {justificativa}
"""
