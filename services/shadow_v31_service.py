from __future__ import annotations

import logging
from threading import Thread
from typing import Optional

import numpy as np
import pandas as pd

from services.history_service import salvar_shadow_v31
from services.market_service import buscar_dados_ativo


logger = logging.getLogger(__name__)

VERSAO_MOTOR = "3.1-shadow-20260826"
BENCHMARK_TICKER = "BOVA11.SA"

LIQUIDEZ_MIN = 5_000_000.0
ATR_PCT_MAX = 0.075
DIST_EMA21_ATR_MAX = 2.0
RETORNO20_MAX = 0.18


def _numero(valor, padrao=0.0) -> float:
    if valor is None or pd.isna(valor):
        return float(padrao)
    return float(valor)


def preparar_features_v31(df: pd.DataFrame) -> pd.DataFrame:
    obrigatorias = {"Open", "High", "Low", "Close", "Volume"}
    ausentes = obrigatorias - set(df.columns)
    if ausentes:
        raise ValueError(
            "Colunas ausentes no histórico: "
            + ", ".join(sorted(ausentes))
        )

    dados = df.copy().sort_index()

    for coluna in obrigatorias:
        dados[coluna] = pd.to_numeric(
            dados[coluna],
            errors="coerce",
        )

    dados = dados.dropna(
        subset=["High", "Low", "Close"]
    )
    dados["Volume"] = dados["Volume"].fillna(0.0)

    if len(dados) < 220:
        raise ValueError(
            "Histórico insuficiente para o Motor V3.1. "
            "São necessários pelo menos 220 pregões."
        )

    close = dados["Close"]
    high = dados["High"]
    low = dados["Low"]
    volume = dados["Volume"]

    dados["ema21"] = close.ewm(
        span=21,
        adjust=False,
    ).mean()
    dados["sma50"] = close.rolling(50).mean()
    dados["sma200"] = close.rolling(200).mean()
    dados["ema21_slope5"] = dados["ema21"].pct_change(5)
    dados["sma50_slope20"] = dados["sma50"].pct_change(20)

    delta = close.diff()
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
    dados["rsi14"] = rsi

    fechamento_anterior = close.shift(1)
    true_range = pd.concat(
        [
            high - low,
            (high - fechamento_anterior).abs(),
            (low - fechamento_anterior).abs(),
        ],
        axis=1,
    ).max(axis=1)
    dados["atr14"] = true_range.ewm(
        alpha=1 / 14,
        min_periods=14,
        adjust=False,
    ).mean()
    dados["atr_pct"] = dados["atr14"] / close

    dados["retorno20"] = close.pct_change(20)
    dados["resistencia20"] = high.rolling(20).max().shift(1)
    dados["suporte20"] = low.rolling(20).min().shift(1)
    dados["breakout_alta"] = close > dados["resistencia20"]

    dados["volume_medio20"] = volume.rolling(20).mean().shift(1)
    dados["volume_ratio"] = (
        volume
        / dados["volume_medio20"].replace(0, np.nan)
    )
    dados["liquidez20"] = (
        close * volume
    ).rolling(20).mean().shift(1)

    amplitude = high - low
    dados["range_atr"] = (
        amplitude
        / dados["atr14"].replace(0, np.nan)
    )
    dados["clv"] = np.where(
        amplitude > 0,
        (2 * close - high - low) / amplitude,
        0.0,
    )
    dados["clv"] = dados["clv"].clip(-1, 1)
    dados["dist_ema21_atr"] = (
        (close - dados["ema21"])
        / dados["atr14"].replace(0, np.nan)
    )

    return dados


def _direcao(row: pd.Series) -> str:
    close = _numero(row.get("Close"))
    ema21 = _numero(row.get("ema21"))
    sma50 = _numero(row.get("sma50"))
    sma200 = row.get("sma200")
    slope21 = _numero(row.get("ema21_slope5"))
    slope50 = _numero(row.get("sma50_slope20"))

    sma200_valida = sma200 is not None and not pd.isna(sma200)

    alta = (
        close > ema21 > sma50
        and slope21 > 0
        and slope50 > 0
    )
    baixa = (
        close < ema21 < sma50
        and slope21 < 0
        and slope50 < 0
    )

    if sma200_valida:
        alta = alta and close > float(sma200)
        baixa = baixa and close < float(sma200)

    if alta:
        return "ALTA"
    if baixa:
        return "BAIXA"
    return "LATERAL"


def _regime_mercado(row: pd.Series) -> str:
    close = _numero(row.get("Close"))
    ema21 = _numero(row.get("ema21"))
    sma50 = _numero(row.get("sma50"))
    sma200 = row.get("sma200")
    slope50 = _numero(row.get("sma50_slope20"))

    bull = int(close > ema21) + int(ema21 > sma50) + int(slope50 > 0)
    bear = int(close < ema21) + int(ema21 < sma50) + int(slope50 < 0)

    if sma200 is not None and not pd.isna(sma200):
        bull += int(close > float(sma200))
        bear += int(close < float(sma200))

    if bull >= 3 and bull > bear:
        return "ALTA"
    if bear >= 3 and bear > bull:
        return "BAIXA"
    return "LATERAL"


