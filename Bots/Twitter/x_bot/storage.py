from __future__ import annotations
import os, sqlite3, time

class StateDB:
    def __init__(self, path: str = "data/state.db"):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self.conn = sqlite3.connect(path)
        self._ensure()

    def _ensure(self):
        cur = self.conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, val TEXT)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS seen (id TEXT PRIMARY KEY, ts REAL)""")
        self.conn.commit()

    def get(self, key: str) -> str | None:
        cur = self.conn.cursor()
        cur.execute("SELECT val FROM kv WHERE key=?", (key,))
        r = cur.fetchone()
        return r[0] if r else None

    def set(self, key: str, val: str):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO kv(key,val) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET val=excluded.val", (key,val))
        self.conn.commit()

    def seen(self, _id: str) -> bool:
        cur = self.conn.cursor()
        cur.execute("SELECT 1 FROM seen WHERE id=?", (_id,))
        return cur.fetchone() is not None

    def mark(self, _id: str):
        cur = self.conn.cursor()
        cur.execute("INSERT OR IGNORE INTO seen(id,ts) VALUES(?,?)", (_id, time.time()))
        self.conn.commit()

    def close(self):
        try: self.conn.close()
        except Exception: pass