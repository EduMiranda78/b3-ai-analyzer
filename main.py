import logging
import re
import time
from datetime import datetime
from pathlib import Path

import markdown2
from dotenv import load_dotenv
from flask import Flask, abort, render_template, request


BASE_DIR = Path(__file__).resolve().parent

load_dotenv(
    dotenv_path=BASE_DIR / ".env",
)

from services.gemini_service import (
    gerar_relatorio as gerar_relatorio_ia,
)
from services.history_service import (
    inicializar_banco,
    listar_analises,
    obter_analise,
    obter_anterior,
    obter_estatisticas,
    salvar_analise,
)
from services.indicators_service import (
    calcular_indicadores,
)
from services.market_service import (
    buscar_dados_ativo,
)
from services.report_service import (
    gerar_relatorio_local,
)
from services.signal_service import (
    calcular_sinal_tecnico,
)
from services.telegram_service import (
    enviar_para_telegram,
)


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | %(levelname)s | "
        "%(message)s"
    ),
)

logging.getLogger(
    "httpx"
).setLevel(
    logging.WARNING
)

logging.getLogger(
    "google_genai"
).setLevel(
    logging.WARNING
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

app.config.update(
    TEMPLATES_AUTO_RELOAD=False,
)

inicializar_banco()


def formatar_dados_para_ia(
    ticker: str,
    indicadores: dict,
    analise: dict,
) -> str:
    ticker_exibicao = ticker.removesuffix(
        ".SA"
    )

    motivos = "\n".join(
        f"- {motivo}"
        for motivo in analise["motivos"]
    )

    alertas = (
        "\n".join(
            f"- {alerta}"
            for alerta in analise["alertas"]
        )
        or "- Nenhum alerta adicional."
    )

    preco_referencia = (
        f"R$ {analise['preco_referencia']:.2f}"
        if analise["preco_referencia"]
        is not None
        else "Não aplicável"
    )

    stop = (
        f"R$ {analise['stop']:.2f}"
        if analise["stop"] is not None
        else "Não aplicável"
    )

    alvo = (
        f"R$ {analise['alvo']:.2f}"
        if analise["alvo"] is not None
        else "Não aplicável"
    )

    risco_retorno = (
        f"{analise['risco_retorno']:.2f}"
        if analise["risco_retorno"]
        is not None
        else "Não aplicável"
    )

    return f"""Ticker: {ticker_exibicao}
Data: {datetime.now():%d/%m/%Y %H:%M}

SINAL FIXO DO SISTEMA: {analise['sinal']}
Pontuação: {analise['pontos']}
Confiança: {analise['confianca']}

Preço: R$ {indicadores['preco']:.2f}
Variação diária: {indicadores['variacao_dia']:.2%}
Retorno em 20 pregões: {indicadores['retorno20']:.2%}
Retorno em 60 pregões: {indicadores['retorno60']:.2%}

EMA 9: {indicadores['ema9']:.2f}
EMA 21: {indicadores['ema21']:.2f}
SMA 50: {indicadores['sma50']:.2f}
SMA 200: {indicadores['sma200']:.2f}

RSI 14: {indicadores['rsi14']:.2f}
MACD: {indicadores['macd']:.4f}
Sinal do MACD: {indicadores['macd_sinal']:.4f}
Histograma do MACD: {indicadores['macd_histograma']:.4f}

ATR 14: {indicadores['atr14']:.2f}
Volatilidade anualizada: {indicadores['volatilidade20']:.2%}

Volume atual: {indicadores['volume']:.0f}
Volume médio de 20 pregões: {indicadores['volume_medio20']:.0f}
Razão de volume: {indicadores['volume_ratio']:.2f}

Suporte de 20 pregões: R$ {indicadores['suporte20']:.2f}
Resistência de 20 pregões: R$ {indicadores['resistencia20']:.2f}

Preço de referência: {preco_referencia}
Stop técnico: {stop}
Alvo técnico: {alvo}
Relação risco-retorno: {risco_retorno}

Motivos:
{motivos}

Alertas:
{alertas}
"""


@app.get("/")
def index():
    return render_template(
        "index.html"
    )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "motor_sinal": "ativo",
    }, 200


@app.get("/historico")
def historico():
    ticker = (
        request.args
        .get("ticker", "")
        .strip()
        .upper()
        .removesuffix(".SA")
    )

    if ticker and not re.fullmatch(
        r"[A-Z0-9]{4,6}",
        ticker,
    ):
        ticker = ""

    analises = listar_analises(
        ticker=ticker or None,
        limite=200,
    )

    estatisticas = obter_estatisticas(
        ticker=ticker or None,
    )

    return render_template(
        "historico.html",
        analises=analises,
        estatisticas=estatisticas,
        ticker_filtro=ticker,
    )


