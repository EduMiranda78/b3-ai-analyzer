def _moeda(valor):
    if valor is None:
        return "Não aplicável"
    return f"R$ {float(valor):.2f}"


def _percentual(valor):
    if valor is None:
        return "Não disponível"
    return f"{float(valor):.2%}"


def construir_resumo_leigo(indicadores: dict, analise: dict) -> dict:
    sinal = analise["sinal"]
    aprovado = bool(analise.get("setup_aprovado"))
    rr = analise.get("risco_retorno")

    if sinal == "COMPRA":
        titulo = "Cenário favorável"
        explicacao = (
            "Os sinais técnicos estão mais favoráveis à alta do que à queda."
        )
        if aprovado:
            conduta = (
                "O plano técnico também apresenta relação entre risco e retorno "
                "compatível com o critério mínimo do sistema."
            )
        else:
            conduta = (
                "Apesar do viés positivo, o risco e o retorno não formam um "
                "plano suficientemente bom. Melhor tratar como observação."
            )

    elif sinal == "VENDA":
        titulo = "Cenário desfavorável"
        explicacao = (
            "Os sinais técnicos apontam mais fraqueza do que força no ativo."
        )
        if aprovado:
            conduta = (
                "Para quem já possui o ativo, o cenário pede atenção ao risco. "
                "VENDA aqui é um viés técnico, não uma ordem de venda a descoberto."
            )
        else:
            conduta = (
                "Há fraqueza técnica, mas o plano não atende ao critério mínimo "
                "de risco e retorno. Evite interpretar o sinal como ordem automática."
            )

    else:
        titulo = "Sem direção clara"
        explicacao = (
            "Os indicadores estão misturados e ainda não confirmam uma direção confiável."
        )
        conduta = (
            "O mais prudente é aguardar nova confirmação antes de usar esta leitura "
            "como base para uma decisão."
        )

    if rr is None:
        rr_texto = "não aplicável"
    else:
        rr_texto = f"1 para {float(rr):.2f}"

    return {
        "titulo": titulo,
        "explicacao": explicacao,
        "conduta": conduta,
        "sinal": sinal,
        "forca": analise.get("confianca", "BAIXA"),
        "preco": _moeda(indicadores.get("preco")),
        "risco_retorno": rr_texto,
        "plano": analise.get("qualidade_plano", "NÃO APLICÁVEL"),
    }


def gerar_relatorio_local(
    ticker: str,
    indicadores: dict,
    analise: dict,
) -> str:
    resumo = construir_resumo_leigo(indicadores, analise)
    sinal = analise["sinal"]
    motivos = analise.get("motivos", [])
    alertas = analise.get("alertas", [])

    motivos_texto = "\n".join(f"- {motivo}" for motivo in motivos[:4])
    if not motivos_texto:
        motivos_texto = "- Não houve confirmação direcional suficiente."

    alertas_texto = "\n".join(f"- {alerta}" for alerta in alertas[:3])
    if not alertas_texto:
        alertas_texto = "- Nenhum alerta técnico adicional."

    if sinal == "NEUTRO":
        plano = (
            "O sistema não definiu entrada, stop ou alvo porque ainda não há "
            "direção técnica suficiente."
        )
    else:
        plano = (
            f"Referência: {_moeda(analise.get('preco_referencia'))}. "
            f"Stop: {_moeda(analise.get('stop'))}. "
            f"Alvo: {_moeda(analise.get('alvo'))}. "
            f"Risco-retorno: {resumo['risco_retorno']}. "
            f"Plano: {resumo['plano']}."
        )

    return f"""## Em poucas palavras

**{resumo['titulo']}**. {resumo['explicacao']}

{resumo['conduta']}

## Níveis principais

Preço atual: {resumo['preco']}.

Suporte: {_moeda(indicadores.get('suporte20'))}.
Resistência: {_moeda(indicadores.get('resistencia20'))}.

{plano}

## O que sustentou a leitura

{motivos_texto}

## Atenção

{alertas_texto}

## SINALIZAÇÃO FINAL: {sinal}
"""
