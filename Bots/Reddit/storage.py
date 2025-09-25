from __future__ import annotations
import os, sqlite3, time

class SeenStore:
    def __init__(self, path: str = "data/seen.db"):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self.conn = sqlite3.connect(path)
        self._ensure()

    def _ensure(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS seen (
                id TEXT PRIMARY KEY,
                kind TEXT,
                ts REAL
            )
        """)
        self.conn.commit()

    def seen(self, _id: str) -> bool:
        cur = self.conn.cursor()
        cur.execute("SELECT 1 FROM seen WHERE id=?", (_id,))
        return cur.fetchone() is not None

    def mark(self, _id: str, kind: str):
        cur = self.conn.cursor()
        cur.execute("INSERT OR IGNORE INTO seen (id, kind, ts) VALUES (?,?,?)", (_id, kind, time.time()))
        self.conn.commit()

    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass