import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


BASE_DIR = Path(__file__).resolve().parent.parent
TIMEZONE = ZoneInfo("America/Sao_Paulo")


def _caminho_banco() -> Path:
    caminho_configurado = os.getenv(
        "ANALISADOR_DB_PATH"
    )

    if caminho_configurado:
        return Path(
            caminho_configurado
        ).expanduser().resolve()

    return (
        BASE_DIR
        / "instance"
        / "analisador.db"
    )


def _conectar():
    caminho = _caminho_banco()

    caminho.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    conexao = sqlite3.connect(
        caminho,
        timeout=10,
    )

    conexao.row_factory = sqlite3.Row

    conexao.execute(
        "PRAGMA journal_mode=WAL"
    )

    conexao.execute(
        "PRAGMA foreign_keys=ON"
    )

    return conexao


def inicializar_banco():
    with _conectar() as conexao:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                ticker TEXT NOT NULL,
                signal TEXT NOT NULL,
                score INTEGER NOT NULL,
                confidence TEXT NOT NULL,
                price REAL NOT NULL,
                reference_price REAL,
                stop_price REAL,
                target_price REAL,
                risk_reward REAL,
                report_source TEXT NOT NULL,
                duration_seconds REAL NOT NULL,
                indicators_json TEXT NOT NULL,
                analysis_json TEXT NOT NULL,
                report_markdown TEXT NOT NULL,
                schema_version INTEGER NOT NULL DEFAULT 1
            )
            """
        )

        conexao.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_analyses_ticker_id
            ON analyses (
                ticker,
                id DESC
            )
            """
        )

        conexao.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_analyses_created_at
            ON analyses (
                created_at DESC
            )
            """
        )

        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS shadow_v31 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                analysis_id INTEGER,
                market_date TEXT NOT NULL,
                ticker TEXT NOT NULL,
                version TEXT NOT NULL,
                legacy_signal TEXT NOT NULL,
                shadow_signal TEXT NOT NULL,
                shadow_state TEXT NOT NULL,
                price REAL NOT NULL,
                benchmark_ticker TEXT NOT NULL,
                benchmark_market_date TEXT,
                result_json TEXT NOT NULL,
                UNIQUE (ticker, market_date, version)
            )
            """
        )

        conexao.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_shadow_v31_ticker_date
            ON shadow_v31 (
                ticker,
                market_date DESC
            )
            """
        )

        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS shadow_v31_outcomes (
                shadow_id INTEGER NOT NULL,
                horizon INTEGER NOT NULL,
                evaluated_at TEXT NOT NULL,
                entry_date TEXT NOT NULL,
                exit_date TEXT NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL NOT NULL,
                asset_return REAL NOT NULL,
                benchmark_return REAL,
                excess_return REAL,
                PRIMARY KEY (shadow_id, horizon),
                FOREIGN KEY (shadow_id) REFERENCES shadow_v31(id)
                    ON DELETE CASCADE
            )
            """
        )


def salvar_analise(
    *,
    ticker: str,
    indicadores: dict,
    analise: dict,
    origem_relatorio: str,
    tempo_total: float,
    relatorio_markdown: str,
) -> int:
    inicializar_banco()

    criado_em = datetime.now(
        TIMEZONE
    ).isoformat(
        timespec="seconds"
    )

    indicadores_json = json.dumps(
        indicadores,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
    )

    analise_json = json.dumps(
        analise,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
    )

    with _conectar() as conexao:
        cursor = conexao.execute(
            """
            INSERT INTO analyses (
                created_at,
                ticker,
                signal,
                score,
                confidence,
                price,
                reference_price,
                stop_price,
                target_price,
                risk_reward,
                report_source,
                duration_seconds,
                indicators_json,
                analysis_json,
                report_markdown
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                criado_em,
                ticker,
                analise["sinal"],
                int(analise["pontos"]),
                analise["confianca"],
                float(indicadores["preco"]),
                analise.get(
                    "preco_referencia"
                ),
                analise.get("stop"),
                analise.get("alvo"),
                analise.get(
                    "risco_retorno"
                ),
                origem_relatorio,
                float(tempo_total),
                indicadores_json,
                analise_json,
                relatorio_markdown,
            ),
        )

        return int(
            cursor.lastrowid
        )


def listar_analises(
    ticker: str | None = None,
    limite: int = 100,
) -> list[dict]:
    inicializar_banco()

    limite = max(
        1,
        min(int(limite), 500),
    )

    parametros = []

    sql = """
        SELECT
            id,
            created_at,
            ticker,
            signal,
            score,
            confidence,
            price,
            reference_price,
            stop_price,
            target_price,
            risk_reward,
            report_source,
            duration_seconds
        FROM analyses
    """

    if ticker:
        sql += " WHERE ticker = ?"
        parametros.append(
            ticker.upper()
        )

    sql += " ORDER BY id DESC LIMIT ?"
    parametros.append(limite)

    with _conectar() as conexao:
        linhas = conexao.execute(
            sql,
            parametros,
        ).fetchall()

    return [
        dict(linha)
        for linha in linhas
    ]


def obter_analise(
    analise_id: int,
) -> dict | None:
    inicializar_banco()

    with _conectar() as conexao:
        linha = conexao.execute(
            """
            SELECT *
            FROM analyses
            WHERE id = ?
            """,
            (int(analise_id),),
        ).fetchone()

    if linha is None:
        return None

    resultado = dict(linha)

    resultado["indicadores"] = json.loads(
        resultado.pop(
            "indicators_json"
        )
    )

    resultado["analise"] = json.loads(
        resultado.pop(
            "analysis_json"
        )
    )

    return resultado


def obter_anterior(
    ticker: str,
    analise_id: int,
) -> dict | None:
    inicializar_banco()

    with _conectar() as conexao:
        linha = conexao.execute(
            """
            SELECT
                id,
                created_at,
                ticker,
                signal,
                score,
                confidence,
                price,
                reference_price,
                stop_price,
                target_price,
                risk_reward,
                report_source,
                duration_seconds
            FROM analyses
            WHERE ticker = ?
              AND id < ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                ticker.upper(),
                int(analise_id),
            ),
        ).fetchone()

    return (
        dict(linha)
        if linha is not None
        else None
    )


