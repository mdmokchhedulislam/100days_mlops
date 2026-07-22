"""Production fraud-detection serving API.

Flask app wired with:
  - GET  /health           — liveness check.
  - POST /predict          — score one transaction; Redis-backed
                             per-IP rate limit (100 req / min).
  - GET  /metrics          — Prometheus scrape endpoint, exposed
                             by `prometheus_flask_exporter`.

The observability stack scrapes `/metrics` every 5 seconds; the
container listens on port 5000 inside the Docker network, and
nginx fronts the public 8085 surface.
"""
import joblib
import numpy as np
import redis
from flask import Flask, jsonify, request
from prometheus_flask_exporter import PrometheusMetrics

MODEL = joblib.load("/app/model.pkl")
REDIS = redis.Redis(host="redis", port=6379, decode_responses=True)

RATE_LIMIT = 100
RATE_WINDOW_SECONDS = 60

app = Flask(__name__)
metrics = PrometheusMetrics(app)


@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/predict", methods=["POST"])
def predict():
    ip = request.remote_addr or "unknown"
    key = f"ratelimit:{ip}"
    try:
        count = REDIS.incr(key)
        if count == 1:
            REDIS.expire(key, RATE_WINDOW_SECONDS)
    except redis.RedisError:
        count = 0

    if count > RATE_LIMIT:
        return jsonify({"error": "rate limit exceeded"}), 429

    payload = request.get_json() or {}
    features = np.array([[
        float(payload.get("amount", 0.0)),
        int(payload.get("hour", 0)),
        int(payload.get("num_tx_past_day", 0)),
    ]])
    return jsonify({"is_fraud": int(MODEL.predict(features)[0])}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8085)