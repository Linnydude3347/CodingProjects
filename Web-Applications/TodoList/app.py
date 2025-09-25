import os
from uuid import uuid4
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, g
import rethinkdb as r

APP_NAME = "Flask + RethinkDB Todo"

RDB_HOST = os.environ.get("RDB_HOST", "localhost")
RDB_PORT = int(os.environ.get("RDB_PORT", "28015"))
RDB_DB = os.environ.get("RDB_DB", "todoapp")
RDB_TABLE = os.environ.get("RDB_TABLE", "todos")

def get_conn():
    return r.connect(host=RDB_HOST, port=RDB_PORT, db=RDB_DB)

def ensure_db():
    # Create DB and table if they don't exist
    conn = r.connect(host=RDB_HOST, port=RDB_PORT)
    if RDB_DB not in r.db_list().run(conn):
        r.db_create(RDB_DB).run(conn)
    conn.use(RDB_DB)
    if RDB_TABLE not in r.table_list().run(conn):
        r.table_create(RDB_TABLE, primary_key="id").run(conn)
        # Secondary index for created_at (useful for ordering)
        r.table(RDB_TABLE).index_create("created_at").run(conn)
        r.table(RDB_TABLE).index_wait("created_at").run(conn)
    conn.close()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")

@app.before_request
def before_request():
    g.rdb_conn = get_conn()

@app.teardown_request
def teardown_request(exc):
    conn = getattr(g, "rdb_conn", None)
    if conn:
        try:
            conn.close()
        except Exception:
            pass

def list_todos(filter_by=None):
    q = r.table(RDB_TABLE)
    if filter_by == "active":
        q = q.filter({"completed": False})
    elif filter_by == "completed":
        q = q.filter({"completed": True})
    # newest first
    q = q.order_by(r.desc("created_at"))
    return list(q.run(g.rdb_conn))

@app.route("/")
def index():
    filter_by = request.args.get("filter", "all")
    todos = list_todos(filter_by if filter_by in {"all", "active", "completed"} else "all")
    counts = {
        "all": r.table(RDB_TABLE).count().run(g.rdb_conn),
        "active": r.table(RDB_TABLE).filter({"completed": False}).count().run(g.rdb_conn),
        "completed": r.table(RDB_TABLE).filter({"completed": True}).count().run(g.rdb_conn),
    }
    return render_template("index.html", app_name=APP_NAME, todos=todos, filter_by=filter_by, counts=counts)

@app.route("/add", methods=["POST"])
def add():
    title = (request.form.get("title") or "").strip()
    if not title:
        flash("Please enter a task.", "danger")
        return redirect(url_for("index"))
    doc = {
        "id": str(uuid4()),
        "title": title,
        "completed": False,
        "created_at": r.now(),
        "updated_at": r.now(),
    }
    r.table(RDB_TABLE).insert(doc).run(g.rdb_conn)
    flash("Task added.", "success")
    return redirect(url_for("index"))

@app.route("/toggle/<string:todo_id>", methods=["POST"])
def toggle(todo_id):
    # Toggle server-side using branch
    r.table(RDB_TABLE).get(todo_id).update({
        "completed": r.branch(r.row["completed"] == True, False, True),
        "updated_at": r.now()
    }).run(g.rdb_conn)
    return redirect(url_for("index", filter=request.args.get("filter", "all")))

@app.route("/edit/<string:todo_id>", methods=["POST"])
def edit(todo_id):
    title = (request.form.get("title") or "").strip()
    if not title:
        flash("Title cannot be empty.", "danger")
        return redirect(url_for("index"))
    r.table(RDB_TABLE).get(todo_id).update({
        "title": title,
        "updated_at": r.now()
    }).run(g.rdb_conn)
    flash("Task updated.", "success")
    return redirect(url_for("index", filter=request.args.get("filter", "all")))

@app.route("/delete/<string:todo_id>", methods=["POST"])
def delete(todo_id):
    r.table(RDB_TABLE).get(todo_id).delete().run(g.rdb_conn)
    flash("Task deleted.", "info")
    return redirect(url_for("index", filter=request.args.get("filter", "all")))

@app.route("/clear-completed", methods=["POST"])
def clear_completed():
    r.table(RDB_TABLE).filter({"completed": True}).delete().run(g.rdb_conn)
    flash("Cleared completed tasks.", "info")
    return redirect(url_for("index"))

@app.template_filter("fmt_dt")
def fmt_dt(value):
    # RethinkDB returns timezone-aware datetimes; format nicely.
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    return value

if __name__ == "__main__":
    ensure_db()
    app.run(debug=True)