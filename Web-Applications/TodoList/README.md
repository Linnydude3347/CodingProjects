# Todo List — Flask + RethinkDB

A simple, clean Todo app backed by RethinkDB. Create, edit, complete, and delete tasks with server-side filtering. Perfect for learning ReQL with Flask.

## Features
- Add tasks (title up to 200 chars)
- Toggle complete/incomplete
- Edit titles inline
- Delete tasks
- Filter: All / Active / Completed
- Auto-creates DB, table, and index on first run

## Quickstart

1) **Install and start RethinkDB**

- macOS (Homebrew): `brew install rethinkdb && rethinkdb`
- Linux: use your package manager or download from https://rethinkdb.com
- Windows: use WSL or Docker

2) **Run the app**

```bash
cd flask_rethink_todo
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt

export SECRET_KEY="change-me"        # optional
export RDB_HOST="localhost"          # default
export RDB_PORT="28015"              # default
export RDB_DB="todoapp"              # default
export RDB_TABLE="todos"             # default

python app.py
# Open http://127.0.0.1:5000
```

## Schema

Table: `todos`

```json
{
  "id": "uuid",
  "title": "string",
  "completed": false,
  "created_at": "RethinkDB time",
  "updated_at": "RethinkDB time"
}
```

Secondary index: `created_at`

## Notes
- This is a minimal server-rendered app (no frontend framework).
- For real-time updates, consider RethinkDB changefeeds + websockets (e.g., Flask-Sock).