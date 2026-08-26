import importlib.util
import logging
from typing import Optional

import pandas as pd
import yfinance as yf

from services.cache_service import cache

logger = logging.getLogger(__name__)

COLUNAS_MERCADO = {"Open", "High", "Low", "Close", "Volume"}


def _scipy_disponivel() -> bool:
    return importlib.util.find_spec("scipy") is not None


def _baixar(
    ticker: str,
    period: str,
    *,
    repair: bool,
):
    return yf.download(
        ticker,
        period=period,
        interval="1d",
        auto_adjust=True,
        actions=False,
        repair=repair,
        progress=False,
        threads=False,
        timeout=12,
        multi_level_index=False,
    )


def _sanear_historico(historico: pd.DataFrame) -> pd.DataFrame:
    if historico is None or historico.empty:
        return pd.DataFrame()

    dados = historico.copy()

    if isinstance(dados.columns, pd.MultiIndex):
        dados.columns = dados.columns.get_level_values(0)

    ausentes = COLUNAS_MERCADO - set(dados.columns)
    if ausentes:
        logger.warning(
            "Yahoo Finance retornou colunas incompletas: %s",
            ", ".join(sorted(ausentes)),
        )
        return pd.DataFrame()

    dados = dados.sort_index()
    dados = dados[~dados.index.duplicated(keep="last")]

    for coluna in COLUNAS_MERCADO:
        dados[coluna] = pd.to_numeric(
            dados[coluna],
            errors="coerce",
        )

    dados = dados.dropna(subset=["High", "Low", "Close"])
    dados["Volume"] = dados["Volume"].fillna(0.0)

    dados = dados[
        (dados["Close"] > 0)
        & (dados["High"] > 0)
        & (dados["Low"] > 0)
        & (dados["High"] >= dados["Low"])
    ]

    return dados


def buscar_dados_ativo(
    ticker: str,
    period: str = "1y",
):
    """Baixa e valida histórico diário de um ativo.

    O modo ``repair=True`` do yfinance usa SciPy em algumas rotinas.
    Quando SciPy não estiver disponível, a consulta continua com
    ``repair=False`` em vez de classificar o ticker incorretamente como
    inválido. Também há uma segunda tentativa sem repair caso a primeira
    consulta retorne vazia.
    """
    cache_key = (ticker, period)

    if cache_key in cache:
        logger.info("Cache HIT: %s (%s)", ticker, period)
        return cache[cache_key], None

    repair = _scipy_disponivel()

    if not repair:
        logger.warning(
            "SciPy não disponível. Consulta %s seguirá com repair=False.",
            ticker,
        )

    try:
        historico = _sanear_historico(
            _baixar(
                ticker,
                period,
                repair=repair,
            )
        )

        if historico.empty and repair:
            logger.warning(
                "Primeira consulta de %s retornou vazia. "
                "Repetindo com repair=False.",
                ticker,
            )
            historico = _sanear_historico(
                _baixar(
                    ticker,
                    period,
                    repair=False,
                )
            )

        if historico.empty:
            return (
                None,
                "Não foi possível obter dados desse ticker agora. "
                "Confira o código do ativo e tente novamente.",
            )

        if len(historico) < 60:
            return (
                None,
                "O ativo possui histórico insuficiente para esta análise. "
                "São necessários pelo menos 60 pregões.",
            )

        ultima_data: Optional[str] = None
        try:
            ultima_data = pd.Timestamp(historico.index[-1]).date().isoformat()
        except Exception:
            logger.warning("Não foi possível identificar a data final de %s", ticker)

        dados = {
            "historico": historico,
            "ultima_data": ultima_data,
            "periodos": int(len(historico)),
            "repair_ativo": bool(repair),
        }

        cache[cache_key] = dados
        return dados, None

    except Exception:
        logger.exception("Falha ao consultar %s no Yahoo Finance", ticker)
        return (
            None,
            "A fonte de dados de mercado está indisponível no momento. "
            "Tente novamente em alguns instantes.",
        )
