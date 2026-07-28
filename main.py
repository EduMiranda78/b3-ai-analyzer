import logging
import re
import time
from datetime import datetime
from pathlib import Path

import markdown2
from dotenv import load_dotenv
from flask import Flask, render_template, request


BASE_DIR = Path(__file__).resolve().parent

load_dotenv(
    dotenv_path=BASE_DIR / ".env",
)

from services.gemini_service import (
    gerar_relatorio as gerar_relatorio_ia,
)
from services.indicators_service import (
    calcular_indicadores,
)
from services.market_service import (
    buscar_dados_ativo,
)
from services.telegram_service import (
    enviar_para_telegram,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = False


TICKER_PATTERN = re.compile(
    r"^[A-Z0-9]{4,6}(\.SA)?$"
)

SINAL_PATTERN = re.compile(
    r"SINALIZAÇÃO\s+FINAL\s*:\s*"
    r"(COMPRA|VENDA|NEUTRO)",
    re.IGNORECASE,
)


def formatar_dados_para_ia(
    ticker: str,
    indicadores: dict,
) -> str:
    ticker_exibicao = ticker.removesuffix(".SA")

    return f"""Ticker: {ticker_exibicao}
Data da análise: {datetime.now():%d/%m/%Y %H:%M}
Preço de fechamento: R$ {indicadores['preco']:.2f}
Variação do último pregão: {indicadores['variacao_dia']:.2%}
EMA 9: {indicadores['ema9']:.2f}
EMA 21: {indicadores['ema21']:.2f}
SMA 50: {indicadores['sma50']:.2f}
Tendência curta: {indicadores['tendencia_curta']}
RSI 14: {indicadores['rsi14']:.2f}
MACD: {indicadores['macd']:.4f}
Sinal do MACD: {indicadores['macd_sinal']:.4f}
Histograma do MACD: {indicadores['macd_histograma']:.4f}
Estado do MACD: {indicadores['macd_status']}
Volatilidade anualizada de 20 pregões: {indicadores['volatilidade20']:.2%}
Suporte de 20 pregões: R$ {indicadores['suporte20']:.2f}
Resistência de 20 pregões: R$ {indicadores['resistencia20']:.2f}
Volume do último pregão: {indicadores['volume']:.0f}
Volume médio de 20 pregões: {indicadores['volume_medio20']:.0f}"""


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return {
        "status": "ok",
    }, 200


@app.post("/gerar_relatorio")
def gerar_relatorio():
    inicio_total = time.perf_counter()

    ticker = (
        request.form
        .get("ticker", "")
        .strip()
        .upper()
    )

    if not TICKER_PATTERN.fullmatch(ticker):
        return render_template(
            "relatorio.html",
            error="Ticker inválido.",
        ), 400

    if not ticker.endswith(".SA"):
        ticker += ".SA"

    inicio_mercado = time.perf_counter()

    dados, erro = buscar_dados_ativo(ticker)

    logger.info(
        "Yahoo Finance %s: %.2fs",
        ticker,
        time.perf_counter() - inicio_mercado,
    )

    if erro:
        return render_template(
            "relatorio.html",
            error=erro,
        ), 502

    try:
        indicadores = calcular_indicadores(
            dados["historico"]
        )

        dados_ia = formatar_dados_para_ia(
            ticker,
            indicadores,
        )

        prompt_path = (
            BASE_DIR / "prompt_analise.txt"
        )

        prompt_base = prompt_path.read_text(
            encoding="utf-8"
        )

        prompt = prompt_base.replace(
            "{dados_do_ativo}",
            dados_ia,
        )

        inicio_ia = time.perf_counter()

        texto = gerar_relatorio_ia(prompt)

        logger.info(
            "Gemini %s: %.2fs",
            ticker,
            time.perf_counter() - inicio_ia,
        )

        html = markdown2.markdown(
            texto,
            extras=["tables"],
            safe_mode="escape",
        )

        match = SINAL_PATTERN.search(texto)

        sinal = (
            match.group(1).upper()
            if match
            else "SEM SINAL"
        )

        enviar_para_telegram(
            ticker.removesuffix(".SA"),
            sinal,
        )

        logger.info(
            "Análise total %s: %.2fs",
            ticker,
            time.perf_counter() - inicio_total,
        )

        return render_template(
            "relatorio.html",
            relatorio=html,
            ticker=ticker.removesuffix(".SA"),
        )

    except Exception:
        logger.exception(
            "Falha ao gerar análise de %s",
            ticker,
        )

        return render_template(
            "relatorio.html",
            error=(
                "Não foi possível gerar "
                "o relatório agora."
            ),
        ), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
    )
