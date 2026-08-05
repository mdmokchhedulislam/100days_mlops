"""Metric emitter for the Monitoring-section labs.

Exposes a Prometheus metrics endpoint carrying the ML-serving signals:
  - `flask_http_request_total{version}`     - request counter, labelled by model version.
  - `prediction_accuracy`                   - gauge, random walk around 0.85.
  - `data_drift_score{column}`              - per-feature PSI, computed by the
                                              Evidently drift scorer
                                              (`../drift/drift_scorer.py`) and
                                              read from the bind-mounted
                                              scores file.
  - `evidently_drift_share`                 - share of feature columns Evidently
                                              flags as drifted in the latest window.
  - `model_inference_duration_seconds`      - latency histogram.

A background thread refreshes the gauges and increments the counters
every 5 seconds so Grafana panels built on top of these metrics see
real motion rather than flat lines. Until the Evidently scorer has
produced its first scores file, the drift gauges fall back to a
deterministic random walk so panels never flatline.
"""
import json
import os
import random
import threading
import time

from flask import Flask, jsonify
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest
from prometheus_client import CONTENT_TYPE_LATEST

app = Flask(__name__)

REGISTRY = CollectorRegistry()

DRIFT_SCORES_PATH = os.environ.get("DRIFT_SCORES_PATH", "/drift/drift_scores.json")

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
    "Population Stability Index (PSI) per feature column, "
    "scored by the Evidently drift scorer.",
    labelnames=["column"],
    registry=REGISTRY,
)

EVIDENTLY_DRIFT_SHARE = Gauge(
    "evidently_drift_share",
    "Share of feature columns Evidently flags as drifted "
    "in the latest scoring window.",
    registry=REGISTRY,
)

INFERENCE_LATENCY = Histogram(
    "model_inference_duration_seconds",
    "End-to-end inference duration in seconds.",
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
    registry=REGISTRY,
)


def _read_evidently_scores():
    """Latest per-column scores from the Evidently drift scorer.

    Returns ({column: psi}, drift_share), or None while the scorer has
    not produced a readable scores file yet.
    """
    try:
        with open(DRIFT_SCORES_PATH) as fh:
            payload = json.load(fh)
        scores = {
            str(column): float(value)
            for column, value in (payload.get("drift_scores") or {}).items()
        }
        if not scores:
            return None
        return scores, float(payload.get("drift_share", 0.0))
    except (OSError, ValueError):
        return None


def _nudge_metrics() -> None:
    random.seed(42)
    accuracy = 0.85
    fallback_drift = {"amount": 0.10, "hour": 0.12, "num_tx_past_day": 0.08}
    while True:
        # Simulate a handful of requests across two model versions.
        for version in ("v1", "v1", "v1", "v2"):
            REQUEST_TOTAL.labels(version=version, endpoint="/predict", method="POST").inc()
            INFERENCE_LATENCY.observe(random.uniform(0.005, 0.15))

        # Random-walk the accuracy around 0.85, clipped to [0.70, 0.95].
        accuracy = max(0.70, min(0.95, accuracy + random.uniform(-0.02, 0.02)))
        PREDICTION_ACCURACY.set(accuracy)

        # Republish the Evidently-computed drift scores; fall back to a
        # random walk only while the scorer's first file is pending.
        evidently = _read_evidently_scores()
        if evidently is not None:
            scores, drift_share = evidently
            for column, score in scores.items():
                DATA_DRIFT_SCORE.labels(column=column).set(score)
            EVIDENTLY_DRIFT_SHARE.set(drift_share)
        else:
            for column in fallback_drift:
                fallback_drift[column] = max(
                    0.01,
                    min(0.60, fallback_drift[column] + random.uniform(-0.02, 0.03)),
                )
                DATA_DRIFT_SCORE.labels(column=column).set(fallback_drift[column])

        time.sleep(5)


@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/metrics")
def metrics():
    return generate_latest(REGISTRY), 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    threading.Thread(target=_nudge_metrics, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)