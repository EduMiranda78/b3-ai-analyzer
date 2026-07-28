import numpy as np
import pandas as pd
import pytest

from services.indicators_service import (
    calcular_indicadores,
)


def criar_historico():
    indice = pd.date_range(
        "2026-01-01",
        periods=100,
        freq="B",
    )

    fechamento = np.arange(
        100,
        200,
        dtype=float,
    )

    return pd.DataFrame(
        {
            "Open": fechamento - 1,
            "High": fechamento + 2,
            "Low": fechamento - 2,
            "Close": fechamento,
            "Volume": np.full(
                100,
                1_000_000,
                dtype=float,
            ),
        },
        index=indice,
    )


def test_calcula_indicadores_de_alta():
    resultado = calcular_indicadores(
        criar_historico()
    )

    assert resultado["preco"] == pytest.approx(
        199.0
    )

    assert resultado["sma50"] == pytest.approx(
        174.5
    )

    assert resultado["suporte20"] == pytest.approx(
        178.0
    )

    assert resultado[
        "resistencia20"
    ] == pytest.approx(
        201.0
    )

    assert resultado[
        "volume_medio20"
    ] == pytest.approx(
        1_000_000
    )

    assert resultado[
        "tendencia_curta"
    ] == "alta"

    assert resultado[
        "macd_status"
    ] == "positivo"

    assert 0 <= resultado["rsi14"] <= 100


def test_rejeita_historico_curto():
    historico = criar_historico().head(20)

    with pytest.raises(
        ValueError,
        match="Histórico insuficiente",
    ):
        calcular_indicadores(historico)
