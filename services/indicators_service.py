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


def _classificar_tendencia(
    ema9: float,
    ema21: float,
    tolerancia: float = 0.001,
) -> str:
    if ema21 <= 0:
        return "indefinida"

    distancia = (
        ema9 / ema21
    ) - 1

    if distancia > tolerancia:
        return "alta"

    if distancia < -tolerancia:
        return "baixa"

    return "lateral"


def _classificar_macd(
    macd: float,
    sinal: float,
    tolerancia: float = 1e-9,
) -> str:
    diferenca = macd - sinal

    if diferenca > tolerancia:
        return "positivo"

    if diferenca < -tolerancia:
        return "negativo"

    return "neutro"


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

    validos = (
        fechamento.notna()
        & maxima.notna()
        & minima.notna()
    )

    fechamento = fechamento[validos]
    maxima = maxima[validos]
    minima = minima[validos]
    volume = volume[validos].fillna(0.0)

    if len(fechamento) < 60:
        raise ValueError(
            "Histórico insuficiente. "
            "São necessários pelo menos "
            "60 pregões."
        )

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

    # Níveis de referência usam apenas pregões anteriores.
    # O shift(1) evita que a barra atual "crie" o próprio
    # suporte/resistência e reduz viés de look-ahead.
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

    # O volume atual é comparado com os 20 pregões anteriores,
    # e não com uma média que já contém a própria barra.
    volume_medio20 = (
        volume
        .rolling(20)
        .mean()
        .shift(1)
    )

    valor_financeiro = (
        fechamento * volume
    )

    valor_financeiro_medio20 = (
        valor_financeiro
        .rolling(20)
        .mean()
        .shift(1)
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

    ema9_atual = _numero(
        ema9.iloc[-1]
    )

    ema21_atual = _numero(
        ema21.iloc[-1]
    )

    sma50_atual = _numero(
        sma50.iloc[-1]
    )

    sma200_raw = sma200.iloc[-1]
    sma200_disponivel = (
        not pd.isna(sma200_raw)
    )
    sma200_atual = _numero(
        sma200_raw
    )

    macd_atual = _numero(
        macd.iloc[-1]
    )

    macd_sinal_atual = _numero(
        macd_sinal.iloc[-1]
    )

    atr_atual = _numero(
        atr14.iloc[-1]
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

    range_atual = _numero(
        (
            maxima.iloc[-1]
            - minima.iloc[-1]
        )
    )

    range_atr = (
        range_atual / atr_atual
        if atr_atual > 0
        else 0.0
    )

    # Close Location Value: -1 = fechamento na mínima,
    # +1 = fechamento na máxima. Ajuda a medir a força
    # da barra sem depender apenas de osciladores.
    if range_atual > 0:
        clv = (
            (
                2 * preco
                - maxima.iloc[-1]
                - minima.iloc[-1]
            )
            / range_atual
        )
    else:
        clv = 0.0

    clv = float(
        max(
            -1.0,
            min(1.0, clv),
        )
    )

    if (
        resistencia > 0
        and preco > resistencia
    ):
        rompimento20 = "alta"
    elif (
        suporte > 0
        and preco < suporte
    ):
        rompimento20 = "baixa"
    else:
        rompimento20 = "nenhum"

    return {
        "preco": preco,
        "variacao_dia": variacao_dia,
        "ema9": ema9_atual,
        "ema21": ema21_atual,
        "sma50": sma50_atual,
        "sma200": sma200_atual,
        "sma200_disponivel": (
            sma200_disponivel
        ),
        "rsi14": _numero(
            rsi.iloc[-1],
            50.0,
        ),
        "macd": macd_atual,
        "macd_sinal": macd_sinal_atual,
        "macd_histograma": _numero(
            macd_histograma.iloc[-1]
        ),
        "atr14": atr_atual,
        "atr_percentual": (
            atr_atual / preco
            if preco > 0
            else 0.0
        ),
        "volatilidade20": _numero(
            volatilidade20.iloc[-1]
        ),
        "suporte20": suporte,
        "resistencia20": resistencia,
        "volume": volume_atual,
        "volume_medio20": media_volume,
        "volume_ratio": volume_ratio,
        "valor_financeiro_medio20": (
            _numero(
                valor_financeiro_medio20
                .iloc[-1]
            )
        ),
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
        "distancia_suporte": distancia_suporte,
        "distancia_resistencia": distancia_resistencia,
        "periodos": int(
            len(fechamento)
        ),
        "clv": clv,
        "range_atr": range_atr,
        "rompimento20": rompimento20,
        "tendencia_curta": (
            _classificar_tendencia(
                ema9_atual,
                ema21_atual,
            )
        ),
        "macd_status": (
            _classificar_macd(
                macd_atual,
                macd_sinal_atual,
            )
        ),
    }
