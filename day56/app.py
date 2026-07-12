"""Minimal Flask ML API for the CI-pipeline lab. Exposes
`/health` + `/predict`. The predict endpoint implements a
rule-based fraud flag so the test suite has deterministic
expectations."""
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/predict", methods=["POST"])
def predict():
    payload = request.get_json() or {}
    amount = float(payload.get("amount", 0.0))
    hour = int(payload.get("hour", 12))
    is_fraud = int(amount > 500 and (hour >= 22 or hour <= 4))
    return jsonify({"is_fraud": is_fraud}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8086)