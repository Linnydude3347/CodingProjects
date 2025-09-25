from __future__ import annotations
import argparse
from praw.models import Submission

from .config import Settings
from .reddit_client import make_reddit
from .storage import SeenStore
from .handlers import find_keyword, render_reply, reply_to_thing

def iter_stream(subreddit, kinds=('submissions','comments'), pause_after=5, limit=1000):
    count = 0
    if 'submissions' in kinds:
        for s in subreddit.stream.submissions(skip_existing=True, pause_after=pause_after):
            if s is None: break
            yield s
            count += 1
            if count >= limit: break
    if 'comments' in kinds and count < limit:
        for c in subreddit.stream.comments(skip_existing=True, pause_after=pause_after):
            if c is None: break
            yield c
            count += 1
            if count >= limit: break

def do_stream(args):
    cfg = Settings.from_env()
    # CLI overrides
    if args.subs: cfg.subreddits = [s.strip() for s in args.subs.split(',') if s.strip()]
    if args.keywords: cfg.keywords = [k.strip() for k in args.keywords.split(',') if k.strip()]
    if args.reply_template: cfg.reply_template = args.reply_template
    if args.dry_run is not None: cfg.dry_run = args.dry_run
    if args.max_items: cfg.max_items = args.max_items

    reddit = make_reddit(cfg)
    seen = SeenStore()

    subs = '+'.join(cfg.subreddits) if cfg.subreddits else 'all'
    sr = reddit.subreddit(subs)
    print(f"Streaming r/{subs} (comments+submissions). Dry-run={cfg.dry_run}. Max items={cfg.max_items}. Keywords={cfg.keywords}")

    handled = 0
    try:
        # Simple loop: interleave submissions and comments
        while handled < cfg.max_items:
            for thing in iter_stream(sr, kinds=('submissions','comments'), pause_after=5, limit=cfg.max_items - handled):
                if thing is None:
                    break
                if seen.seen(thing.fullname):
                    continue
                body = thing.selftext if isinstance(thing, Submission) else thing.body
                kw = find_keyword(body or '', cfg.keywords)
                if kw:
                    author = str(thing.author) if thing.author else "[deleted]"
                    permalink = f"https://www.reddit.com{thing.permalink}"
                    subreddit = str(thing.subreddit)
                    title = thing.title if isinstance(thing, Submission) else ''
                    url = getattr(thing, 'url', '') if isinstance(thing, Submission) else ''
                    reply_body = render_reply(cfg.reply_template, author=author, keyword=kw, permalink=permalink, subreddit=subreddit, title=title, url=url)
                    res = reply_to_thing(thing, reply_body, dry_run=cfg.dry_run)
                    print(res)
                seen.mark(thing.fullname, thing.__class__.__name__)
                handled += 1
                if handled >= cfg.max_items:
                    break
    finally:
        seen.close()

def do_inbox(args):
    cfg = Settings.from_env()
    if args.dry_run is not None: cfg.dry_run = args.dry_run
    reddit = make_reddit(cfg)
    seen = SeenStore()
    me = reddit.user.me()
    print(f"Processing inbox for u/{me} (dry_run={cfg.dry_run})")
    count = 0
    try:
        for item in reddit.inbox.unread(limit=cfg.max_items):
            if seen.seen(item.fullname):
                continue
            body = getattr(item, 'body', '') or ''
            author = str(getattr(item, 'author', None)) if getattr(item, 'author', None) else "[deleted]"
            permalink = getattr(item, 'context', None) or ''
            subreddit = str(getattr(item, 'subreddit', '')) if getattr(item, 'subreddit', None) else ''
            # Detect a keyword inside the mention body (optional)
            kw = find_keyword(body, cfg.keywords) if cfg.keywords else 'your mention'
            reply_body = render_reply(cfg.reply_template, author=author, keyword=kw, permalink=permalink, subreddit=subreddit)
            res = reply_to_thing(item, reply_body, dry_run=cfg.dry_run)
            print(res)
            if args.mark_read and not cfg.dry_run:
                try: item.mark_read()
                except Exception: pass
            seen.mark(item.fullname, item.__class__.__name__)
            count += 1
            if count >= cfg.max_items: break
    finally:
        seen.close()

