# Twitter (X) Bot — Tweepy (v2)

A simple but sturdy **Twitter/X bot** using **Tweepy** and the **v2 API**. It can **tweet**, **poll mentions** and reply on keyword hits, and (optionally) search and reply. It keeps a small SQLite state to avoid repeats and supports **dry‑run** mode for safe testing.

## Features
- Tweet / reply from CLI
- Poll **mentions** since last run and reply when a keyword is found
- Optional **search & reply** by query
- SQLite `state.db` to store `since_id` and processed tweet IDs
- Dry‑run mode to preview actions
- Dockerfile & docker-compose for deployment

## Quickstart
```bash
cd twitter_bot
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill your keys & behavior
```

### Post a tweet
```bash
python -m x_bot.main tweet --text "Hello from my bot!"
```

### Reply to mentions (keywords from .env)
```bash
python -m x_bot.main reply-mentions --max 100
```

### Search and reply to recent tweets
```bash
python -m x_bot.main search-reply       --query "(python OR pandas) lang:en -is:retweet"       --limit 50
```

## Getting credentials
1. Apply at https://developer.x.com/ and create a Project + App.
2. Generate **API Key & Secret**, **Bearer Token**, and **Access Token & Secret** (user context).
3. Put them into `.env`. Make sure your plan allows posting.

## CLI
```bash
python -m x_bot.main -h
python -m x_bot.main tweet -h
python -m x_bot.main reply-mentions -h
python -m x_bot.main search-reply -h
```

## Docker
```bash
docker compose up --build
```

## Notes
- The bot matches keywords as whole words (case-insensitive). Customize `handlers.py` for regex logic.
- Respect platform policies and rate limits. Start with `DRY_RUN=true`.