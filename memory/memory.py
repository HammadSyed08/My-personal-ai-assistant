import sqlite3
import os


class MemoryManager:

    def __init__(self, db_path="data/memory.db"):

        # Make sure the data folder exists
        os.makedirs(
            os.path.dirname(db_path),
            exist_ok=True
        )

        self.db_path = db_path

        self._create_table()

    def _connect(self):

        return sqlite3.connect(
            self.db_path
        )

    def _create_table(self):

        connection = self._connect()
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory TEXT NOT NULL
            )
        """)

        connection.commit()
        connection.close()

    def remember(self, text):

        if not text:
            return False

        connection = self._connect()
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO memories (memory) VALUES (?)",
            (text,)
        )

        connection.commit()
        connection.close()

        return True


    def recall(self):

        connection = self._connect()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT id, memory FROM memories ORDER BY id"
        )

        memories = cursor.fetchall()

        connection.close()

        return memories

    def forget(self, memory_id):

        connection = self._connect()
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM memories WHERE id = ?",
            (memory_id,)
        )

        connection.commit()

        deleted = cursor.rowcount > 0

        connection.close()

        return deleted

    def search(self, keyword):

        if not keyword:
            return []

        connection = self._connect()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, memory
            FROM memories
            WHERE memory LIKE ?
            ORDER BY id
            """,
            (f"%{keyword}%",)
        )

        results = cursor.fetchall()

        connection.close()

        return results




memory = MemoryManager()

