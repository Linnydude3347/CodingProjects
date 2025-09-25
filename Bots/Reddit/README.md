# Reddit Bot (PRAW)

A lightweight Reddit bot using **PRAW** that can **watch subreddits**, **reply on keyword hits**, and **process mentions**. It keeps a small SQLite database to avoid double-posting and supports **dry‑run** mode to preview actions.

## Features
- Stream **submissions & comments** from target subreddits (or `all`)
- Keyword matching (case‑insensitive, whole phrase)
- Inbox mention processing (`u/yourbot`)
- SQLite `seen` store to prevent duplicates
- Dry‑run mode for safe testing
- Dockerfile & docker-compose for easy deploy

## Quickstart
```bash
cd reddit_bot
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Fill in your API keys and desired behavior in .env
```

Run a stream (uses .env defaults):
```bash
python -m bot.main stream
```

Process unread mentions once:
```bash
python -m bot.main inbox --mark-read
```

Override subs/keywords from CLI:
```bash
python -m bot.main stream --subs "python,learnpython" --keywords "pandas,numpy" --dry-run
```

## How to get credentials
1. Create a Reddit account for your bot (or use yours if allowed).
2. Go to https://www.reddit.com/prefs/apps → **create app** → type **script**.
3. Copy **client ID** and **secret**. Set **user agent** like `yourapp:1.0 (by u/yourname)`.
4. Put values into `.env` (`REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USERNAME`, `REDDIT_PASSWORD`, `REDDIT_USER_AGENT`).

## CLI
```bash
python -m bot.main -h
python -m bot.main stream -h
python -m bot.main inbox -h
python -m bot.main once -h
```

## Docker
```bash
docker compose up --build
```

## Notes
- PRAW manages rate‑limits; this bot also caps operations with `MAX_ITEMS` as a safety.
- Keyword matches are literal (case‑insensitive). You can add regex in `handlers.py` if you need it.
- To avoid spam, consider replying only when you’re explicitly mentioned or when authors are asking questions (e.g., contains a `?`). Customize in `handlers.py`.