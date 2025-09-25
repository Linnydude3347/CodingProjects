import csv
import json
import os
import sqlite3
from typing import Dict, Iterable, List

DEFAULT_FIELDS = [
    "id","created_at","text","lang","author_id","author_username","author_name","author_verified",
    "like_count","retweet_count","reply_count","quote_count","source","hashtags","is_retweet","is_reply","is_quote",
    "conversation_id","in_reply_to_user_id"
]

def to_jsonl(path: str, rows: Iterable[Dict], ensure_ascii: bool=False):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=ensure_ascii, default=str) + "\n")

def to_csv(path: str, rows: Iterable[Dict], fields: List[str] = None):
    fields = fields or DEFAULT_FIELDS
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    file_exists = os.path.exists(path)
    with open(path, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        for r in rows:
            writer.writerow({k: (str(v) if v is not None else "") for k, v in r.items()})

def to_sqlite(path: str, table: str, rows: Iterable[Dict]):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {table} (
            id TEXT PRIMARY KEY,
            created_at TEXT,
            text TEXT,
            lang TEXT,
            author_id TEXT,
            author_username TEXT,
            author_name TEXT,
            author_verified INTEGER,
            like_count INTEGER,
            retweet_count INTEGER,
            reply_count INTEGER,
            quote_count INTEGER,
            source TEXT,
            hashtags TEXT,
            is_retweet INTEGER,
            is_reply INTEGER,
            is_quote INTEGER,
            conversation_id TEXT,
            in_reply_to_user_id TEXT
        )
    """)
    to_insert = []
    for r in rows:
        to_insert.append((
            r.get("id"), str(r.get("created_at") or ""), r.get("text"),
            r.get("lang"), str(r.get("author_id") or ""), r.get("author_username"),
            r.get("author_name"), 1 if r.get("author_verified") else 0,
            r.get("like_count"), r.get("retweet_count"),
            r.get("reply_count"), r.get("quote_count"),
            r.get("source"), r.get("hashtags"),
            1 if r.get("is_retweet") else 0,
            1 if r.get("is_reply") else 0,
            1 if r.get("is_quote") else 0,
            str(r.get("conversation_id") or ""), str(r.get("in_reply_to_user_id") or ""),
        ))
    cur.executemany(f"""
        INSERT OR IGNORE INTO {table} (
            id, created_at, text, lang, author_id, author_username, author_name, author_verified,
            like_count, retweet_count, reply_count, quote_count, source, hashtags,
            is_retweet, is_reply, is_quote, conversation_id, in_reply_to_user_id
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, to_insert)
    conn.commit()
    conn.close()