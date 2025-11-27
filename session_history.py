"""
Session History Database (SQLite)
Хранение истории сессий для аналитики и восстановления
"""
import sqlite3
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class SessionHistoryDB:
    """SQLite база для хранения истории сессий"""

    def __init__(self, db_path: str = "data/sessions.db"):
        """
        Args:
            db_path: Путь к SQLite файлу
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_db()
        logger.info(f"✅ Session History DB initialized: {db_path}")

    def _init_db(self):
        """Создать таблицы если их нет"""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()

            # Таблица сессий
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS sessions
                           (
                               session_id
                               TEXT
                               PRIMARY
                               KEY,
                               doc_type
                               TEXT,
                               status
                               TEXT,
                               progress
                               REAL,
                               created_at
                               TIMESTAMP,
                               updated_at
                               TIMESTAMP,
                               document_path
                               TEXT,
                               metadata
                               TEXT
                           )
                           """)

            # Таблица сообщений
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS messages
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               session_id
                               TEXT,
                               role
                               TEXT,
                               content
                               TEXT,
                               timestamp
                               TIMESTAMP,
                               FOREIGN
                               KEY
                           (
                               session_id
                           ) REFERENCES sessions
                           (
                               session_id
                           )
                               )
                           """)

            # Индексы
            cursor.execute("""
                           CREATE INDEX IF NOT EXISTS idx_session_id
                               ON messages (session_id)
                           """)

            cursor.execute("""
                           CREATE INDEX IF NOT EXISTS idx_created_at
                               ON sessions (created_at)
                           """)

            conn.commit()

    def create_session(
            self,
            session_id: str,
            doc_type: Optional[str] = None,
            metadata: Optional[Dict] = None
    ):
        """Создать новую сессию"""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()

            now = datetime.utcnow().isoformat()

            cursor.execute("""
                INSERT OR REPLACE INTO sessions 
                (session_id, doc_type, status, progress, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                doc_type,
                "active",
                0.0,
                now,
                now,
                json.dumps(metadata or {})
            ))

            conn.commit()

    def add_message(
            self,
            session_id: str,
            role: str,
            content: str
    ):
        """Добавить сообщение в историю"""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                           INSERT INTO messages (session_id, role, content, timestamp)
                           VALUES (?, ?, ?, ?)
                           """, (
                               session_id,
                               role,
                               content,
                               datetime.now()
                           ))

            # Обновляем timestamp сессии
            cursor.execute("""
                           UPDATE sessions
                           SET updated_at = ?
                           WHERE session_id = ?
                           """, (datetime.now(), session_id))

            conn.commit()

    def update_session(
            self,
            session_id: str,
            **kwargs
    ):
        """Обновить сессию"""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()

            fields = []
            values = []

            for key, value in kwargs.items():
                if key == "metadata":
                    value = json.dumps(value)
                fields.append(f"{key} = ?")
                values.append(value)

            fields.append("updated_at = ?")
            values.append(datetime.utcnow().isoformat())

            values.append(session_id)

            query = f"""
                UPDATE sessions 
                SET {', '.join(fields)}
                WHERE session_id = ?
            """

            cursor.execute(query, values)
            conn.commit()

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Получить информацию о сессии"""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                           SELECT *
                           FROM sessions
                           WHERE session_id = ?
                           """, (session_id,))

            row = cursor.fetchone()

            if row:
                data = dict(row)
                if data.get("metadata"):
                    data["metadata"] = json.loads(data["metadata"])
                return data

            return None

    def get_session_messages(
            self,
            session_id: str,
            limit: Optional[int] = None
    ) -> List[Dict]:
        """Получить историю сообщений сессии"""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = """
                    SELECT * \
                    FROM messages
                    WHERE session_id = ?
                    ORDER BY timestamp ASC \
                    """

            if limit:
                query += f" LIMIT {limit}"

            cursor.execute(query, (session_id,))

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def list_sessions(
            self,
            limit: int = 50,
            status: Optional[str] = None
    ) -> List[Dict]:
        """Список сессий"""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = "SELECT * FROM sessions"
            params = []

            if status:
                query += " WHERE status = ?"
                params.append(status)

            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_statistics(self) -> Dict:
        """Статистика по сессиям"""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()

            # Общее количество сессий
            cursor.execute("SELECT COUNT(*) FROM sessions")
            total_sessions = cursor.fetchone()[0]

            # Количество по типам документов
            cursor.execute("""
                           SELECT doc_type, COUNT(*) as count
                           FROM sessions
                           WHERE doc_type IS NOT NULL
                           GROUP BY doc_type
                           """)
            by_doc_type = {row[0]: row[1] for row in cursor.fetchall()}

            # Активные сессии
            cursor.execute("""
                           SELECT COUNT(*)
                           FROM sessions
                           WHERE status = 'active'
                           """)
            active_sessions = cursor.fetchone()[0]

            # Завершенные сессии (progress >= 1.0)
            cursor.execute("""
                           SELECT COUNT(*)
                           FROM sessions
                           WHERE progress >= 1.0
                           """)
            completed_sessions = cursor.fetchone()[0]

            # Общее количество сообщений
            cursor.execute("SELECT COUNT(*) FROM messages")
            total_messages = cursor.fetchone()[0]

            return {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "completed_sessions": completed_sessions,
                "total_messages": total_messages,
                "by_doc_type": by_doc_type
            }

    def delete_session(self, session_id: str):
        """Удалить сессию и все её сообщения"""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()

            cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))

            conn.commit()

    def cleanup_old_sessions(self, days: int = 30):
        """Удалить старые сессии"""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()

            cutoff = datetime.now().timestamp() - (days * 24 * 3600)

            cursor.execute("""
                           DELETE
                           FROM messages
                           WHERE session_id IN (SELECT session_id
                                                FROM sessions
                                                WHERE updated_at < datetime(?, 'unixepoch'))
                           """, (cutoff,))

            cursor.execute("""
                           DELETE
                           FROM sessions
                           WHERE updated_at < datetime(?, 'unixepoch')
                           """, (cutoff,))

            deleted = cursor.rowcount
            conn.commit()

            return deleted


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Тест
    db = SessionHistoryDB("test_sessions.db")

    session_id = "test-123"

    # Создать сессию
    db.create_session(session_id, doc_type="new_feature")

    # Добавить сообщения
    db.add_message(session_id, "user", "Хочу добавить фичу")
    db.add_message(session_id, "assistant", "Расскажите подробнее")

    # Обновить прогресс
    db.update_session(session_id, progress=0.5, status="processing")

    # Получить историю
    messages = db.get_session_messages(session_id)
    print(f"Messages: {len(messages)}")

    # Статистика
    stats = db.get_statistics()
    print(f"Stats: {stats}")