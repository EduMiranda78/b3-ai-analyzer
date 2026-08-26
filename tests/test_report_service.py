from services.report_service import construir_resumo_leigo


def test_resumo_compra_sem_plano_aprovado_e_prudente():
    resumo = construir_resumo_leigo(
        {"preco": 10.0},
        {
            "sinal": "COMPRA",
            "confianca": "MÉDIA",
            "setup_aprovado": False,
            "risco_retorno": 1.2,
            "qualidade_plano": "FRACO",
        },
    )

    assert resumo["titulo"] == "Cenário favorável"
    assert "observação" in resumo["conduta"]
    assert resumo["plano"] == "FRACO"


def test_resumo_neutro_recomenda_aguardar_confirmacao():
    resumo = construir_resumo_leigo(
        {"preco": 10.0},
        {
            "sinal": "NEUTRO",
            "confianca": "BAIXA",
            "setup_aprovado": False,
            "risco_retorno": None,
            "qualidade_plano": "NÃO APLICÁVEL",
        },
    )

    assert resumo["titulo"] == "Sem direção clara"
    assert "aguardar" in resumo["conduta"]
