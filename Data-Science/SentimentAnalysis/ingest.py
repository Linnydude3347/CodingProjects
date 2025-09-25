import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

try:
    import tweepy
except ImportError as e:
    tweepy = None

DEFAULT_TWEET_FIELDS = [
    "id","text","author_id","created_at","lang","public_metrics","referenced_tweets","source"
]

def _client(bearer_token: Optional[str]=None):
    if tweepy is None:
        raise RuntimeError("tweepy not installed. Please `pip install tweepy`.")
    token = bearer_token or os.getenv("TWITTER_BEARER_TOKEN")
    if not token:
        raise RuntimeError("Bearer token missing. Set TWITTER_BEARER_TOKEN or pass --bearer-token.")
    return tweepy.Client(bearer_token=token, wait_on_rate_limit=True)

def search_recent(query: str, limit: int = 200, max_results: int = 100,
                  start_time: Optional[str] = None, end_time: Optional[str] = None,
                  bearer_token: Optional[str] = None):
    """Yield basic tweet dicts from the v2 recent search endpoint."""
    client = _client(bearer_token)
    got = 0
    next_token = None
    while got < limit:
        resp = client.search_recent_tweets(
            query=query,
            max_results=min(max_results, 100),
            next_token=next_token,
            start_time=start_time,
            end_time=end_time,
            tweet_fields=DEFAULT_TWEET_FIELDS,
        )
        if resp is None or resp.data is None:
            break
        for t in resp.data:
            pm = getattr(t, "public_metrics", {}) or {}
            yield {
                "id": str(t.id),
                "created_at": getattr(t, "created_at", None),
                "text": getattr(t, "text", ""),
                "lang": getattr(t, "lang", None),
                "like_count": pm.get("like_count"),
                "retweet_count": pm.get("retweet_count"),
                "reply_count": pm.get("reply_count"),
                "quote_count": pm.get("quote_count"),
                "source": getattr(t, "source", None),
            }
            got += 1
            if got >= limit:
                break
        meta = resp.meta or {}
        next_token = meta.get("next_token")
        if not next_token:
            break