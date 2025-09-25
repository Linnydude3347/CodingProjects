# Django Blog

A minimal yet complete blog built with Django: list posts, read details, create/edit/delete (auth required), with pagination and a simple dark theme.

## Quickstart

```bash
cd django_blog
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt

# Create DB & admin user
python manage.py migrate
python manage.py createsuperuser

# Run the server
python manage.py runserver
# Visit http://127.0.0.1:8000
```

## Features
- Home page with paginated posts (newest first)
- Post detail pages (slug-based URLs)
- Create, update, delete posts (author-only)
- Sign up, login, logout via Django auth
- Admin interface for managing posts
- Lightweight dark UI (no JS)

## Structure
- `blogproject/` — project settings, URLs, WSGI/ASGI
- `blog/` — app with models, views, URLs, admin
- `templates/` — Jinja-like Django templates
- `static/` — global CSS
- `manage.py` — Django CLI entry point

## Notes
- Default DB is SQLite at `db.sqlite3`.
- Set a real secret in production: `export DJANGO_SECRET_KEY="change-me"`.
- For deploying, add a proper `ALLOWED_HOSTS`, debug off, static collection, and a WSGI/ASGI server.