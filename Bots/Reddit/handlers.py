from __future__ import annotations
import re
from typing import Optional
from praw.models import Comment, Submission

def find_keyword(text: str, keywords: list[str]) -> Optional[str]:
    t = text or ""
    for kw in keywords:
        if not kw: continue
        pattern = re.escape(kw)
        if re.search(rf"\b{pattern}\b", t, flags=re.IGNORECASE):
            return kw
    return None

def render_reply(template: str, *, author: str, keyword: str, permalink: str, subreddit: str, title: str = "", url: str = "") -> str:
    safe = template.format(author=author or "", keyword=keyword or "", permalink=permalink or "", subreddit=subreddit or "", title=title or "", url=url or "")
    return safe

def reply_to_thing(thing: Comment | Submission, body: str, dry_run: bool = True) -> Optional[str]:
    if dry_run:
        return f"[DRY RUN] Would reply to {thing.fullname} with: {body[:140]}..."
    try:
        rep = thing.reply(body)
        return rep.permalink
    except Exception as e:
        return f"Error replying: {e}"