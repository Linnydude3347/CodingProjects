from __future__ import annotations
import praw
from .config import Settings

def make_reddit(cfg: Settings) -> praw.Reddit:
    # Password grant ('script' app)
    reddit = praw.Reddit(
        client_id=cfg.client_id,
        client_secret=cfg.client_secret,
        user_agent=cfg.user_agent,
        username=cfg.username,
        password=cfg.password,
        ratelimit_seconds=60,  # hint to PRAW
    )
    # test a lightweight read
    _ = reddit.user.me()
    return reddit