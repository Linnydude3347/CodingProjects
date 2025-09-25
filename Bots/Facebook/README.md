# Facebook Messenger Bot (Python + Flask)

A minimal, production‑ready **Messenger bot** server in Python. It verifies the webhook, receives messages/events, and replies via the **Meta Graph API**. Includes signature verification and Docker support.

## Features
- **Webhook verify** (`GET /webhook`) and **event receiver** (`POST /webhook`)
- **Signature check** using `APP_SECRET` (`X-Hub-Signature-256`)
- **Send text**, **quick replies**, and **typing indicators**
- Simple command router (`help`, `menu`, echo), **Get Started** postback handling
- **Dockerfile**, **docker-compose**, Procfile, and `.env.example`

## Quickstart
```bash
cd facebook_messenger_bot
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# fill PAGE_ACCESS_TOKEN, VERIFY_TOKEN, APP_SECRET in .env
```

Run locally:
```bash
python app.py
# or with gunicorn
PORT=8080 gunicorn -w 2 -b 0.0.0.0:$PORT app:app
```

### Ngrok (for local webhook)
```bash
ngrok http 8080
# Copy the https URL and set as the Messenger webhook callback with verify token = VERIFY_TOKEN
# Subscribe to 'messages', 'messaging_postbacks', 'messaging_optins' events.
```

## Messenger setup (high level)
1. Create an app at developers.facebook.com and add the **Messenger** product.
2. Connect a **Facebook Page** and generate a **Page Access Token**.
3. In **Webhooks**, set the callback URL to `https://your-domain/webhook` and use your `VERIFY_TOKEN`.
4. Click **Verify and Save**, then **Subscribe** the Page to the webhook events.
5. In Page settings, enable **Get Started** and (optionally) a **Persistent Menu** pointing to postbacks handled here.

## Test
- DM your Page from Messenger.
- Send `help` or `menu` to try quick replies.
- The bot echoes other messages.

## Deploy with Docker
```bash
docker compose up --build
```

## Files
- `app.py` — Flask server: webhook verify + events
- `messenger.py` — Graph API helpers (send text, quick replies, sender actions)
- `security.py` — signature verification (X-Hub-Signature-256)
- `.env.example`, `Dockerfile`, `docker-compose.yml`, `Procfile`, `requirements.txt`, `.gitignore`, `README.md`