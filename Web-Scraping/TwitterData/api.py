import os
import time
from datetime import datetime
from typing import Dict, Iterator, List, Optional
import tweepy

DEFAULT_TWEET_FIELDS = [
    "id","text","author_id","created_at","lang","public_metrics",
    "referenced_tweets","in_reply_to_user_id","conversation_id","entities","source"
]
DEFAULT_USER_FIELDS = [
    "id","username","name","verified","created_at","public_metrics","description","location"
]

class TwitterClient:
    def __init__(self, bearer_token: Optional[str] = None, retry: int = 3, backoff: float = 2.0):
        token = bearer_token or os.getenv("TWITTER_BEARER_TOKEN") or os.getenv("X_BEARER_TOKEN")
        if not token:
            raise RuntimeError("Bearer token not provided. Set TWITTER_BEARER_TOKEN or pass bearer_token.")
        self.client = tweepy.Client(
            bearer_token=token,
            wait_on_rate_limit=True
        )
        self.retry = retry
        self.backoff = backoff

    def search_recent(
        self,
        query: str,
        max_results: int = 100,
        limit: int = 1000,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        tweet_fields: List[str] = None,
        user_fields: List[str] = None,
        expansions: List[str] = None,
    ) -> Iterator[Dict]:
        """Yield flattened tweet dicts up to `limit` results using recent search.
        - query: a Twitter v2 query (e.g. "(python OR pandas) lang:en -is:retweet")
        - max_results: per-request (10..100)
        - limit: total tweets to yield
        - start_time/end_time: ISO 8601 (YYYY-MM-DDTHH:MM:SSZ)
        """
        tweet_fields = tweet_fields or DEFAULT_TWEET_FIELDS
        user_fields = user_fields or DEFAULT_USER_FIELDS
        expansions = expansions or ["author_id"]

        got = 0
        next_token = None

        while got < limit:
            try:
                resp = self.client.search_recent_tweets(
                    query=query,
                    max_results=min(max_results, 100),
                    next_token=next_token,
                    start_time=start_time,
                    end_time=end_time,
                    since_id=since_id,
                    until_id=until_id,
                    tweet_fields=list(set(tweet_fields)),
                    user_fields=list(set(user_fields)),
                    expansions=list(set(expansions)),
                )
            except tweepy.TooManyRequests as e:
                # Rate-limited: Tweepy with wait_on_rate_limit should sleep, but handle just in case
                time.sleep(self.backoff)
                continue
            except Exception as e:
                if self.retry > 0:
                    self.retry -= 1
                    time.sleep(self.backoff)
                    continue
                raise

            if resp is None or resp.data is None or len(resp.data) == 0:
                break

            users_by_id = {}
            if resp.includes and "users" in resp.includes:
                for u in resp.includes["users"]:
                    users_by_id[u.id] = {
                        "author_id": u.id,
                        "author_username": u.username,
                        "author_name": u.name,
                        "author_verified": bool(getattr(u, "verified", False)),
                    }

            for t in resp.data:
                # Flatten public metrics
                pm = getattr(t, "public_metrics", {}) or {}
                # Extract hashtags (if entities present)
                hashtags = None
                ents = getattr(t, "entities", None)
                if ents and "hashtags" in ents and ents["hashtags"]:
                    hashtags = [h.get("tag") for h in ents["hashtags"] if isinstance(h, dict) and h.get("tag")]
                # Compose record
                rec = {
                    "id": str(t.id),
                    "created_at": getattr(t, "created_at", None),
                    "text": getattr(t, "text", ""),
                    "lang": getattr(t, "lang", None),
                    "author_id": getattr(t, "author_id", None),
                    "like_count": pm.get("like_count"),
                    "retweet_count": pm.get("retweet_count"),
                    "reply_count": pm.get("reply_count"),
                    "quote_count": pm.get("quote_count"),
                    "source": getattr(t, "source", None),
                    "hashtags": "|".join(hashtags) if hashtags else None,
                    "is_retweet": any(rt.get("type") == "retweeted" for rt in (getattr(t, "referenced_tweets", []) or [])),
                    "is_reply": any(rt.get("type") == "replied_to" for rt in (getattr(t, "referenced_tweets", []) or [])),
                    "is_quote": any(rt.get("type") == "quoted" for rt in (getattr(t, "referenced_tweets", []) or [])),
                    "conversation_id": getattr(t, "conversation_id", None),
                    "in_reply_to_user_id": getattr(t, "in_reply_to_user_id", None),
                }
                # Merge author info
                if rec["author_id"] in users_by_id:
                    rec.update(users_by_id[rec["author_id"]])

                got += 1
                yield rec
                if got >= limit:
                    break

            meta = resp.meta or {}
            next_token = meta.get("next_token")
            if not next_token:
                break