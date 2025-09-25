import os
from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:////data/users.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

    def to_dict(self):
        return {"id": self.id, "username": self.username}

with app.app_context():
    db.create_all()

@app.get("/health")
def health():
    return jsonify(status="ok")

@app.get("/users")
def list_users():
    users = User.query.order_by(User.id.asc()).all()
    return jsonify([u.to_dict() for u in users])

@app.post("/users")
def create_user():
    data = request.get_json(force=True, silent=True) or {}
    username = (data.get("username") or "").strip()
    if not username:
        abort(400, description="username is required")
    if User.query.filter_by(username=username).first():
        abort(409, description="username already exists")
    u = User(username=username)
    db.session.add(u)
    db.session.commit()
    return jsonify(u.to_dict()), 201

@app.get("/users/<int:user_id>")
def get_user(user_id):
    u = db.session.get(User, user_id)
    if not u:
        abort(404)
    return jsonify(u.to_dict())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)