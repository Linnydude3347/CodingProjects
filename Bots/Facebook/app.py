import os, logging
from flask import Flask, request, jsonify, abort
from dotenv import load_dotenv
from messenger import send_text, send_quick_replies, send_action, get_psid_from_event
from security import verify_signature

load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("fb-bot")

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "dev-verify")
DEBUG = os.getenv("DEBUG", "false").lower() in ("1","true","yes","y")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8080"))

@app.get("/")
def root():
    return {"ok": True, "service": "facebook-messenger-bot"}

@app.get("/webhook")
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403

@app.post("/webhook")
def webhook():
    # Verify signature if provided
    if not verify_signature(request):
        app.logger.warning("Invalid signature")
        abort(403)

    payload = request.get_json(force=True, silent=True) or {}
    if payload.get("object") != "page":
        return jsonify({"status": "ignored"}), 200

    for entry in payload.get("entry", []):
        for event in entry.get("messaging", []):
            psid = get_psid_from_event(event)
            if not psid:
                continue

            # Mark seen + typing
            send_action(psid, "mark_seen")
            send_action(psid, "typing_on")

            if "message" in event:
                msg = event["message"]
                text = (msg.get("text") or "").strip()
                quick = msg.get("quick_reply", {}).get("payload")
                if quick:
                    # quick-reply payloads handle like commands
                    text = quick

                if text.lower() in ("help", "/help"):
                    send_text(psid, "Commands: 'help', 'menu', or say anything for an echo.")
                elif text.lower() in ("menu", "/menu"):
                    send_quick_replies(psid, "What do you need?",
                        [
                            {"title": "Help", "payload": "help"},
                            {"title": "Docs", "payload": "docs"},
                            {"title": "Echo", "payload": "echo"}
                        ]
                    )
                elif text.lower() == "docs":
                    send_text(psid, "Messenger docs: https://developers.facebook.com/docs/messenger-platform/")
                elif text.lower() == "echo":
                    send_text(psid, "Echo mode on. Reply with any text.")
                else:
                    # default echo
                    send_text(psid, f"You said: {text or '[no text]'}")

            elif "postback" in event:
                payload = (event["postback"].get("payload") or "").lower()
                if payload in ("get_started", "start"):
                    send_text(psid, "Welcome! Type 'help' to see commands.")
                else:
                    send_text(psid, f"Postback: {payload}")

            send_action(psid, "typing_off")

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)