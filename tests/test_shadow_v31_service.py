import pandas as pd

from services.shadow_v31_service import (
    VERSAO_MOTOR,
    avaliar_linha_v31,
)


def linha_compra():
    return pd.Series(
        {
            "Close": 110.0,
            "ema21": 105.0,
            "sma50": 100.0,
            "sma200": 90.0,
            "ema21_slope5": 0.01,
            "sma50_slope20": 0.03,
            "atr_pct": 0.025,
            "rsi14": 64.0,
            "dist_ema21_atr": 1.2,
            "retorno20": 0.10,
            "volume_ratio": 1.35,
            "liquidez20": 80_000_000.0,
            "clv": 0.70,
            "range_atr": 1.20,
            "breakout_alta": True,
        }
    )


def benchmark_alta():
    return pd.Series(
        {
            "Close": 130.0,
            "ema21": 125.0,
            "sma50": 120.0,
            "sma200": 110.0,
            "sma50_slope20": 0.02,
        }
    )


def test_v31_compra_exige_todos_os_criterios():
    resultado = avaliar_linha_v31(
        linha_compra(),
        benchmark_alta(),
    )

    assert resultado["versao"] == VERSAO_MOTOR
    assert resultado["sinal"] == "COMPRA"
    assert resultado["estado"] == "COMPRA"
    assert resultado["regime_mercado"] == "ALTA"
    assert resultado["pendencias"] == []


def test_v31_sem_rompimento_fica_aguardar():
    row = linha_compra()
    row["breakout_alta"] = False

    resultado = avaliar_linha_v31(
        row,
        benchmark_alta(),
    )

    assert resultado["sinal"] == "NEUTRO"
    assert resultado["estado"] == "AGUARDAR"
    assert "rompimento_20" in resultado["pendencias"]


def test_v31_nao_compra_com_mercado_baixista():
    benchmark = benchmark_alta()
    benchmark["Close"] = 90.0
    benchmark["ema21"] = 95.0
    benchmark["sma50"] = 100.0
    benchmark["sma200"] = 110.0
    benchmark["sma50_slope20"] = -0.03

    resultado = avaliar_linha_v31(
        linha_compra(),
        benchmark,
    )

    assert resultado["sinal"] == "NEUTRO"
    assert "mercado_nao_baixista" in resultado["pendencias"]
