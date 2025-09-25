from __future__ import annotations
import argparse, logging
from x_bot.config import Settings
from x_bot.twitter_client import XClient
from x_bot.storage import StateDB
from x_bot.handlers import find_keyword, render_reply

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("x-bot")

# -------------- commands --------------
def cmd_tweet(args):
    cfg = Settings.from_env()
    api = XClient(cfg.bearer, cfg.api_key, cfg.api_secret, cfg.access_token, cfg.access_secret)
    if cfg.dry_run:
        print(f"[DRY RUN] Would tweet: {args.text}")
        return
    url = api.tweet(args.text)
    print("Tweeted:", url)

def cmd_reply_mentions(args):
    cfg = Settings.from_env()
    api = XClient(cfg.bearer, cfg.api_key, cfg.api_secret, cfg.access_token, cfg.access_secret)
    db = StateDB()
    since_id = args.since or db.get("since_id")
    log.info("Me: @%s", api.me().username)
    log.info("Fetching mentions since_id=%s", since_id or "(none)")
    handled = 0
    max_id = since_id

    try:
        for t in api.mentions(since_id=since_id, limit=args.max or cfg.max_actions):
            tid = str(t.id)
            text = t.text or ""
            author = t.author_id  # we only have ID unless we expand; reply will @ author from context
            # rough author username not available without expansions; reply text doesn't need it
            kw = find_keyword(text, cfg.keywords)
            if kw:
                body = render_reply(cfg.reply_template, author="", keyword=kw)
                msg = f"[DRY RUN] Would reply to {tid}: {body}" if cfg.dry_run else None
                if cfg.dry_run:
                    print(msg)
                else:
                    try:
                        url = api.reply(body, in_reply_to_id=tid)
                        print("Replied:", url)
                    except Exception as e:
                        log.warning("reply failed for %s: %s", tid, e)
            # mark seen
            db.mark(tid)
            handled += 1
            if max_id is None or int(tid) > int(max_id or 0):
                max_id = tid
            if handled >= (args.max or cfg.max_actions):
                break
    finally:
        if max_id:
            db.set("since_id", max_id)
        db.close()
    print(f"Handled {handled} mention(s). New since_id={max_id}")

def cmd_search_reply(args):
    cfg = Settings.from_env()
    api = XClient(cfg.bearer, cfg.api_key, cfg.api_secret, cfg.access_token, cfg.access_secret)
    db = StateDB()
    handled = 0
    try:
        for t in api.search_recent(args.query, limit=args.limit or cfg.max_actions):
            tid = str(t.id)
            if db.seen(tid): continue
            kw = find_keyword(t.text or "", cfg.keywords)
            if kw:
                body = render_reply(cfg.reply_template, author="", keyword=kw)
                if cfg.dry_run:
                    print(f"[DRY RUN] Would reply to {tid}: {body}")
                else:
                    try:
                        url = api.reply(body, in_reply_to_id=tid)
                        print("Replied:", url)
                    except Exception as e:
                        log.warning("reply failed for %s: %s", tid, e)
            db.mark(tid)
            handled += 1
            if handled >= (args.limit or cfg.max_actions):
                break
    finally:
        db.close()
    print(f"Handled {handled} tweet(s) from search.")

def main(argv=None):
    ap = argparse.ArgumentParser(description="Twitter (X) Bot CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("tweet", help="Post a tweet")
    t.add_argument("--text", required=True)
    t.set_defaults(func=cmd_tweet)

    m = sub.add_parser("reply-mentions", help="Reply to mentions since last run (keyword-based)")
    m.add_argument("--since", help="Override since_id (default: from state.db)")
    m.add_argument("--max", type=int, help="Max actions this run")
    m.set_defaults(func=cmd_reply_mentions)

    s = sub.add_parser("search-reply", help="Search recent tweets and reply on keyword hits")
    s.add_argument("--query", required=True, help='e.g. "(python OR pandas) lang:en -is:retweet"')
    s.add_argument("--limit", type=int, help="Max tweets to consider")
    s.set_defaults(func=cmd_search_reply)

    args = ap.parse_args(argv)
    args.func(args)

if __name__ == "__main__":
    main()