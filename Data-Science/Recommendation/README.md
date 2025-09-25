# Recommendation Systems — Data Analysis Toolkit

A compact, practical collection of classic recommendation algorithms with a consistent API, evaluation helpers, and a CLI. Bring your own interactions (ratings or implicit feedback) and get top-N recommendations plus metrics like Precision@K, Recall@K, MAP, and NDCG.

## Algorithms
- **Popularity** baseline (by count or mean rating)
- **User-KNN** collaborative filtering (cosine)
- **Item-KNN** collaborative filtering (cosine)
- **SVD (MF)** via sparse truncated SVD (scipy.sparse.linalg.svds)
- **Content-based** (TF‑IDF on item metadata + cosine)

> Optional: swap in more advanced methods (implicit ALS, LightFM) by uncommenting deps in `requirements.txt` and extending `recommenders/`.

## Data format
Provide a CSV with columns:
- `user_id` — user identifier (string or int)
- `item_id` — item identifier
- `rating` — numeric (explicit). For implicit usage, set 1/0 or leave out and we will binarize.
- `timestamp` — optional (unix seconds or ISO), used by time-based splits

Minimal sample at `data/sample_ratings.csv` is included.

Optional metadata CSV (for content-based), with e.g.:
- `item_id`, `title`, `genres` (or `description`) — free text used to build TF‑IDF item vectors

## Quickstart
```bash
cd recommender_systems
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
```

Evaluate Item-KNN on the sample data:
```bash
python -m scripts.cli eval       --ratings data/sample_ratings.csv       --algo itemknn --topk 10 --min-user-interactions 3
```

Get recommendations for a single user:
```bash
python -m scripts.cli recommend       --ratings data/sample_ratings.csv       --algo svd --user u_3 --topk 5
```

Content-based (needs item metadata):
```bash
python -m scripts.cli recommend       --ratings data/sample_ratings.csv       --items data/sample_items.csv       --algo content --user u_3 --topk 5 --text-cols title,genres
```

## MovieLens (optional)
Use the helper script to download/prepare MovieLens 100K:
```bash
python -m scripts.prepare_movielens --dest data/raw --variant ml-100k
python -m scripts.cli eval --ratings data/raw/ml-100k/ratings.csv --algo itemknn --topk 10
```

## Notes
- SVD uses a simple truncated SVD on the (sparse) user–item matrix; set `--factors` as needed.
- For implicit feedback, pass `--implicit` to the CLI to binarize interactions (rating > 0 ⇒ 1).
- Metrics evaluate holdout interactions per user; cold-start users/items are skipped by default.