import sqlite3
from config import DATABASE_FILE


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_FILE)
        self.create_tables()

    def create_tables(self):
        query = """
        CREATE TABLE IF NOT EXISTS groups (
            group_id INTEGER PRIMARY KEY,
            group_name TEXT,
            last_message_id INTEGER DEFAULT 0
        )
        """
        self.conn.execute(query)
        self.conn.commit()

    def get_last_message_id(self, group_id):
        cursor = self.conn.execute(
            "SELECT last_message_id FROM groups WHERE group_id=?",
            (group_id,)
        )
        row = cursor.fetchone()
        return row[0] if row else 0

    def update_last_message_id(self, group_id, group_name, message_id):
        self.conn.execute("""
            INSERT INTO groups (group_id, group_name, last_message_id)
            VALUES (?, ?, ?)
            ON CONFLICT(group_id)
            DO UPDATE SET last_message_id=excluded.last_message_id
        """, (group_id, group_name, message_id))
        self.conn.commit()
