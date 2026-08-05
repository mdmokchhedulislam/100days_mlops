"""Metric emitter for the Monitoring-section labs.

Exposes a Prometheus `/metrics` endpoint carrying ML-serving signals:
  - `flask_http_request_total{version}`     — request counter.
  - `prediction_accuracy`                   — gauge.
  - `data_drift_score{column}`              — per-feature drift.
  - `model_inference_duration_seconds`      — latency histogram.
  - `fraud_amount_usd_total{version}`       — total fraudulent amount by model version.
"""

import random
import threading
import time

from flask import Flask, jsonify
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

app = Flask(__name__)

REGISTRY = CollectorRegistry()

REQUEST_TOTAL = Counter(
    "flask_http_request_total",
    "Total HTTP requests handled, labelled by model version.",
    labelnames=["version", "endpoint", "method"],
    registry=REGISTRY,
)

PREDICTION_ACCURACY = Gauge(
    "prediction_accuracy",
    "Rolling prediction accuracy on the shadow eval set.",
    registry=REGISTRY,
)

DATA_DRIFT_SCORE = Gauge(
    "data_drift_score",
    "Population Stability Index (PSI) per feature column.",
    labelnames=["column"],
    registry=REGISTRY,
)

INFERENCE_LATENCY = Histogram(
    "model_inference_duration_seconds",
    "End-to-end inference duration in seconds.",
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
    registry=REGISTRY,
)

# New metric
FRAUD_AMOUNT_USD_TOTAL = Counter(
    "fraud_amount_usd_total",
    "Total fraudulent transaction amount in USD.",
    labelnames=["version"],
    registry=REGISTRY,
)


def _nudge_metrics() -> None:
    random.seed(42)

    accuracy = 0.85
    drift = {
        "amount": 0.10,
        "hour": 0.12,
        "num_tx_past_day": 0.08,
    }

    while True:
        # Simulate requests across model versions
        for version in ("v1", "v1", "v1", "v2"):
            REQUEST_TOTAL.labels(
                version=version,
                endpoint="/predict",
                method="POST",
            ).inc()

            INFERENCE_LATENCY.observe(random.uniform(0.005, 0.15))

            # Increment fraud amount for each version
            FRAUD_AMOUNT_USD_TOTAL.labels(version=version).inc(
                random.uniform(10, 200)
            )

        # Random walk accuracy
        accuracy = max(
            0.70,
            min(0.95, accuracy + random.uniform(-0.02, 0.02)),
        )
        PREDICTION_ACCURACY.set(accuracy)

        # Random walk drift scores
        for column in drift:
            drift[column] = max(
                0.01,
                min(
                    0.60,
                    drift[column] + random.uniform(-0.02, 0.03),
                ),
            )

            DATA_DRIFT_SCORE.labels(column=column).set(drift[column])

        time.sleep(5)


@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/metrics")
def metrics():
    return (
        generate_latest(REGISTRY),
        200,
        {"Content-Type": CONTENT_TYPE_LATEST},
    )


if __name__ == "__main__":
    threading.Thread(target=_nudge_metrics, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)