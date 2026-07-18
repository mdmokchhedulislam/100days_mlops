"""Flask async prediction server backed by Redis.

Incoming `POST /predict-async` requests return a `task_id` and
kick off prediction on a background thread. The worker writes the
result to Redis under `result:<task_id>` with a 600-second TTL.
Clients poll `GET /result/<task_id>` to retrieve the stored
classification once the worker has finished.
"""

import threading
import time
import uuid

import joblib
import numpy as np
import redis
from flask import Flask, jsonify, request

MODEL = joblib.load("/root/code/serving/model.pkl")
REDIS = redis.Redis(host="localhost", port=6379, decode_responses=True)

RESULT_KEY = "result:{task_id}"
RESULT_TTL_SECONDS = 600

app = Flask(__name__)


def _run_prediction(task_id: str, features) -> None:
    # Simulate some processing time
    time.sleep(0.3)

    # Run prediction
    is_fraud = int(MODEL.predict(np.array([features]))[0])

    # Store result in Redis with TTL
    key = RESULT_KEY.format(task_id=task_id)
    REDIS.set(
        key,
        is_fraud,
        ex=RESULT_TTL_SECONDS
    )


@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/predict-async", methods=["POST"])
def predict_async():
    payload = request.get_json() or {}

    features = [
        float(payload.get("amount", 0.0)),
        int(payload.get("hour", 0)),
        int(payload.get("num_tx_past_day", 0)),
    ]

    task_id = uuid.uuid4().hex

    threading.Thread(
        target=_run_prediction,
        args=(task_id, features),
        daemon=True,
    ).start()

    return jsonify({"task_id": task_id}), 202


@app.route("/result/<task_id>")
def result(task_id):
    key = RESULT_KEY.format(task_id=task_id)

    value = REDIS.get(key)

    if value is not None:
        return jsonify({
            "task_id": task_id,
            "is_fraud": int(value)
        }), 200

    return jsonify({
        "task_id": task_id,
        "status": "pending"
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8085)