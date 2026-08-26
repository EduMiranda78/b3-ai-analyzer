#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(
    __file__
).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(ROOT_DIR),
    )

from services.backtest_service import (  # noqa: E402
    BacktestConfig,
    avaliar_sinais_historicos,
)
from services.market_service import (  # noqa: E402
    buscar_dados_ativo,
)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Avalia historicamente o viés direcional "
            "do motor técnico sem look-ahead."
        )
    )

    parser.add_argument(
        "ticker",
        help="Ticker B3, por exemplo PETR4",
    )

    parser.add_argument(
        "--period",
        default="5y",
        help="Período aceito pelo yfinance (padrão: 5y)",
    )

    parser.add_argument(
        "--horizon",
        type=int,
        default=10,
        help="Horizonte em pregões (padrão: 10)",
    )

    parser.add_argument(
        "--warmup",
        type=int,
        default=220,
        help="Pregões antes do primeiro sinal (padrão: 220)",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Exibe o resultado completo em JSON.",
    )

    args = parser.parse_args()

    ticker = (
        args.ticker
        .strip()
        .upper()
    )

    if not ticker.endswith(".SA"):
        ticker += ".SA"

    dados, erro = buscar_dados_ativo(
        ticker,
        period=args.period,
    )

    if erro:
        raise SystemExit(erro)

    resultado = avaliar_sinais_historicos(
        dados["historico"],
        BacktestConfig(
            horizonte=args.horizon,
            warmup=args.warmup,
        ),
    )

    if args.json:
        print(
            json.dumps(
                resultado,
                ensure_ascii=False,
                indent=2,
                allow_nan=False,
            )
        )
        return

    pf = resultado["profit_factor"]

    if pf is None:
        pf_texto = "n/d"
    else:
        pf_texto = f"{pf:.2f}"

    print(
        f"Ticker: {ticker.removesuffix('.SA')}"
    )
    print(
        f"Sinais avaliados: {resultado['total_sinais']}"
    )
    print(
        "Taxa de acerto: "
        f"{resultado['taxa_acerto']:.1%}"
    )
    print(
        "Retorno direcional médio: "
        f"{resultado['retorno_medio_direcional']:.2%}"
    )
    print(
        "Retorno direcional mediano: "
        f"{resultado['retorno_mediano_direcional']:.2%}"
    )
    print(
        f"Profit factor: {pf_texto}"
    )
    print()
    print(resultado["metodologia"])


if __name__ == "__main__":
    main()
