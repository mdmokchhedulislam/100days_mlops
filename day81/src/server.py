"""Minimal Flask inference server for the fraud-detector model.

Loads ``artifacts/model.joblib`` on startup and exposes ``/predict``.
The model behind it is the synthetic DummyClassifier from src.train --
§2.5 says model quality is not the lab's subject.
"""
from __future__ import annotations

import os
from pathlib import Path

import joblib
from flask import Flask, jsonify, request

from src.train import train

MODEL_PATH = Path(os.environ.get("MODEL_PATH", "artifacts/model.joblib"))
app = Flask(__name__)

if MODEL_PATH.exists():
    model = joblib.load(MODEL_PATH)
else:
    # Fall back to an in-process train() so the container is self-sufficient
    # when run without a pre-baked model.joblib.
    model = train()["model"]


@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/predict", methods=["POST"])
def predict():
    payload = request.get_json(silent=True) or {}
    row = [payload.get(c, 0.0) for c in (
        "amount", "hour", "num_tx_past_day", "category_code"
    )]
    prediction = int(model.predict([row])[0])
    return jsonify({"is_fraud": prediction}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)