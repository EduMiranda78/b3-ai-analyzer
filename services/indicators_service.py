import math

import numpy as np
import pandas as pd


def _numero(valor, padrao=0.0):
    if valor is None or pd.isna(valor):
        return padrao

    return float(valor)


def calcular_indicadores(df: pd.DataFrame) -> dict:
    dados = df.copy()

    fechamento = pd.to_numeric(
        dados["Close"],
        errors="coerce",
    ).dropna()

    if len(fechamento) < 35:
        raise ValueError(
            "Histórico insuficiente para os indicadores."
        )

    ema9 = fechamento.ewm(
        span=9,
        adjust=False,
    ).mean()

    ema21 = fechamento.ewm(
        span=21,
        adjust=False,
    ).mean()

    sma50 = fechamento.rolling(50).mean()

    ema12 = fechamento.ewm(
        span=12,
        adjust=False,
    ).mean()

    ema26 = fechamento.ewm(
        span=26,
        adjust=False,
    ).mean()

    macd = ema12 - ema26

    macd_sinal = macd.ewm(
        span=9,
        adjust=False,
    ).mean()

    macd_histograma = macd - macd_sinal

    delta = fechamento.diff()

    ganhos = delta.clip(lower=0)
    perdas = -delta.clip(upper=0)

    ganho_medio = ganhos.ewm(
        alpha=1 / 14,
        min_periods=14,
        adjust=False,
    ).mean()

    perda_media = perdas.ewm(
        alpha=1 / 14,
        min_periods=14,
        adjust=False,
    ).mean()

    rs = ganho_medio / perda_media.replace(0, np.nan)

    rsi = 100 - (100 / (1 + rs))

    rsi = rsi.mask(
        (ganho_medio == 0) & (perda_media == 0),
        50,
    )

    rsi = rsi.mask(
        (perda_media == 0) & (ganho_medio > 0),
        100,
    )

    rsi = rsi.mask(
        (ganho_medio == 0) & (perda_media > 0),
        0,
    )

    retornos = fechamento.pct_change()

    volatilidade = (
        retornos
        .rolling(20)
        .std()
        * math.sqrt(252)
    )

    maximo20 = (
        pd.to_numeric(
            dados["High"],
            errors="coerce",
        )
        .rolling(20)
        .max()
    )

    minimo20 = (
        pd.to_numeric(
            dados["Low"],
            errors="coerce",
        )
        .rolling(20)
        .min()
    )

    volume = pd.to_numeric(
        dados["Volume"],
        errors="coerce",
    )

    volume_medio20 = volume.rolling(20).mean()

    preco = _numero(fechamento.iloc[-1])
    preco_anterior = _numero(
        fechamento.iloc[-2],
        preco,
    )

    variacao_dia = (
        (preco / preco_anterior) - 1
        if preco_anterior
        else 0.0
    )

    ema9_atual = _numero(ema9.iloc[-1])
    ema21_atual = _numero(ema21.iloc[-1])

    macd_atual = _numero(macd.iloc[-1])
    macd_sinal_atual = _numero(
        macd_sinal.iloc[-1]
    )

    return {
        "preco": preco,
        "variacao_dia": variacao_dia,
        "ema9": ema9_atual,
        "ema21": ema21_atual,
        "sma50": _numero(sma50.iloc[-1]),
        "rsi14": _numero(rsi.iloc[-1], 50.0),
        "macd": macd_atual,
        "macd_sinal": macd_sinal_atual,
        "macd_histograma": _numero(
            macd_histograma.iloc[-1]
        ),
        "volatilidade20": _numero(
            volatilidade.iloc[-1]
        ),
        "suporte20": _numero(
            minimo20.iloc[-1]
        ),
        "resistencia20": _numero(
            maximo20.iloc[-1]
        ),
        "volume": _numero(volume.iloc[-1]),
        "volume_medio20": _numero(
            volume_medio20.iloc[-1]
        ),
        "tendencia_curta": (
            "alta"
            if ema9_atual > ema21_atual
            else "baixa"
        ),
        "macd_status": (
            "positivo"
            if macd_atual > macd_sinal_atual
            else "negativo"
        ),
    }
