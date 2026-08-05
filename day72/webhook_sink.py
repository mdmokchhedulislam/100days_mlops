"""Webhook sink for the Day 72 Grafana alerting lab.

Accepts POSTs on `/hook` and writes each payload to stdout + a rolling
log file at `/var/log/sink/alerts.log`. Grafana's 'Test' button and any
fired notification policy that routes here hits this exact URL.
"""
import json
import logging
import os
import sys
from datetime import datetime, timezone

from flask import Flask, jsonify, request

LOG_DIR = "/var/log/sink"
LOG_PATH = os.path.join(LOG_DIR, "alerts.log")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")
log = logging.getLogger("webhook-sink")

app = Flask(__name__)


@app.route("/hook", methods=["POST"])
def hook():
    payload = request.get_json(silent=True) or {}
    entry = {
        "received_at": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }
    with open(LOG_PATH, "a") as fh:
        fh.write(json.dumps(entry) + "\n")
    log.info("received alert: %s", json.dumps(payload)[:400])
    return jsonify({"status": "ok"}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "up"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)