def obter_estatisticas(
    ticker: str | None = None,
) -> dict:
    inicializar_banco()

    parametros = []

    filtro = ""

    if ticker:
        filtro = "WHERE ticker = ?"
        parametros.append(
            ticker.upper()
        )

    with _conectar() as conexao:
        resumo = conexao.execute(
            f"""
            SELECT
                COUNT(*) AS total,
                SUM(
                    CASE
                        WHEN signal = 'COMPRA'
                        THEN 1 ELSE 0
                    END
                ) AS compras,
                SUM(
                    CASE
                        WHEN signal = 'VENDA'
                        THEN 1 ELSE 0
                    END
                ) AS vendas,
                SUM(
                    CASE
                        WHEN signal = 'NEUTRO'
                        THEN 1 ELSE 0
                    END
                ) AS neutros,
                COUNT(
                    DISTINCT ticker
                ) AS tickers
            FROM analyses
            {filtro}
            """,
            parametros,
        ).fetchone()

    return {
        chave: int(
            resumo[chave] or 0
        )
        for chave in (
            "total",
            "compras",
            "vendas",
            "neutros",
            "tickers",
        )
    }



def salvar_shadow_v31(
    *,
    ticker: str,
    analysis_id: int | None,
    market_date: str,
    legacy_signal: str,
    resultado: dict,
    benchmark_ticker: str = "BOVA11",
    benchmark_market_date: str | None = None,
) -> int:
    inicializar_banco()

    criado_em = datetime.now(
        TIMEZONE
    ).isoformat(
        timespec="seconds"
    )

    resultado_json = json.dumps(
        resultado,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
    )

    with _conectar() as conexao:
        conexao.execute(
            """
            INSERT INTO shadow_v31 (
                created_at,
                analysis_id,
                market_date,
                ticker,
                version,
                legacy_signal,
                shadow_signal,
                shadow_state,
                price,
                benchmark_ticker,
                benchmark_market_date,
                result_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (ticker, market_date, version)
            DO UPDATE SET
                created_at = excluded.created_at,
                analysis_id = excluded.analysis_id,
                legacy_signal = excluded.legacy_signal,
                shadow_signal = excluded.shadow_signal,
                shadow_state = excluded.shadow_state,
                price = excluded.price,
                benchmark_ticker = excluded.benchmark_ticker,
                benchmark_market_date = excluded.benchmark_market_date,
                result_json = excluded.result_json
            """,
            (
                criado_em,
                analysis_id,
                market_date,
                ticker.upper().removesuffix(".SA"),
                resultado["versao"],
                legacy_signal,
                resultado["sinal"],
                resultado["estado"],
                float(resultado["preco"]),
                benchmark_ticker.upper().removesuffix(".SA"),
                benchmark_market_date,
                resultado_json,
            ),
        )

        linha = conexao.execute(
            """
            SELECT id
            FROM shadow_v31
            WHERE ticker = ?
              AND market_date = ?
              AND version = ?
            """,
            (
                ticker.upper().removesuffix(".SA"),
                market_date,
                resultado["versao"],
            ),
        ).fetchone()

    return int(linha["id"])


def listar_shadow_v31(
    *,
    ticker: str | None = None,
    limite: int = 100,
) -> list[dict]:
    inicializar_banco()

    limite = max(1, min(int(limite), 1000))
    parametros: list = []

    sql = """
        SELECT
            id,
            created_at,
            analysis_id,
            market_date,
            ticker,
            version,
            legacy_signal,
            shadow_signal,
            shadow_state,
            price,
            benchmark_ticker,
            benchmark_market_date,
            result_json
        FROM shadow_v31
    """

    if ticker:
        sql += " WHERE ticker = ?"
        parametros.append(
            ticker.upper().removesuffix(".SA")
        )

    sql += " ORDER BY market_date DESC, id DESC LIMIT ?"
    parametros.append(limite)

    with _conectar() as conexao:
        linhas = conexao.execute(
            sql,
            parametros,
        ).fetchall()

    resultado = []
    for linha in linhas:
        item = dict(linha)
        item["resultado"] = json.loads(
            item.pop("result_json")
        )
        resultado.append(item)

    return resultado
