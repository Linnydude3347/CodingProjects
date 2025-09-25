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
    bearer: str
    api_key: str
    api_secret: str
    access_token: str
    access_secret: str
    keywords: List[str]
    reply_template: str
    dry_run: bool
    max_actions: int

    @classmethod
    def from_env(cls) -> "Settings":
        def need(name):
            v = os.getenv(name)
            if not v: raise RuntimeError(f"Missing env: {name}")
            return v
        return cls(
            bearer=need("TWITTER_BEARER_TOKEN"),
            api_key=need("TWITTER_API_KEY"),
            api_secret=need("TWITTER_API_SECRET"),
            access_token=need("TWITTER_ACCESS_TOKEN"),
            access_secret=need("TWITTER_ACCESS_SECRET"),
            keywords=_split_csv(os.getenv("KEYWORDS","")),
            reply_template=os.getenv("REPLY_TEMPLATE", "Hi @{author}, I saw '{keyword}'. (bot)"),
            dry_run=os.getenv("DRY_RUN","true").strip().lower() in ("1","true","yes","y"),
            max_actions=int(os.getenv("MAX_ACTIONS","200")),
        )