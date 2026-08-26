import pandas as pd

from services import market_service


def _historico_valido(periodos=80):
    indice = pd.date_range("2026-01-01", periods=periodos, freq="B")
    return pd.DataFrame(
        {
            "Open": [10.0] * periodos,
            "High": [11.0] * periodos,
            "Low": [9.0] * periodos,
            "Close": [10.5] * periodos,
            "Volume": [1_000_000.0] * periodos,
        },
        index=indice,
    )


def test_funciona_sem_scipy(monkeypatch):
    market_service.cache.clear()
    chamadas = []

    monkeypatch.setattr(market_service, "_scipy_disponivel", lambda: False)

    def baixar(ticker, period, *, repair):
        chamadas.append(repair)
        return _historico_valido()

    monkeypatch.setattr(market_service, "_baixar", baixar)

    dados, erro = market_service.buscar_dados_ativo("PETR4.SA")

    assert erro is None
    assert dados is not None
    assert chamadas == [False]
    assert dados["periodos"] == 80


def test_repete_sem_repair_quando_primeira_consulta_vazia(monkeypatch):
    market_service.cache.clear()
    chamadas = []

    monkeypatch.setattr(market_service, "_scipy_disponivel", lambda: True)

    def baixar(ticker, period, *, repair):
        chamadas.append(repair)
        if repair:
            return pd.DataFrame()
        return _historico_valido()

    monkeypatch.setattr(market_service, "_baixar", baixar)

    dados, erro = market_service.buscar_dados_ativo("VALE3.SA")

    assert erro is None
    assert dados is not None
    assert chamadas == [True, False]


def test_nao_chama_ticker_invalido_quando_fonte_retorna_vazio(monkeypatch):
    market_service.cache.clear()
    monkeypatch.setattr(market_service, "_scipy_disponivel", lambda: False)
    monkeypatch.setattr(
        market_service,
        "_baixar",
        lambda *args, **kwargs: pd.DataFrame(),
    )

    dados, erro = market_service.buscar_dados_ativo("XXXX3.SA")

    assert dados is None
    assert "Confira o código" in erro
    assert "inválido" not in erro.lower()