@app.get("/historico/<int:analise_id>")
def historico_detalhe(
    analise_id: int,
):
    item = obter_analise(
        analise_id
    )

    if item is None:
        abort(404)

    anterior = obter_anterior(
        item["ticker"],
        item["id"],
    )

    comparacao = None

    if anterior is not None:
        preco_anterior = float(
            anterior["price"]
        )

        preco_atual = float(
            item["price"]
        )

        variacao_preco = (
            (
                preco_atual
                / preco_anterior
            )
            - 1
        ) * 100 if preco_anterior else 0.0

        comparacao = {
            "sinal_anterior": anterior[
                "signal"
            ],
            "mudou_sinal": (
                anterior["signal"]
                != item["signal"]
            ),
            "variacao_pontos": (
                int(item["score"])
                - int(anterior["score"])
            ),
            "variacao_preco_percentual": (
                variacao_preco
            ),
        }

    relatorio_html = markdown2.markdown(
        item["report_markdown"],
        extras=["tables"],
        safe_mode="escape",
    )

    return render_template(
        "historico_detalhe.html",
        item=item,
        anterior=anterior,
        comparacao=comparacao,
        relatorio_html=relatorio_html,
    )


@app.post("/gerar_relatorio")
def gerar_relatorio():
    inicio_total = time.perf_counter()

    ticker = (
        request.form
        .get("ticker", "")
        .strip()
        .upper()
    )

    import re

    ticker_pattern = re.compile(
        r"^[A-Z0-9]{4,6}(\.SA)?$"
    )

    if not ticker_pattern.fullmatch(
        ticker
    ):
        return render_template(
            "relatorio.html",
            error="Ticker inválido.",
        ), 400

    if not ticker.endswith(".SA"):
        ticker += ".SA"

    inicio_mercado = time.perf_counter()

    dados, erro = buscar_dados_ativo(
        ticker
    )

    logger.info(
        "Yahoo Finance %s: %.2fs",
        ticker,
        (
            time.perf_counter()
            - inicio_mercado
        ),
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

        analise = calcular_sinal_tecnico(
            indicadores
        )

        logger.info(
            (
                "Sinal %s: %s | "
                "pontos=%s | confiança=%s"
            ),
            ticker,
            analise["sinal"],
            analise["pontos"],
            analise["confianca"],
        )

        dados_ia = formatar_dados_para_ia(
            ticker,
            indicadores,
            analise,
        )

        prompt_base = (
            BASE_DIR
            / "prompt_analise.txt"
        ).read_text(
            encoding="utf-8"
        )

        prompt = prompt_base.replace(
            "{dados_do_ativo}",
            dados_ia,
        )

        inicio_ia = time.perf_counter()

        origem_relatorio = "Gemini"

        try:
            texto = gerar_relatorio_ia(
                prompt
            )

            logger.info(
                "Gemini %s: %.2fs",
                ticker,
               (
                    time.perf_counter()
                    - inicio_ia
                ),
            )

        except Exception as erro_ia:
            origem_relatorio = "motor local"

            logger.warning(
                (
                    "Gemini indisponível para %s. "
                    "Usando relatório local. "
                    "Erro: %s: %s"
                ),
                ticker,
                type(erro_ia).__name__,
                erro_ia,
            )

            texto = gerar_relatorio_local(
                ticker=ticker.removesuffix(
                    ".SA"
                ),
                indicadores=indicadores,
                analise=analise,
            )

        html = markdown2.markdown(
            texto,
            extras=["tables"],
            safe_mode="escape",
        )

        enviar_para_telegram(
            ticker.removesuffix(".SA"),
            analise["sinal"],
        )

        tempo_total = (
            time.perf_counter()
            - inicio_total
        )

        logger.info(
            "Análise total %s: %.2fs",
            ticker,
            tempo_total,
        )

        analise_id = None

        try:
            analise_id = salvar_analise(
                ticker=ticker.removesuffix(
                    ".SA"
                ),
                indicadores=indicadores,
                analise=analise,
                origem_relatorio=origem_relatorio,
                tempo_total=tempo_total,
                relatorio_markdown=texto,
            )

            logger.info(
                "Análise %s salva com ID %s",
                ticker,
                analise_id,
            )

        except Exception:
            logger.exception(
                "Falha ao salvar histórico de %s",
                ticker,
            )

        return render_template(
            "relatorio.html",
            relatorio=html,
            ticker=ticker.removesuffix(
                ".SA"
            ),
            analise=analise,
            indicadores=indicadores,
            tempo_total=tempo_total,
            origem_relatorio=origem_relatorio,
            analise_id=analise_id,
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
