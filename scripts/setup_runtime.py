"""Instala dependências e deixa o modelo local de embeddings em cache."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def main() -> None:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")]
    )
    from sentence_transformers import SentenceTransformer

    SentenceTransformer(MODEL)
    print(f"Dependências instaladas e modelo em cache: {MODEL}")


if __name__ == "__main__":
    main()