def avaliar_linha_v31(
    row: pd.Series,
    benchmark_row: pd.Series,
) -> dict:
    direcao = _direcao(row)
    regime = _regime_mercado(benchmark_row)

    atr_pct = _numero(row.get("atr_pct"), np.nan)
    rsi = _numero(row.get("rsi14"), np.nan)
    dist = _numero(row.get("dist_ema21_atr"), np.nan)
    retorno20 = _numero(row.get("retorno20"), np.nan)
    volume_ratio = _numero(row.get("volume_ratio"), np.nan)
    liquidez = _numero(row.get("liquidez20"))
    clv = _numero(row.get("clv"))
    range_atr = _numero(row.get("range_atr"))
    breakout_alta = bool(row.get("breakout_alta", False))

    criterios = {
        "tendencia_alta": direcao == "ALTA",
        "mercado_nao_baixista": regime != "BAIXA",
        "rompimento_20": breakout_alta,
        "fechamento_forte": clv >= 0.45,
        "amplitude_confirmada": range_atr >= 0.80,
        "volume_confirmado": volume_ratio >= 1.00,
        "liquidez_ok": liquidez >= LIQUIDEZ_MIN,
        "volatilidade_ok": (
            not np.isnan(atr_pct)
            and atr_pct <= ATR_PCT_MAX
        ),
        "rsi_nao_estendido": (
            not np.isnan(rsi)
            and rsi <= 72
        ),
        "distancia_media_ok": (
            not np.isnan(dist)
            and dist <= DIST_EMA21_ATR_MAX
        ),
        "retorno20_nao_estendido": (
            not np.isnan(retorno20)
            and retorno20 <= RETORNO20_MAX
        ),
    }

    compra = all(criterios.values())

    if compra:
        estado = "COMPRA"
    elif direcao == "BAIXA":
        estado = "EVITAR"
    elif direcao == "ALTA":
        estado = "AGUARDAR"
    else:
        estado = "NEUTRO"

    pendencias = [
        nome
        for nome, ok in criterios.items()
        if not ok
    ]

    return {
        "versao": VERSAO_MOTOR,
        "sinal": "COMPRA" if compra else "NEUTRO",
        "estado": estado,
        "direcao": direcao,
        "regime_mercado": regime,
        "preco": _numero(row.get("Close")),
        "rsi14": None if np.isnan(rsi) else round(rsi, 4),
        "atr_pct": None if np.isnan(atr_pct) else round(atr_pct, 6),
        "dist_ema21_atr": None if np.isnan(dist) else round(dist, 4),
        "retorno20": None if np.isnan(retorno20) else round(retorno20, 6),
        "volume_ratio": None if np.isnan(volume_ratio) else round(volume_ratio, 4),
        "liquidez20": round(liquidez, 2),
        "clv": round(clv, 4),
        "range_atr": round(range_atr, 4),
        "criterios": criterios,
        "pendencias": pendencias,
    }


def avaliar_shadow_v31(
    historico_ativo: pd.DataFrame,
    historico_benchmark: pd.DataFrame,
) -> dict:
    ativo = preparar_features_v31(historico_ativo)
    benchmark = preparar_features_v31(historico_benchmark)

    data_ativo = pd.Timestamp(ativo.index[-1])
    benchmark_ate_data = benchmark.loc[
        pd.to_datetime(benchmark.index) <= data_ativo
    ]

    if benchmark_ate_data.empty:
        raise ValueError(
            "Benchmark sem dados disponíveis até a data do ativo."
        )

    benchmark_row = benchmark_ate_data.iloc[-1]

    resultado = avaliar_linha_v31(
        ativo.iloc[-1],
        benchmark_row,
    )
    resultado["data_mercado"] = data_ativo.date().isoformat()

    try:
        resultado["data_benchmark"] = pd.Timestamp(
            benchmark_row.name
        ).date().isoformat()
    except Exception:
        resultado["data_benchmark"] = None

    return resultado


def executar_shadow_v31(
    *,
    ticker: str,
    historico_ativo: pd.DataFrame,
    legacy_signal: str,
    analysis_id: Optional[int],
    market_date: Optional[str],
) -> Optional[dict]:
    dados_benchmark, erro_benchmark = buscar_dados_ativo(
        BENCHMARK_TICKER,
        period="1y",
    )

    if erro_benchmark or not dados_benchmark:
        logger.warning(
            "Shadow V3.1 %s sem benchmark: %s",
            ticker,
            erro_benchmark or "sem dados",
        )
        return None

    resultado = avaliar_shadow_v31(
        historico_ativo,
        dados_benchmark["historico"],
    )

    salvar_shadow_v31(
        ticker=ticker.removesuffix(".SA"),
        analysis_id=analysis_id,
        market_date=(
            market_date
            or resultado.get("data_mercado")
        ),
        legacy_signal=legacy_signal,
        resultado=resultado,
        benchmark_ticker=BENCHMARK_TICKER.removesuffix(".SA"),
        benchmark_market_date=(
            dados_benchmark.get("ultima_data")
            or resultado.get("data_benchmark")
        ),
    )

    logger.info(
        "Shadow V3.1 %s: estado=%s | sinal=%s | mercado=%s",
        ticker,
        resultado["estado"],
        resultado["sinal"],
        resultado["regime_mercado"],
    )

    return resultado


def agendar_shadow_v31(
    *,
    ticker: str,
    historico_ativo: pd.DataFrame,
    legacy_signal: str,
    analysis_id: Optional[int],
    market_date: Optional[str],
) -> bool:
    if not isinstance(historico_ativo, pd.DataFrame):
        logger.warning(
            "Shadow V3.1 ignorado para %s: histórico não é DataFrame.",
            ticker,
        )
        return False

    historico_copia = historico_ativo.copy()

    def worker():
        try:
            executar_shadow_v31(
                ticker=ticker,
                historico_ativo=historico_copia,
                legacy_signal=legacy_signal,
                analysis_id=analysis_id,
                market_date=market_date,
            )
        except Exception:
            logger.exception(
                "Falha isolada no Shadow V3.1 de %s",
                ticker,
            )

    Thread(
        target=worker,
        name=f"shadow-v31-{ticker}",
        daemon=True,
    ).start()

    return True
