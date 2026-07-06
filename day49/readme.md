The xFusionCorp Industries ML platform team is cutting the first end-to-end release on the fraud-detector repo. The release is a three-job Gitea Actions workflow: pull the MLflow credential from Vault, gate on a Great Expectations data-quality checkpoint, and register the trained model in MLflow. All four services—Vault, MLflow, Gitea, the Actions runner—are already running. Your capstone task is to drive the release from its four UIs: stage the credential in Vault, open and merge a pull request in Gitea, then promote the registered model in MLflow.


Each of the four UIs has a button at the top of the lab:

Gitea (port 3000) – gitea-admin / gitea2026. The fraud-detector repo sits on main; a feature branch production-release is pre-pushed. No pull request has been opened yet.
Vault (port 8200) – log in with the token at /root/code/vault-token. The KV v2 engine is enabled at secret/; secret/mlflow is empty.
MLflow UI (port 5000) – the Models page is empty.
Data Docs – rendered by the data-quality job once the workflow runs.
The workflow at .gitea/workflows/production.yml on the production-release branch is complete and correct. It reads Vault KV key mlflow_password, runs the schema_check GE checkpoint, and registers the trained model as fraud-detector in MLflow. It only triggers on pull_request against main.

The end state must include:

secret/mlflow has a non-empty mlflow_password key (any value works).
A pull request exists from production-release → main and has been merged.
The workflow run on that PR's head commit reaches combined status success (all three jobs green).
fraud-detector is registered in MLflow with the production alias pointing at one of its versions.
Each of the four pieces lives behind a different UI and, in a real team, a different owner: Vault (security), Gitea (the dev lead opening + merging the PR), MLflow (the ML engineer promoting the model), Data Docs (the data team reviewing the quality report). The capstone walks all four. Order matters for the first step: stage the Vault secret before opening the PR, otherwise the workflow's very first job fails and the reader has to re-trigger.




name: Production release

on:
  pull_request:
    branches: [main]

env:
  VAULT_ADDR: http://localhost:8200
  MLFLOW_TRACKING_URI: http://localhost:5000

jobs:
  fetch-secret:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Read MLflow password from Vault
        run: |
          TOKEN=$(cat /root/code/vault-token)
          PASSWORD=$(curl -sf -H "X-Vault-Token: $TOKEN" \
            "$VAULT_ADDR/v1/secret/data/mlflow" \
            | python3 -c "import json, sys; print(json.load(sys.stdin)['data']['data']['mlflow_password'])")
          if [ -z "$PASSWORD" ]; then
            echo "::error::Empty password returned from Vault -- is `mlflow_password` staged in `secret/mlflow`?"
            exit 1
          fi
          echo "::notice::Fetched MLflow password from Vault (len=${#PASSWORD})"

  data-quality:
    runs-on: ubuntu-latest
    needs: fetch-secret
    steps:
      - uses: actions/checkout@v4
      - name: Install Great Expectations
        run: pip install --break-system-packages great_expectations pandas numpy
      - name: Run schema checkpoint
        run: python3 -m src.gx_run --checkpoint schema_check

  register-model:
    runs-on: ubuntu-latest
    needs: data-quality
    steps:
      - uses: actions/checkout@v4
      - name: Install deps
        run: pip install --break-system-packages mlflow numpy scikit-learn pandas
      - name: Register model
        env:
          VAULT_KEY_USED: mlflow_password
        run: python3 -m src.register
      - name: Assert a version exists in the registry
        run: |
          python3 -c "
          import mlflow
          mlflow.set_tracking_uri('$MLFLOW_TRACKING_URI')
          client = mlflow.tracking.MlflowClient()
          rm = client.get_registered_model('fraud-detector')
          assert rm.latest_versions, 'fraud-detector has no versions'
          print('Registered model versions:', [v.version for v in rm.latest_versions])
          "




register.py

"""Log a synthetic run to MLflow and register the model.

Called by the `register-model` job in the capstone's production
workflow. The secret pulled from Vault in the earlier job is
attached as a run tag so the audit trail links the deployed model
version back to the credential bundle that produced it.
"""
from __future__ import annotations

import os
import sys

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from mlflow.models.signature import infer_signature
from sklearn.dummy import DummyClassifier

