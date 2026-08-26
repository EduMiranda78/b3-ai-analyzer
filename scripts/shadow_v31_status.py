#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from services.history_service import listar_shadow_v31


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Lista as leituras registradas pelo Motor V3.1 em shadow mode."
    )
    parser.add_argument("--ticker", default=None)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    itens = listar_shadow_v31(
        ticker=args.ticker,
        limite=args.limit,
    )

    if not itens:
        print("Nenhum registro do Shadow V3.1 ainda.")
        return 0

    print(
        "DATA       TICKER  LEGADO  V3.1     ESTADO    MERCADO  PREÇO"
    )
    print("-" * 72)

    for item in itens:
        r = item["resultado"]
        print(
            f"{item['market_date']:<10} "
            f"{item['ticker']:<7} "
            f"{item['legacy_signal']:<7} "
            f"{item['shadow_signal']:<8} "
            f"{item['shadow_state']:<9} "
            f"{r.get('regime_mercado', 'N/D'):<8} "
            f"{item['price']:.2f}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
