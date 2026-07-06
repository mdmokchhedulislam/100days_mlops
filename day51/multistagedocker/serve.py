"""Minimal Flask feature server for the trained fraud-detection
RandomForest. Exposes `/predict` + `/health`."""
import joblib
import numpy as np
from flask import Flask, jsonify, request

app = Flask(__name__)
model = joblib.load("/app/model.pkl")


@app.route("/predict", methods=["POST"])
def predict():
    payload = request.get_json()
    features = np.array([[
        payload["amount"],
        payload["hour"],
        payload["num_tx_past_day"],
    ]])
    pred = int(model.predict(features)[0])
    return jsonify({"is_fraud": pred})


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)