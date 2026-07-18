"""A/B-testing Flask server for the fraud-detection model.

Loads two model versions (`model_v1.pkl` + `model_v2.pkl`) and
routes incoming traffic between them: the bulk of requests must
reach the stable v1, a small slice goes to the candidate v2 so
its predictions can be compared against v1 for drift.

The release checklist requires an 80 / 20 split (v1 / v2) and a
`model_version` field on every response so downstream monitoring
can attribute each prediction to the model that produced it.
"""
import random

import joblib
import numpy as np
from flask import Flask, jsonify, request

MODEL_V1 = joblib.load("/root/code/serving/model_v1.pkl")
MODEL_V2 = joblib.load("/root/code/serving/model_v2.pkl")

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/predict", methods=["POST"])
def predict():
    payload = request.get_json() or {}

    features = np.array([[
        float(payload.get("amount", 0.0)),
        int(payload.get("hour", 0)),
        int(payload.get("num_tx_past_day", 0)),
    ]])

    # A/B Routing: 80% -> v1, 20% -> v2
    if random.random() < 0.8:
        model = MODEL_V1
        model_version = "v1"
    else:
        model = MODEL_V2
        model_version = "v2"

    # Make prediction
    prediction = int(model.predict(features)[0])

    # Return prediction with model version
    return jsonify({
        "is_fraud": prediction,
        "model_version": model_version
    }), 200
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8085)