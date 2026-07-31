import logging

import yfinance as yf

from services.cache_service import cache

logger = logging.getLogger(__name__)


def buscar_dados_ativo(ticker: str):
    if ticker in cache:
        logger.info("Cache HIT: %s", ticker)
        return cache[ticker], None

    try:
        historico = yf.download(
            ticker,
            period="1y",
            interval="1d",
            auto_adjust=False,
            actions=False,
            progress=False,
            threads=False,
            timeout=12,
            multi_level_index=False,
        )

        if historico is None or historico.empty:
            return None, "Ticker inválido ou sem dados de mercado."

        historico = historico.dropna(subset=["Close"])

        if len(historico) < 35:
            return None, (
                "Histórico insuficiente para calcular os indicadores."
            )

        dados = {
            "historico": historico,
        }

        cache[ticker] = dados

        return dados, None

    except Exception:
        logger.exception(
            "Falha ao consultar %s no Yahoo Finance",
            ticker,
        )

        return None, (
            "Não foi possível consultar os dados de mercado agora."
        )
