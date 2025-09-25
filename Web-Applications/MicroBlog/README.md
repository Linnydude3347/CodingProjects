# MicroBlog (Flask)

A tiny Twitter-style microblog built with Flask + SQLite + SQLAlchemy + Flask-Login.

## Quickstart

```bash
cd flask_microblog
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Optional: set a real secret
export SECRET_KEY="change-me"

# Run the app
python app.py
# App will start on http://127.0.0.1:5000
```

## Features
- Register / login / logout
- Create, edit, delete short posts (280 chars)
- User profiles with their posts
- Pagination on timelines
- Simple dark UI (pure CSS, no JS)

## Environment
- DB defaults to local SQLite file `microblog.db`. Override with `DATABASE_URL` env var.
- CSRF is enabled via `Flask-WTF` (SECRET_KEY required).

## Notes
- This is intentionally compact and suitable for learning / prototyping.
- For production, add proper logging, error pages, and serve with a WSGI server.