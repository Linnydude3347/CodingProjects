import os, hmac, hashlib
from flask import Request

APP_SECRET = os.getenv("APP_SECRET", "")

def verify_signature(req: Request) -> bool:
    """Verify X-Hub-Signature-256 HMAC of the raw request body.
    If APP_SECRET isn't set, skip verification (dev mode).
    """
    if not APP_SECRET:
        return True
    sig = req.headers.get("X-Hub-Signature-256", "")
    if not sig.startswith("sha256="):
        return False
    provided = sig.split("=", 1)[1]
    digest = hmac.new(APP_SECRET.encode("utf-8"), req.get_data(), hashlib.sha256).hexdigest()
    # constant-time compare
    try:
        return hmac.compare_digest(provided, digest)
    except Exception:
        return False