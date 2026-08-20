"""Operações locais de retenção, backup e inspeção do GeoAI Mentor."""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parents[1]
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from dotenv import load_dotenv

from geoai_mentor.infrastructure.sqlite_repository import SQLiteConversationRepository


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("acao", choices=("status", "backup", "retencao"))
    parser.add_argument(
        "--database",
        default=os.getenv("GEOAI_DATABASE_PATH", "data/geoai_mentor.db"),
    )
    parser.add_argument(
        "--dias",
        type=int,
        default=int(os.getenv("GEOAI_RETENTION_DAYS", "90")),
    )
    parser.add_argument("--destino", default="backups")
    args = parser.parse_args()

    repository = SQLiteConversationRepository(args.database)
    try:
        if args.acao == "status":
            print(f"Conversas persistidas: {len(repository.listar_conversas())}")
        elif args.acao == "retencao":
            if args.dias <= 0:
                parser.error("--dias deve ser maior que zero")
            limite = datetime.now(timezone.utc) - timedelta(days=args.dias)
            print(f"Conversas expiradas: {repository.expirar_conversas(limite)}")
        else:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            destino = Path(args.destino) / f"geoai_mentor_{timestamp}.db"
            print(f"Backup criado: {repository.criar_backup(str(destino))}")
    finally:
        repository.fechar()


if __name__ == "__main__":
    main()
