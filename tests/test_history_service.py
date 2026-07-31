from services.history_service import (
    listar_analises,
    obter_analise,
    obter_anterior,
    obter_estatisticas,
    salvar_analise,
)


def dados_teste(
    sinal="COMPRA",
    pontos=6,
    preco=100.0,
):
    indicadores = {
        "preco": preco,
        "rsi14": 60.0,
        "volume_ratio": 1.2,
    }

    analise = {
        "sinal": sinal,
        "pontos": pontos,
        "confianca": "ALTA",
        "preco_referencia": preco,
        "stop": preco - 5,
        "alvo": preco + 10,
        "risco_retorno": 2.0,
        "motivos": [
            "Motivo de teste."
        ],
        "alertas": [],
    }

    return indicadores, analise


def test_salva_lista_e_compara(
    tmp_path,
    monkeypatch,
):
    banco = tmp_path / "historico.db"

    monkeypatch.setenv(
        "ANALISADOR_DB_PATH",
        str(banco),
    )

    indicadores1, analise1 = dados_teste(
        sinal="NEUTRO",
        pontos=1,
        preco=95.0,
    )

    id1 = salvar_analise(
        ticker="PETR4",
        indicadores=indicadores1,
        analise=analise1,
        origem_relatorio="motor local",
        tempo_total=1.2,
        relatorio_markdown="Relatório 1",
    )

    indicadores2, analise2 = dados_teste(
        sinal="COMPRA",
        pontos=6,
        preco=100.0,
    )

    id2 = salvar_analise(
        ticker="PETR4",
        indicadores=indicadores2,
        analise=analise2,
        origem_relatorio="Gemini",
        tempo_total=2.0,
        relatorio_markdown="Relatório 2",
    )

    assert id2 > id1

    itens = listar_analises(
        ticker="PETR4"
    )

    assert len(itens) == 2
    assert itens[0]["id"] == id2
    assert itens[0]["signal"] == "COMPRA"

    detalhe = obter_analise(id2)

    assert detalhe is not None
    assert detalhe["ticker"] == "PETR4"
    assert detalhe["analise"]["sinal"] == "COMPRA"
    assert detalhe["indicadores"]["preco"] == 100.0

    anterior = obter_anterior(
        "PETR4",
        id2,
    )

    assert anterior is not None
    assert anterior["id"] == id1
    assert anterior["signal"] == "NEUTRO"

    estatisticas = obter_estatisticas(
        ticker="PETR4"
    )

    assert estatisticas == {
        "total": 2,
        "compras": 1,
        "vendas": 0,
        "neutros": 1,
        "tickers": 1,
    }
