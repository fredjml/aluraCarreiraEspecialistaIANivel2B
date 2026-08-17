"""Persistência transacional de conversas em SQLite."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock

from geoai_mentor.domain.models import Conversation, Message


class SQLiteConversationRepository:
    """Implementa o repositório de conversas usando somente a biblioteca padrão."""

    def __init__(self, database_path: str) -> None:
        if database_path != ":memory:":
            Path(database_path).expanduser().resolve().parent.mkdir(
                parents=True, exist_ok=True
            )
        self._lock = RLock()
        self._connection = sqlite3.connect(
            database_path,
            check_same_thread=False,
        )
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._criar_schema()

    def _criar_schema(self) -> None:
        with self._lock, self._connection:
            self._connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL DEFAULT 'Nova conversa',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (conversation_id)
                        REFERENCES conversations(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_messages_conversation
                    ON messages(conversation_id, id);
                """
            )
            colunas = {
                row["name"]
                for row in self._connection.execute("PRAGMA table_info(conversations)")
            }
            if "title" not in colunas:
                self._connection.execute(
                    "ALTER TABLE conversations ADD COLUMN title TEXT NOT NULL DEFAULT 'Nova conversa'"
                )

    def criar_conversa(self, conversation_id: str, title: str) -> Conversation:
        agora = datetime.now(timezone.utc)
        with self._lock, self._connection:
            self._connection.execute(
                """
                INSERT INTO conversations(id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (conversation_id, title, agora.isoformat(), agora.isoformat()),
            )
        return Conversation(conversation_id, title, agora, agora)

    def listar_conversas(self) -> list[Conversation]:
        with self._lock:
            rows = self._connection.execute(
                """
                SELECT id, title, created_at, updated_at
                FROM conversations ORDER BY updated_at DESC
                """
            ).fetchall()
        return [
            Conversation(
                id=row["id"],
                title=row["title"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )
            for row in rows
        ]

    def renomear_conversa(self, conversation_id: str, title: str) -> None:
        agora = datetime.now(timezone.utc).isoformat()
        with self._lock, self._connection:
            cursor = self._connection.execute(
                "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?",
                (title, agora, conversation_id),
            )
            if cursor.rowcount == 0:
                raise KeyError(f"Conversa não encontrada: {conversation_id}")

    def listar_mensagens(self, conversation_id: str) -> list[Message]:
        """Lista mensagens na mesma ordem em que foram persistidas."""
        with self._lock:
            rows = self._connection.execute(
                """
                SELECT role, content, created_at
                FROM messages
                WHERE conversation_id = ?
                ORDER BY id
                """,
                (conversation_id,),
            ).fetchall()
        return [
            Message(
                role=row["role"],
                content=row["content"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )
            for row in rows
        ]

    def salvar_interacao(
        self,
        conversation_id: str,
        pergunta: str,
        resposta: str,
    ) -> None:
        """Grava pergunta e resposta na mesma transação."""
        agora = datetime.now(timezone.utc).isoformat()
        with self._lock, self._connection:
            self._connection.execute(
                """
                INSERT INTO conversations(id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET updated_at = excluded.updated_at
                """,
                (conversation_id, pergunta[:60], agora, agora),
            )
            self._connection.executemany(
                """
                INSERT INTO messages(conversation_id, role, content, created_at)
                VALUES (?, ?, ?, ?)
                """,
                [
                    (conversation_id, "user", pergunta, agora),
                    (conversation_id, "assistant", resposta, agora),
                ],
            )

    def limpar_conversa(self, conversation_id: str) -> None:
        """Exclui a conversa e suas mensagens por cascata."""
        with self._lock, self._connection:
            self._connection.execute(
                "DELETE FROM conversations WHERE id = ?",
                (conversation_id,),
            )

    def expirar_conversas(self, antes_de: datetime) -> int:
        """Exclui conversas anteriores ao limite de retenção informado."""
        with self._lock, self._connection:
            cursor = self._connection.execute(
                "DELETE FROM conversations WHERE updated_at < ?",
                (antes_de.isoformat(),),
            )
        return cursor.rowcount

    def criar_backup(self, destination_path: str) -> str:
        """Cria uma cópia consistente usando a API de backup do SQLite."""
        destination = Path(destination_path).expanduser().resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        backup_connection = sqlite3.connect(destination)
        try:
            with self._lock:
                self._connection.backup(backup_connection)
        finally:
            backup_connection.close()
        return str(destination)

    def fechar(self) -> None:
        """Fecha explicitamente a conexão quando o ciclo de vida exigir."""
        with self._lock:
            self._connection.close()