def do_once(args):
    cfg = Settings.from_env()
    if args.subs: cfg.subreddits = [s.strip() for s in args.subs.split(',') if s.strip()]
    if args.keywords: cfg.keywords = [k.strip() for k in args.keywords.split(',') if k.strip()]
    if args.reply_template: cfg.reply_template = args.reply_template
    if args.dry_run is not None: cfg.dry_run = args.dry_run

    reddit = make_reddit(cfg)
    seen = SeenStore()
    subs = '+'.join(cfg.subreddits) if cfg.subreddits else 'all'
    sr = reddit.subreddit(subs)

    print(f"Scanning latest from r/{subs} (new posts & comments), dry_run={cfg.dry_run}")
    try:
        # Fetch a small window of new items
        count = 0
        for s in sr.new(limit=args.limit):
            if seen.seen(s.fullname): continue
            kw = find_keyword(s.selftext or '', cfg.keywords)
            if kw:
                author = str(s.author) if s.author else "[deleted]"
                permalink = f"https://www.reddit.com{s.permalink}"
                reply_body = render_reply(cfg.reply_template, author=author, keyword=kw, permalink=permalink, subreddit=str(s.subreddit), title=s.title, url=s.url)
                print(reply_to_thing(s, reply_body, dry_run=cfg.dry_run))
            seen.mark(s.fullname, 'Submission'); count += 1
            if count >= cfg.max_items: break
        for c in sr.comments(limit=args.limit):
            if seen.seen(c.fullname): continue
            kw = find_keyword(c.body or '', cfg.keywords)
            if kw:
                author = str(c.author) if c.author else "[deleted]"
                permalink = f"https://www.reddit.com{c.permalink}"
                reply_body = render_reply(cfg.reply_template, author=author, keyword=kw, permalink=permalink, subreddit=str(c.subreddit))
                print(reply_to_thing(c, reply_body, dry_run=cfg.dry_run))
            seen.mark(c.fullname, 'Comment'); count += 1
            if count >= cfg.max_items: break
    finally:
        seen.close()

def main(argv=None):
    ap = argparse.ArgumentParser(description="Reddit Bot — PRAW")
    sub = ap.add_subparsers(dest='cmd', required=True)

    st = sub.add_parser('stream', help='Stream comments + submissions and act on keyword hits')
    st.add_argument('--subs', help='Comma-separated subreddits (default from .env or all)')
    st.add_argument('--keywords', help='Comma-separated keywords')
    st.add_argument('--reply-template', help='Reply template string')
    st.add_argument('--dry-run', action=argparse.BooleanOptionalAction, default=None)
    st.add_argument('--max-items', type=int, help='Safety cap per run (default .env MAX_ITEMS)')
    st.set_defaults(func=do_stream)

    ib = sub.add_parser('inbox', help='Process unread inbox (mentions/messages)')
    ib.add_argument('--dry-run', action=argparse.BooleanOptionalAction, default=None)
    ib.add_argument('--mark-read', action='store_true', help='Mark items read after replying')
    ib.set_defaults(func=do_inbox)

    once = sub.add_parser('once', help='Scan latest N items (no streaming)')
    once.add_argument('--subs', help='Comma-separated subreddits')
    once.add_argument('--keywords', help='Comma-separated keywords')
    once.add_argument('--reply-template', help='Reply template string')
    once.add_argument('--limit', type=int, default=200, help='How many to fetch for posts/comments')
    once.add_argument('--dry-run', action=argparse.BooleanOptionalAction, default=None)
    once.set_defaults(func=do_once)

    args = ap.parse_args(argv)
    args.func(args)

if __name__ == '__main__':
    main()