# Twitter (X) Sentiment Analysis — Python Data Science

A compact pipeline to collect tweets (via the official v2 API), clean text, run sentiment analysis (VADER or an optional Transformer), and generate quick visual reports.

## Features
- **Fetch** recent tweets (last ~7 days) with a v2 query using Tweepy
- **Load** existing CSV/JSONL files (if you already have tweets)
- **Preprocess**: URL/mention/hashtag cleanup, emoji handling, normalization
- **Sentiment**: VADER (fast, lexicon-based) or optional **Transformers** pipeline
- **Report**: counts, distribution, and time-series plots

## Quickstart
```bash
cd twitter_sentiment
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 1) Fetch data (optional)
Requires a Twitter/X developer account:
```bash
export TWITTER_BEARER_TOKEN="YOUR_TOKEN"
python -m twitter_sentiment.cli fetch \
  --query "(python OR pandas) lang:en -is:retweet" \
  --limit 500 \
  --jsonl data/python.jsonl
```

Or use your own CSV/JSONL with a `text` column (and optionally `created_at`).

### 2) Analyze sentiment
```bash
# VADER (default)
python -m twitter_sentiment.cli analyze --input data/python.jsonl --out data/python_scored.csv

# Optional: Transformers (uncomment deps in requirements.txt first)
# python -m twitter_sentiment.cli analyze --input data/python.jsonl --out data/python_scored.csv --model hf
```

### 3) Generate report (charts saved under reports/)
```bash
python -m twitter_sentiment.cli report --input data/python_scored.csv
```

## Output columns
The analyze step adds:
- `sentiment` ∈ {`positive`, `neutral`, `negative`}
- `sentiment_score` (VADER compound score in [-1, 1], or model score in [0,1])

## Notes
- For Transformers, the default is `cardiffnlp/twitter-roberta-base-sentiment-latest`. Adjust with `--hf-model`.
- Time series uses `created_at` if available; otherwise it groups by row index.
- You can run `analyze` directly on CSV/JSONL without fetching.