EXPERIMENT = "production-release"
REGISTERED_MODEL = "fraud-detector"


def main() -> int:
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(EXPERIMENT)

    # Deterministic synthetic data -- per MLOps-not-ML, quality
    # numbers are seeded, not earned.
    rng = np.random.default_rng(42)
    X_df = pd.DataFrame(
        rng.normal(size=(80, 4)),
        columns=["amount", "hour", "num_tx_past_day", "category_code"],
    )
    y = (rng.normal(size=80) > 0).astype(int)
    model = DummyClassifier(strategy="most_frequent").fit(X_df, y)
    signature = infer_signature(X_df, model.predict(X_df))

    with mlflow.start_run(run_name="production-release") as run:
        mlflow.log_metric("f1_score", 0.82)
        mlflow.log_metric("accuracy", 0.84)
        mlflow.set_tag("vault_token_source", os.environ.get("VAULT_KEY_USED", "unknown"))

        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            signature=signature,
            input_example=X_df.head(2),
            registered_model_name=REGISTERED_MODEL,
        )
        print(f"Logged run {run.info.run_id[:8]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())




gx_run.py


"""Log a synthetic run to MLflow and register the model.

Called by the `register-model` job in the capstone's production
workflow. The secret pulled from Vault in the earlier job is
attached as a run tag so the audit trail links the deployed model
version back to the credential bundle that produced it.
"""
from __future__ import annotations

import os
import sys

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from mlflow.models.signature import infer_signature
from sklearn.dummy import DummyClassifier

EXPERIMENT = "production-release"
REGISTERED_MODEL = "fraud-detector"


def main() -> int:
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(EXPERIMENT)

    # Deterministic synthetic data -- per MLOps-not-ML, quality
    # numbers are seeded, not earned.
    rng = np.random.default_rng(42)
    X_df = pd.DataFrame(
        rng.normal(size=(80, 4)),
        columns=["amount", "hour", "num_tx_past_day", "category_code"],
    )
    y = (rng.normal(size=80) > 0).astype(int)
    model = DummyClassifier(strategy="most_frequent").fit(X_df, y)
    signature = infer_signature(X_df, model.predict(X_df))

    with mlflow.start_run(run_name="production-release") as run:
        mlflow.log_metric("f1_score", 0.82)
        mlflow.log_metric("accuracy", 0.84)
        mlflow.set_tag("vault_token_source", os.environ.get("VAULT_KEY_USED", "unknown"))

        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            signature=signature,
            input_example=X_df.head(2),
            registered_model_name=REGISTERED_MODEL,
        )
        print(f"Logged run {run.info.run_id[:8]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())


    pyproject.toml


    """Log a synthetic run to MLflow and register the model.

Called by the `register-model` job in the capstone's production
workflow. The secret pulled from Vault in the earlier job is
attached as a run tag so the audit trail links the deployed model
version back to the credential bundle that produced it.
"""
from __future__ import annotations

import os
import sys

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from mlflow.models.signature import infer_signature
from sklearn.dummy import DummyClassifier

EXPERIMENT = "production-release"
REGISTERED_MODEL = "fraud-detector"


def main() -> int:
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(EXPERIMENT)

    # Deterministic synthetic data -- per MLOps-not-ML, quality
    # numbers are seeded, not earned.
    rng = np.random.default_rng(42)
    X_df = pd.DataFrame(
        rng.normal(size=(80, 4)),
        columns=["amount", "hour", "num_tx_past_day", "category_code"],
    )
    y = (rng.normal(size=80) > 0).astype(int)
    model = DummyClassifier(strategy="most_frequent").fit(X_df, y)
    signature = infer_signature(X_df, model.predict(X_df))

    with mlflow.start_run(run_name="production-release") as run:
        mlflow.log_metric("f1_score", 0.82)
        mlflow.log_metric("accuracy", 0.84)
        mlflow.set_tag("vault_token_source", os.environ.get("VAULT_KEY_USED", "unknown"))

        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            signature=signature,
            input_example=X_df.head(2),
            registered_model_name=REGISTERED_MODEL,
        )
        print(f"Logged run {run.info.run_id[:8]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())