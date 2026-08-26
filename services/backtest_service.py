from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from services.indicators_service import (
    calcular_indicadores,
)
from services.signal_service import (
    calcular_sinal_tecnico,
)


@dataclass(frozen=True)
class BacktestConfig:
    horizonte: int = 10
    warmup: int = 220
    incluir_neutro: bool = False


def _validar_config(
    config: BacktestConfig,
):
    if config.horizonte < 1:
        raise ValueError(
            "O horizonte deve ser maior que zero."
        )

    if config.warmup < 60:
        raise ValueError(
            "O warmup deve ter pelo menos 60 pregões."
        )


def _profit_factor(
    retornos: list[float],
) -> float | None:
    ganhos = sum(
        retorno
        for retorno in retornos
        if retorno > 0
    )

    perdas = abs(
        sum(
            retorno
            for retorno in retornos
            if retorno < 0
        )
    )

    if perdas == 0:
        # Evita Infinity no JSON e não atribui um
        # profit factor artificialmente "perfeito"
        # a amostras pequenas sem perdas observadas.
        return None

    return ganhos / perdas


def avaliar_sinais_historicos(
    df: pd.DataFrame,
    config: BacktestConfig | None = None,
) -> dict:
    """
    Avalia o viés direcional do motor sem look-ahead.

    O sinal é calculado apenas com dados disponíveis até
    o fechamento da barra t. A entrada de referência é a
    abertura de t+1 (ou o fechamento, quando Open não existe)
    e a saída é o fechamento após `horizonte` pregões.

    Isso NÃO simula execução de stop/alvo nem custos. A métrica
    mede a capacidade direcional do sinal, não o P&L de uma
    estratégia pronta para produção.
    """
    config = config or BacktestConfig()
    _validar_config(config)

    if "Close" not in df.columns:
        raise ValueError(
            "A coluna Close é obrigatória."
        )

    minimo = (
        config.warmup
        + config.horizonte
        + 1
    )

    if len(df) < minimo:
        raise ValueError(
            "Histórico insuficiente para backtest: "
            f"são necessários pelo menos {minimo} pregões."
        )

    dados = df.copy()

    fechamento = pd.to_numeric(
        dados["Close"],
        errors="coerce",
    )

    if "Open" in dados.columns:
        abertura = pd.to_numeric(
            dados["Open"],
            errors="coerce",
        )
    else:
        abertura = fechamento.copy()

    eventos: list[dict] = []
    sinal_anterior = "NEUTRO"

    ultimo_indice_sinal = (
        len(dados)
        - config.horizonte
        - 1
    )

    for i in range(
        config.warmup - 1,
        ultimo_indice_sinal + 1,
    ):
        janela = dados.iloc[
            : i + 1
        ]

        indicadores = (
            calcular_indicadores(
                janela
            )
        )

        analise = (
            calcular_sinal_tecnico(
                indicadores
            )
        )

        sinal = analise["sinal"]

        mudou = (
            sinal != sinal_anterior
        )

        registrar = (
            mudou
            and (
                config.incluir_neutro
                or sinal != "NEUTRO"
            )
        )

        if registrar:
            entrada_idx = i + 1
            saida_idx = (
                entrada_idx
                + config.horizonte
                - 1
            )

            preco_entrada = (
                abertura.iloc[
                    entrada_idx
                ]
            )

            if pd.isna(preco_entrada):
                preco_entrada = (
                    fechamento.iloc[
                        entrada_idx
                    ]
                )

            preco_saida = (
                fechamento.iloc[
                    saida_idx
                ]
            )

            if (
                not pd.isna(
                    preco_entrada
                )
                and not pd.isna(
                    preco_saida
                )
                and float(
                    preco_entrada
                ) > 0
            ):
                retorno_ativo = (
                    float(preco_saida)
                    / float(preco_entrada)
                    - 1
                )

                if sinal == "COMPRA":
                    retorno_direcional = (
                        retorno_ativo
                    )
                elif sinal == "VENDA":
                    retorno_direcional = (
                        -retorno_ativo
                    )
                else:
                    retorno_direcional = 0.0

                eventos.append(
                    {
                        "data_sinal": (
                            str(
                                dados.index[i]
                            )
                        ),
                        "data_entrada": (
                            str(
                                dados.index[
                                    entrada_idx
                                ]
                            )
                        ),
                        "data_saida": (
                            str(
                                dados.index[
                                    saida_idx
                                ]
                            )
                        ),
                        "sinal": sinal,
                        "pontos": int(
                            analise[
                                "pontos"
                            ]
                        ),
                        "forca_percentual": float(
                            analise.get(
                                "forca_percentual",
                                0,
                            )
                        ),
                        "preco_entrada": float(
                            preco_entrada
                        ),
                        "preco_saida": float(
                            preco_saida
                        ),
                        "retorno_ativo": float(
                            retorno_ativo
                        ),
                        "retorno_direcional": float(
                            retorno_direcional
                        ),
                        "acerto": bool(
                            retorno_direcional
                            > 0
                        ),
                    }
                )

        sinal_anterior = sinal

    retornos = [
        evento[
            "retorno_direcional"
        ]
        for evento in eventos
        if evento["sinal"]
        != "NEUTRO"
    ]

    total = len(retornos)

    if total:
        taxa_acerto = (
            sum(
                retorno > 0
                for retorno in retornos
            )
            / total
        )

        retorno_medio = float(
            np.mean(retornos)
        )

        retorno_mediano = float(
            np.median(retornos)
        )

        desvio = float(
            np.std(
                retornos,
                ddof=1,
            )
        ) if total > 1 else 0.0
    else:
        taxa_acerto = 0.0
        retorno_medio = 0.0
        retorno_mediano = 0.0
        desvio = 0.0

    profit_factor = (
        _profit_factor(retornos)
    )

    return {
        "metodologia": (
            "Sinal no fechamento; entrada de referência "
            "na abertura seguinte; saída no fechamento "
            f"após {config.horizonte} pregões. "
            "Sem stop, alvo, custos ou slippage."
        ),
        "horizonte": (
            config.horizonte
        ),
        "warmup": config.warmup,
        "total_sinais": total,
        "compras": sum(
            evento["sinal"]
            == "COMPRA"
            for evento in eventos
        ),
        "vendas": sum(
            evento["sinal"]
            == "VENDA"
            for evento in eventos
        ),
        "taxa_acerto": (
            taxa_acerto
        ),
        "retorno_medio_direcional": (
            retorno_medio
        ),
        "retorno_mediano_direcional": (
            retorno_mediano
        ),
        "desvio_retorno_direcional": (
            desvio
        ),
        "profit_factor": (
            profit_factor
        ),
        "eventos": eventos,
    }
