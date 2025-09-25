import os, logging
from typing import List, Dict
import requests

log = logging.getLogger("fb-bot")

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN", "")
GRAPH_VERSION = os.getenv("GRAPH_VERSION", "v19.0")
GRAPH_URL = f"https://graph.facebook.com/{GRAPH_VERSION}/me/messages"

def _headers():
    return {"Content-Type": "application/json"}

def _params():
    return {"access_token": PAGE_ACCESS_TOKEN}

def send_action(psid: str, action: str = "typing_on"):
    data = {"recipient": {"id": psid}, "sender_action": action}
    try:
        r = requests.post(GRAPH_URL, headers=_headers(), params=_params(), json=data, timeout=10)
        if r.status_code >= 400:
            log.warning("action error %s %s", r.status_code, r.text)
    except Exception as e:
        log.exception("send_action error: %s", e)

def send_text(psid: str, text: str):
    data = {"recipient": {"id": psid}, "message": {"text": text[:640]}}
    try:
        r = requests.post(GRAPH_URL, headers=_headers(), params=_params(), json=data, timeout=10)
        if r.status_code >= 400:
            log.warning("send_text error %s %s", r.status_code, r.text)
    except Exception as e:
        log.exception("send_text error: %s", e)

def send_quick_replies(psid: str, text: str, options: List[Dict[str, str]]):
    # options: [{"title":"Help","payload":"help"}, ...]
    replies = [
        {"content_type": "text", "title": opt["title"][:20], "payload": opt["payload"][:100]}
        for opt in options
    ]
    data = {"recipient": {"id": psid},
            "message": {"text": text[:640], "quick_replies": replies}}
    try:
        r = requests.post(GRAPH_URL, headers=_headers(), params=_params(), json=data, timeout=10)
        if r.status_code >= 400:
            log.warning("send_quick_replies error %s %s", r.status_code, r.text)
    except Exception as e:
        log.exception("send_quick_replies error: %s", e)

def get_psid_from_event(event: dict):
    sender = event.get("sender", {})
    return sender.get("id")