# Microservices Starter — Docker + Flask + React

A working starter that spins up two Flask microservices (`users`, `tasks`), a lightweight API gateway, and a React (Vite) frontend served by Nginx — all orchestrated with Docker Compose.

## What you get
- **Users service (Flask + SQLite)** — create/list/get users
- **Tasks service (Flask + SQLite)** — CRUD tasks (optionally linked to a user)
- **Gateway (Flask)** — routes `/api/users/*` and `/api/tasks/*` to the respective services
- **Frontend (React + Vite + Nginx)** — simple UI that talks to the gateway; Nginx proxies `/api/*` to the gateway (no CORS headaches)

## Quickstart
```bash
cd microservices-flask-react
cp .env.example .env   # optional; defaults are okay
docker compose up --build
# Frontend: http://localhost:3000
# Gateway:  http://localhost:8080 (proxied by frontend at /api)
```

## Endpoints
- `GET /api/users` — list users
- `POST /api/users` — create user `{ "username": "alice" }`
- `GET /api/users/<id>` — get user

- `GET /api/tasks` — list tasks (filter: `?user_id=1`)
- `POST /api/tasks` — create `{ "title": "Buy milk", "user_id": 1 }`
- `PATCH /api/tasks/<id>` — partial update `{ "completed": true }`
- `DELETE /api/tasks/<id>` — delete

## Dev notes
- SQLite files are stored in Docker volumes (`users_data`, `tasks_data`).
- The frontend makes calls to `/api/*`; Nginx forwards those to `gateway:8080` inside the network.
- Change ports via `.env` if you like.