import math

import numpy as np
import pandas as pd


COLUNAS_OBRIGATORIAS = {
    "High",
    "Low",
    "Close",
    "Volume",
}


def _numero(valor, padrao=0.0):
    if valor is None or pd.isna(valor):
        return float(padrao)

    return float(valor)


def calcular_indicadores(
    df: pd.DataFrame,
) -> dict:
    colunas_ausentes = (
        COLUNAS_OBRIGATORIAS
        - set(df.columns)
    )

    if colunas_ausentes:
        nomes = ", ".join(
            sorted(colunas_ausentes)
        )

        raise ValueError(
            f"Colunas ausentes: {nomes}"
        )

    dados = df.copy()

    fechamento = pd.to_numeric(
        dados["Close"],
        errors="coerce",
    )

    maxima = pd.to_numeric(
        dados["High"],
        errors="coerce",
    )

    minima = pd.to_numeric(
        dados["Low"],
        errors="coerce",
    )

    volume = pd.to_numeric(
        dados["Volume"],
        errors="coerce",
    )

    validos = fechamento.notna()

    fechamento = fechamento[validos]
    maxima = maxima[validos]
    minima = minima[validos]
    volume = volume[validos]

    if len(fechamento) < 60:
        raise ValueError(
            "Histórico insuficiente. "
            "São necessários pelo menos "
            "60 pregões."
        )

    maximo = pd.to_numeric(
        dados["High"],
        errors="coerce",
    ).reindex(
        fechamento.index
    )

    minimo = pd.to_numeric(
        dados["Low"],
        errors="coerce",
    ).reindex(
        fechamento.index
    )

    volume = pd.to_numeric(
        dados["Volume"],
        errors="coerce",
    ).reindex(
        fechamento.index
    ).fillna(0.0)

    ema9 = fechamento.ewm(
        span=9,
        adjust=False,
    ).mean()

    ema21 = fechamento.ewm(
        span=21,
        adjust=False,
    ).mean()

    sma50 = fechamento.rolling(
        50
    ).mean()

    sma200 = fechamento.rolling(
        200
    ).mean()

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

    macd_histograma = (
        macd - macd_sinal
    )

    delta = fechamento.diff()

    ganhos = delta.clip(
        lower=0
    )

    perdas = -delta.clip(
        upper=0
    )

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

    rs = (
        ganho_medio
        / perda_media.replace(
            0,
            np.nan,
        )
    )

    rsi = 100 - (
        100 / (1 + rs)
    )

    rsi = rsi.mask(
        (
            (ganho_medio == 0)
            & (perda_media == 0)
        ),
        50,
    )

    rsi = rsi.mask(
        (
            (perda_media == 0)
            & (ganho_medio > 0)
        ),
        100,
    )

    rsi = rsi.mask(
        (
            (ganho_medio == 0)
            & (perda_media > 0)
        ),
        0,
    )

    fechamento_anterior = (
        fechamento.shift(1)
    )

    true_range = pd.concat(
        [
            maxima - minima,
            (
                maxima
                - fechamento_anterior
            ).abs(),
            (
                minima
                - fechamento_anterior
            ).abs(),
        ],
        axis=1,
    ).max(axis=1)

    atr14 = true_range.ewm(
        alpha=1 / 14,
        min_periods=14,
        adjust=False,
    ).mean()

    retornos = fechamento.pct_change()

    volatilidade20 = (
        retornos
        .rolling(
            20,
            min_periods=2,
        )
        .std()
        * math.sqrt(252)
    )

    suporte20 = (
        minima
        .rolling(20)
        .min()
        .shift(1)
    )

    resistencia20 = (
        maxima
        .rolling(20)
        .max()
        .shift(1)
    )

    volume_medio20 = (
        volume
        .rolling(20)
        .mean()
    )

    preco = _numero(
        fechamento.iloc[-1]
    )

    preco_anterior = _numero(
        fechamento.iloc[-2],
        preco,
    )

    variacao_dia = (
        (preco / preco_anterior) - 1
        if preco_anterior
        else 0.0
    )

    media_volume = _numero(
        volume_medio20.iloc[-1]
    )

    volume_atual = _numero(
        volume.iloc[-1]
    )

    volume_ratio = (
        volume_atual / media_volume
        if media_volume > 0
        else 0.0
    )

    suporte = _numero(
        suporte20.iloc[-1]
    )

    resistencia = _numero(
        resistencia20.iloc[-1]
    )

    distancia_suporte = (
        (preco - suporte) / preco
        if preco > 0 and suporte > 0
        else 0.0
    )

    distancia_resistencia = (
        (resistencia - preco) / preco
        if preco > 0
        and resistencia > 0
        else 0.0
    )

    ema9_atual = _numero(
        ema9.iloc[-1]
    )

    ema21_atual = _numero(
        ema21.iloc[-1]
    )

    macd_atual = _numero(
        macd.iloc[-1]
    )

    macd_sinal_atual = _numero(
        macd_sinal.iloc[-1]
    )

    suporte_atual = _numero(
        suporte20.iloc[-1]
    )

    resistencia_atual = _numero(
        resistencia20.iloc[-1]
    )

    volume_atual = _numero(
        volume.iloc[-1]
    )

    volume_medio_atual = _numero(
        volume_medio20.iloc[-1]
    )

    volume_ratio = (
        volume_atual / volume_medio_atual
        if volume_medio_atual > 0
        else 0.0
    )

    distancia_suporte = (
        (preco - suporte_atual) / preco
        if preco > 0 and suporte_atual > 0
        else 0.0
    )

    distancia_resistencia = (
        (resistencia_atual - preco) / preco
        if preco > 0 and resistencia_atual > 0
        else 0.0
    )

    return {
        "preco": preco,
        "variacao_dia": variacao_dia,
        "ema9": ema9_atual,
        "ema21": ema21_atual,
        "sma50": _numero(
            sma50.iloc[-1]
        ),
        "sma200": _numero(
            sma200.iloc[-1]
        ),
        "rsi14": _numero(
            rsi.iloc[-1],
            50.0,
        ),
        "macd": macd_atual,
        "macd_sinal": (
            macd_sinal_atual
        ),
        "macd_histograma": _numero(
            macd_histograma.iloc[-1]
        ),
        "atr14": _numero(
            atr14.iloc[-1]
        ),
        "volatilidade20": _numero(
            volatilidade20.iloc[-1]
        ),
        "suporte20": suporte,
        "resistencia20": resistencia,
        "volume": volume_atual,
        "volume_medio20": media_volume,
        "volume_ratio": volume_ratio,
        "retorno20": _numero(
            fechamento
            .pct_change(20)
            .iloc[-1]
        ),
        "retorno60": _numero(
            fechamento
            .pct_change(60)
            .iloc[-1]
        ),
        "distancia_suporte": (
            distancia_suporte
        ),
        "distancia_resistencia": (
            distancia_resistencia
        ),
        "distancia_suporte": distancia_suporte,
        "distancia_resistencia": distancia_resistencia,
        "tendencia_curta": (
            "alta"
            if ema9_atual > ema21_atual
            else "baixa"
        ),
        "macd_status": (
            "positivo"
            if macd_atual
            > macd_sinal_atual
            else "negativo"
        ),
    }
