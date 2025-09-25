from __future__ import annotations
import tweepy, logging
from dataclasses import dataclass
from typing import Optional

log = logging.getLogger("x-bot")

@dataclass
class Me:
    id: str
    username: str
    name: str

class XClient:
    def __init__(self, bearer: str, api_key: str, api_secret: str, access_token: str, access_secret: str):
        # Use user context for write actions
        self.client = tweepy.Client(
            bearer_token=bearer,
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret,
            wait_on_rate_limit=True,
        )
        self._me: Optional[Me] = None

    def me(self) -> Me:
        if self._me: return self._me
        r = self.client.get_me()
        u = r.data
        self._me = Me(id=str(u.id), username=u.username, name=u.name)
        return self._me

    # --- actions ---
    def tweet(self, text: str) -> str:
        r = self.client.create_tweet(text=text[:280])
        return f"https://twitter.com/{self.me().username}/status/{r.data.get('id')}"

    def reply(self, text: str, in_reply_to_id: str) -> str:
        r = self.client.create_tweet(text=text[:280], in_reply_to_tweet_id=in_reply_to_id)
        return f"https://twitter.com/{self.me().username}/status/{r.data.get('id')}"

    def like(self, tweet_id: str):
        self.client.like(tweet_id)

    def retweet(self, tweet_id: str):
        self.client.retweet(tweet_id)

    # --- fetching ---
    def mentions(self, since_id: str | None = None, limit: int = 100):
        uid = self.me().id
        paginator = tweepy.Paginator(
            self.client.get_users_mentions,
            id=uid,
            since_id=since_id,
            max_results=100,
            tweet_fields=["created_at","author_id","conversation_id","in_reply_to_user_id","public_metrics","lang"],
        )
        count = 0
        for page in paginator:
            if not page.data: break
            for t in page.data:
                yield t
                count += 1
                if count >= limit: return

    def search_recent(self, query: str, limit: int = 100):
        paginator = tweepy.Paginator(
            self.client.search_recent_tweets,
            query=query,
            max_results=100,
            tweet_fields=["created_at","author_id","conversation_id","in_reply_to_user_id","public_metrics","lang"],
        )
        count = 0
        for page in paginator:
            if not page.data: break
            for t in page.data:
                yield t
                count += 1
                if count >= limit: return