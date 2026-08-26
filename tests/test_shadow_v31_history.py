from services import history_service


def test_shadow_v31_upsert_por_ticker_data_versao(monkeypatch, tmp_path):
    banco = tmp_path / "shadow.db"
    monkeypatch.setenv("ANALISADOR_DB_PATH", str(banco))

    resultado = {
        "versao": "3.1-shadow-20260826",
        "sinal": "COMPRA",
        "estado": "COMPRA",
        "preco": 42.50,
        "regime_mercado": "ALTA",
    }

    primeiro = history_service.salvar_shadow_v31(
        ticker="PETR4",
        analysis_id=1,
        market_date="2026-08-26",
        legacy_signal="NEUTRO",
        resultado=resultado,
        benchmark_market_date="2026-08-26",
    )

    resultado2 = dict(resultado)
    resultado2["preco"] = 42.70

    segundo = history_service.salvar_shadow_v31(
        ticker="PETR4",
        analysis_id=2,
        market_date="2026-08-26",
        legacy_signal="COMPRA",
        resultado=resultado2,
        benchmark_market_date="2026-08-26",
    )

    itens = history_service.listar_shadow_v31(
        ticker="PETR4"
    )

    assert primeiro == segundo
    assert len(itens) == 1
    assert itens[0]["analysis_id"] == 2
    assert itens[0]["legacy_signal"] == "COMPRA"
    assert itens[0]["price"] == 42.70
