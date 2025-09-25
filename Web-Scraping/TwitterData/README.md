# Twitter (X) Data Mining — Python

A compact toolkit to collect recent tweets via the official Twitter (X) v2 API using Tweepy, then save to JSONL/CSV/SQLite and run quick word-frequency analysis.

## Features
- Recent Search (last ~7 days) with a v2 query (e.g., `lang:en -is:retweet` filters)
- Output to **JSONL**, **CSV**, or **SQLite**
- Flattened author metadata (username, name, verified) via expansions
- Quick text analysis helper for top words from JSONL

## Quickstart

```bash
cd twitter_mining
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt

# Set your Bearer Token (from your X developer account)
export TWITTER_BEARER_TOKEN="YOUR_TOKEN_HERE"

# Fetch 500 English tweets about Python (no retweets), save to JSONL
python -m twitter_mining.main search \
    --query "(python OR pandas) lang:en -is:retweet" \
    --limit 500 \
    --jsonl data/python.jsonl
```

Save to CSV instead:

```bash
python -m twitter_mining.main search --query "datascience lang:en -is:retweet" --limit 300 --csv data/ds.csv
```

Save to SQLite:

```bash
python -m twitter_mining.main search --query "ai lang:en -is:retweet" --limit 1000 --sqlite data/tweets.db --table tweets
```

Analyze word frequency from JSONL:

```bash
python -m twitter_mining.analyze data/python.jsonl --top 30
```

## Query Tips (v2)
- Exclude retweets: `-is:retweet`
- Only English: `lang:en`
- Exact phrase: `"machine learning"`
- Boolean: `(python OR pandas) (data OR "data science") -is:retweet`

## Outputs
Each tweet is flattened with fields like:
- `id, created_at, text, lang, author_id, author_username, author_name, author_verified`
- `like_count, retweet_count, reply_count, quote_count`
- `hashtags` (pipe-delimited if present), `is_retweet`, `is_reply`, `is_quote`

## Config
- Reads `TWITTER_BEARER_TOKEN` (or `X_BEARER_TOKEN`) from environment. You can also pass `--bearer-token`.
- Optional time bounds: `--start-time` / `--end-time` in ISO 8601 UTC (e.g., `2025-09-01T00:00:00Z`).

## Notes
- Recent Search generally returns up to 7 days of data; availability and quotas depend on your developer access level.
- For historical/complete archives or streaming, extend `twitter_mining/api.py` using additional endpoints.
- Always follow Twitter/X terms when storing or re-distributing content.