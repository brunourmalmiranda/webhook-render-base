import os
import uuid
from datetime import datetime, timezone
from flask import Flask, request, jsonify

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

APP_NAME = os.getenv("APP_NAME", "webhook-render-base")
WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN", "")

def now_iso():
    return datetime.now(timezone.utc).isoformat()

@app.get("/health")
def health():
    return jsonify(
        ok=True,
        service=APP_NAME,
        token_configured=bool(WEBHOOK_TOKEN),
        ts=now_iso()
    )

@app.post("/webhook")
def webhook():
    request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())

    # auth
    token = request.headers.get("X-Webhook-Token", "")
    if WEBHOOK_TOKEN and token != WEBHOOK_TOKEN:
        app.logger.warning("unauthorized request_id=%s ip=%s", request_id, request.remote_addr)
        return jsonify(ok=False, error="unauthorized", request_id=request_id), 401

    # json parsing
    data = request.get_json(silent=True)
    if data is None:
        return jsonify(ok=False, error="invalid_json", request_id=request_id), 400

    # exemplo de validação mínima (ajusta depois ao teu schema real)
    event = data.get("event")
    if not event:
        return jsonify(ok=False, error="missing_event", request_id=request_id), 422

    app.logger.info("webhook received request_id=%s event=%s", request_id, event)

    return jsonify(ok=True, request_id=request_id, received=data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
