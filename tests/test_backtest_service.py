import numpy as np
import pandas as pd

from services.backtest_service import (
    BacktestConfig,
    avaliar_sinais_historicos,
)


def criar_tendencia_alta():
    indice = pd.date_range(
        "2024-01-01",
        periods=140,
        freq="B",
    )

    fechamento = np.linspace(
        100,
        180,
        len(indice),
    )

    return pd.DataFrame(
        {
            "Open": fechamento - 0.2,
            "High": fechamento + 1.0,
            "Low": fechamento - 1.0,
            "Close": fechamento,
            "Volume": np.full(
                len(indice),
                1_500_000.0,
            ),
        },
        index=indice,
    )


def test_backtest_usa_entrada_na_barra_seguinte():
    dados = criar_tendencia_alta()

    resultado = avaliar_sinais_historicos(
        dados,
        BacktestConfig(
            horizonte=5,
            warmup=60,
        ),
    )

    assert resultado["total_sinais"] >= 1
    assert resultado["compras"] >= 1
    assert resultado["taxa_acerto"] > 0

    primeiro = resultado["eventos"][0]

    assert (
        primeiro["data_sinal"]
        != primeiro["data_entrada"]
    )


def test_backtest_rejeita_historico_curto():
    dados = criar_tendencia_alta().head(60)

    try:
        avaliar_sinais_historicos(
            dados,
            BacktestConfig(
                horizonte=10,
                warmup=60,
            ),
        )
    except ValueError as erro:
        assert "Histórico insuficiente" in str(erro)
    else:
        raise AssertionError(
            "Era esperado ValueError."
        )
