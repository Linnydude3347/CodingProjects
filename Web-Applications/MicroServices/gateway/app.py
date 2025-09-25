import os
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import requests

USERS_URL = os.environ.get("USERS_URL", "http://users:5000")
TASKS_URL = os.environ.get("TASKS_URL", "http://tasks:5000")
PORT = int(os.environ.get("PORT", "8080"))
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")

app = Flask(__name__)
if CORS_ORIGINS:
    CORS(app, resources={r"/api/*": {"origins": CORS_ORIGINS}})

SERVICE_MAP = {
    "users": USERS_URL,
    "tasks": TASKS_URL,
}

@app.get("/health")
def health():
    return jsonify(status="ok")

def _proxy(service_name, rest=""):
    base = SERVICE_MAP.get(service_name)
    if not base:
        return jsonify(error="Unknown service"), 404

    url = f"{base}/{rest}" if rest else base
    resp = requests.request(
        method=request.method,
        url=url,
        params=request.args,
        data=request.get_data(),
        headers={k: v for k, v in request.headers if k.lower() != "host"},
        cookies=request.cookies,
    )
    excluded = {"content-encoding", "content-length", "transfer-encoding", "connection"}
    headers = [(k, v) for k, v in resp.headers.items() if k.lower() not in excluded]
    return Response(resp.content, status=resp.status_code, headers=headers)

@app.route("/api/<service>", methods=["GET", "POST", "PATCH", "DELETE", "PUT", "OPTIONS"])
@app.route("/api/<service>/<path:rest>", methods=["GET", "POST", "PATCH", "DELETE", "PUT", "OPTIONS"])
def proxy(service, rest=""):
    return _proxy(service, rest)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)