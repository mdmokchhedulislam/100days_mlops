"""Recommendation model stub."""
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "recommend"}), 200


@app.route("/predict", methods=["POST"])
def predict():
    payload = request.get_json() or {}
    user_id = int(payload.get("user_id", 0))
    items = [f"item_{(user_id + i) % 10}" for i in range(3)]
    return jsonify({"service": "recommend", "items": items}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)