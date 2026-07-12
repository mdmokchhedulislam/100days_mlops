"""Flask fraud-detection prediction API.

Loads the pre-trained RandomForest at `/root/code/serving/model.pkl`
and exposes `/health` + `/predict` over HTTP.
"""
import joblib
import numpy as np
from flask import Flask, jsonify, request

MODEL_PATH = "/root/code/serving/model.pkl"
MODEL = joblib.load(MODEL_PATH)

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    features = np.array([[
        data["amount"],
        data["hour"],
        data["num_tx_past_day"]
    ]])
    prediction = int(MODEL.predict(features)[0])
    return jsonify({"is_fraud": prediction}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8085)