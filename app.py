import os
from flask import Flask, request, jsonify

from dotenv import load_dotenv
load_dotenv()  # lê o ficheiro .env na raiz do projecto

app = Flask(__name__)

APP_NAME = os.getenv("APP_NAME", "webhook-render-base")
WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN", "")

@app.get("/health")
def health():
    # nunca devolvas o token; só confirmo se existe ou não
    return jsonify(ok=True, service=APP_NAME, token_configured=bool(WEBHOOK_TOKEN))

@app.post("/webhook")
def webhook():
    # valida token (header)
    token = request.headers.get("X-Webhook-Token", "")
    if WEBHOOK_TOKEN and token != WEBHOOK_TOKEN:
        return jsonify(ok=False, error="unauthorized"), 401

    data = request.get_json(silent=True) or {}
    return jsonify(ok=True, received=data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
