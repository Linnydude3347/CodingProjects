from __future__ import annotations
import os
from dataclasses import dataclass
from typing import List
from dotenv import load_dotenv

load_dotenv()

def _split_csv(val: str | None) -> list[str]:
    if not val: return []
    return [p.strip() for p in val.split(',') if p.strip()]

@dataclass
class Settings:
    client_id: str
    client_secret: str
    user_agent: str
    username: str
    password: str
    subreddits: List[str]
    keywords: List[str]
    reply_template: str
    dry_run: bool = True
    max_items: int = 200

    @classmethod
    def from_env(cls) -> "Settings":
        def need(name):
            v = os.getenv(name)
            if not v: raise RuntimeError(f"Missing env: {name}")
            return v
        subs = _split_csv(os.getenv("SUBREDDITS", ""))
        kws = _split_csv(os.getenv("KEYWORDS", ""))
        return cls(
            client_id=need("REDDIT_CLIENT_ID"),
            client_secret=need("REDDIT_CLIENT_SECRET"),
            user_agent=need("REDDIT_USER_AGENT"),
            username=need("REDDIT_USERNAME"),
            password=need("REDDIT_PASSWORD"),
            subreddits=subs or ["all"],
            keywords=kws,
            reply_template=os.getenv("REPLY_TEMPLATE", "Hi u/{author}, I saw '{keyword}'. (bot)"),
            dry_run=os.getenv("DRY_RUN", "true").strip().lower() in ("1","true","t","yes","y"),
            max_items=int(os.getenv("MAX_ITEMS", "200")),
        )