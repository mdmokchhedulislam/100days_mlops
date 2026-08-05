"""Drift-triggered retrain setup for Day 73.

Runs once at lab startup and leaves the MLflow registry in a
champion/challenger state:

  - `fraud-detector` v1  — the incumbent, currently serving
    (f1_score 0.71), with the `production` alias attached.
  - `fraud-detector` v2  — the challenger the drift-triggered
    retrain just produced (f1_score 0.82), registered but NOT
    promoted.

The reader authors the promotion gate (`promote.py`) that decides
whether v2 should replace v1 as `production`. This script does NOT
promote anything beyond seeding the incumbent alias.
"""
import os
from datetime import datetime

import mlflow
import mlflow.sklearn
import pandas as pd
from mlflow import MlflowClient
from mlflow.models.signature import infer_signature
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier

TRACKING_URI = "http://localhost:5000"
EXPERIMENT = "retraining-monitor"
REGISTERED_MODEL = "fraud-detector"
LOG_PATH = "/root/code/logs/monitoring.log"

# Two candidate models. f1 values are fixed so the registry the reader
# sees is deterministic; the challenger (v2) beats the incumbent (v1).
# Model quality itself is irrelevant here -- the teaching point is the
# promotion gate, so the metrics are synthetic.
CANDIDATES = [
    {"run_name": "incumbent", "f1": 0.71, "drift_share": 0.05},
    {"run_name": "retrained-challenger", "f1": 0.82, "drift_share": 0.48},
]


def log(msg: str) -> None:
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line, flush=True)
    with open(LOG_PATH, "a") as fh:
        fh.write(line + "\n")


def main() -> None:
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT)

    X, y = make_classification(
        n_samples=400, n_features=4, n_informative=3, n_redundant=0,
        random_state=42,
    )
    columns = ["amount", "hour", "num_tx_past_day", "category_code"]
    X_df = pd.DataFrame(X, columns=columns)
    y_s = pd.Series(y, name="is_fraud")
    signature = infer_signature(X_df, y_s)

    client = MlflowClient(tracking_uri=TRACKING_URI)

    for cand in CANDIDATES:
        with mlflow.start_run(run_name=cand["run_name"]):
            model = RandomForestClassifier(n_estimators=20, random_state=42)
            model.fit(X_df, y_s)
            mlflow.log_metric("drift_share", cand["drift_share"])
            mlflow.log_metric("f1_score", cand["f1"])
            mlflow.sklearn.log_model(
                sk_model=model,
                artifact_path="model",
                signature=signature,
                input_example=X_df.head(2),
                registered_model_name=REGISTERED_MODEL,
            )
        log(f"Registered {REGISTERED_MODEL} ({cand['run_name']}, f1={cand['f1']})")

    # Seed the incumbent: point `production` at v1. The challenger (v2)
    # is left unpromoted -- the reader's gate decides its fate.
    client.set_registered_model_alias(REGISTERED_MODEL, "production", "1")
    log("Set production -> v1 (incumbent). Challenger v2 awaits the promotion gate.")


if __name__ == "__main__":
    main()