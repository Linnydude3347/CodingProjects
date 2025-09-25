import os
from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:////data/tasks.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, nullable=True)  # optional link to users service

    def to_dict(self):
        return {"id": self.id, "title": self.title, "completed": self.completed, "user_id": self.user_id}

with app.app_context():
    db.create_all()

@app.get("/health")
def health():
    return jsonify(status="ok")

@app.get("/tasks")
def list_tasks():
    q = Task.query
    user_id = request.args.get("user_id", type=int)
    if user_id is not None:
        q = q.filter(Task.user_id == user_id)
    tasks = q.order_by(Task.id.desc()).all()
    return jsonify([t.to_dict() for t in tasks])

@app.post("/tasks")
def create_task():
    data = request.get_json(force=True, silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        abort(400, description="title is required")
    task = Task(title=title, user_id=data.get("user_id"))
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201

@app.patch("/tasks/<int:task_id>")
def update_task(task_id):
    t = db.session.get(Task, task_id)
    if not t:
        abort(404)
    data = request.get_json(force=True, silent=True) or {}
    if "title" in data:
        new_title = (data["title"] or "").strip()
        if not new_title:
            abort(400, description="title cannot be empty")
        t.title = new_title
    if "completed" in data:
        t.completed = bool(data["completed"])
    if "user_id" in data:
        t.user_id = data["user_id"]
    db.session.commit()
    return jsonify(t.to_dict())

@app.delete("/tasks/<int:task_id>")
def delete_task(task_id):
    t = db.session.get(Task, task_id)
    if not t:
        abort(404)
    db.session.delete(t)
    db.session.commit()
    return "", 204

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)