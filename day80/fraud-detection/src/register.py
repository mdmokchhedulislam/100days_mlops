"""Log a run to MLflow and register it under `fraud-detector`.

Reads the tracking URI + token from the environment -- the CI supplies
them through repository secrets. Refuses to run without
``MLFLOW_TRACKING_URI`` set so a missing secret shows up as an explicit
failure in the CI log, not a silent redirect to the default ./mlruns.
"""
from __future__ import annotations

import os
import sys

import mlflow
import mlflow.sklearn
import pandas as pd
from mlflow.models.signature import infer_signature

from src.train import train

EXPERIMENT = "ci-registration"
REGISTERED_MODEL = "fraud-detector"


def main() -> None:
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI")
    if not tracking_uri:
        sys.exit(
            "MLFLOW_TRACKING_URI is not set. Configure a repository "
            "secret of that name (and MLFLOW_TOKEN) in the Gitea "
            "repository Settings, then reference them as env in the "
            "register job."
        )

    # Token is not validated server-side in this lab, but we read it
    # so a missing secret still surfaces as a failure.
    token = os.environ.get("MLFLOW_TOKEN")
    if not token:
        sys.exit("MLFLOW_TOKEN is not set. Add it as a repository secret.")

    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(EXPERIMENT)

    result = train()
    model = result["model"]
    metrics = result["metrics"]

    rng_features = result["model"].__class__.__name__
    print(f"Training complete: {rng_features}, metrics={metrics}")

    X_example = pd.DataFrame(
        [[0.0, 0.0, 0.0, 0.0]],
        columns=["amount", "hour", "num_tx_past_day", "category_code"],
    )
    y_example = model.predict(X_example)

    with mlflow.start_run(run_name="ci-registration") as run:
        for k, v in metrics.items():
            if isinstance(v, (int, float)):
                mlflow.log_metric(k, float(v))
        signature = infer_signature(X_example, y_example)
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            signature=signature,
            input_example=X_example,
            registered_model_name=REGISTERED_MODEL,
        )
        print(
            f"Registered {REGISTERED_MODEL} from run {run.info.run_id[:8]}..."
        )


if __name__ == "__main__":
    main()