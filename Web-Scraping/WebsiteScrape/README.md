# Scrape a Website with Scrapy + MongoDB

A ready-to-run Scrapy project that saves scraped items into MongoDB. Includes a generic site spider and a demo spider for `quotes.toscrape.com`.

## Features
- **Generic spider**: crawl from a start URL, follow in-domain links (optional), extract basic page info
- **Mongo pipeline**: upsert by unique key (`url` by default), with automatic unique index
- **.env support**: configure Mongo via environment variables (`python-dotenv`)
- **Demo spider**: `quotes_demo` targets the public test site `quotes.toscrape.com`

## Quickstart

```bash
# 1) (Optional) Start MongoDB via Docker
docker compose up -d mongo

# 2) Set up environment
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # customize if needed
```

### Run the demo spider
```bash
scrapy crawl quotes_demo -O data/quotes.jsonl
```

### Run the generic spider (in-domain crawl)
```bash
# Crawl up to 100 pages starting from the URL, store pages in Mongo
scrapy crawl generic -a url=https://quotes.toscrape.com -a follow=true -a max_pages=100
```

**Arguments**
- `url` (required): starting page
- `allowed` (optional): domain to constrain (e.g., `-a allowed=example.com`)
- `follow` (default: `true`): follow links within domain
- `max_pages` (default: `100`): safety limit

## MongoDB storage
Configure via `.env` (or real env vars):
```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB=scrapy_db
MONGO_COLLECTION=pages
MONGO_UNIQUE_KEY=url
```

The pipeline creates a unique index on `MONGO_UNIQUE_KEY` and performs an upsert for each item.

## Notes
- Default politeness: `ROBOTSTXT_OBEY = True`, small `DOWNLOAD_DELAY`. Adjust responsibly.
- To export to files, use Scrapy's feeds: `-O data/output.jsonl` or `-O data/output.csv`.
- For larger crawls, consider rotating proxies, caching (`HTTPCACHE_ENABLED=1`), and more robust deduplication.