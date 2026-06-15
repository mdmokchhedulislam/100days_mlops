The xFusionCorp Industries ML platform team's audit pipeline depends on run-to-run reproducibility—identical code and identical data must produce identical metrics. The fraud-detection trainer at /root/code/fraud-detection/src/models/train.py currently fails this guarantee: consecutive runs on the same dataset report different accuracy and F1 values. Your task is to make the trainer deterministic so the check_determinism.sh probe succeeds.


The MLflow tracking server is already running on port 5000. The MLflow UI button at the top of the lab can be opened to confirm—the dashboard loads with an empty fraud-detection-repro experiment.

The project layout under /root/code/fraud-detection/:

data/train.csv – A pre-generated 200-row synthetic binary classification dataset. The same file is read by both runs.
src/models/train.py – The trainer (non-deterministic on purpose). Every non-reproducibility concern is correctly wired; only the seed discipline is missing.
check_determinism.sh – Executable probe that runs the trainer three times, writes reports/metrics_run_1.json, reports/metrics_run_2.json, and reports/metrics_run_3.json, and diffs each adjacent pair. Exits 0 only when all three JSON files are byte-identical.
models/ – Where each run persists its serialised model.
reports/ – Where each run writes its metrics JSON.
Running /root/code/fraud-detection/check_determinism.sh currently prints FAIL: the three runs did not produce byte-identical metrics. followed by a diff. Open src/models/train.py in the VS Code editor, add the seed discipline required by scikit-learn's randomised operations, save, and re-run the probe.

The end state must include:

check_determinism.sh exits with status 0.
At least two runs exist in the fraud-detection-repro experiment, named repro-run-1 and repro-run-2, with identical metrics.accuracy and metrics.f1_score values (to at least six decimal places).
All three probe runs produce byte-identical metrics JSON files at reports/metrics_run_1.json, reports/metrics_run_2.json, and reports/metrics_run_3.json – Covering accuracy, f1_score, and the model's feature_importances.
Only train.py needs to change. The probe, the dataset, and the MLflow wiring are all correct and must not be modified.













solve trian.py

"""Training script for the fraud-detection model.

This scaffold is deliberately non-deterministic — running it twice
produces different metrics on the same input data. A reproducibility
fix is required so downstream tooling (checksum-based caching,
experiment comparison, audit trails) can rely on run-to-run
stability.

Every non-reproducibility concern is already handled here — data
loading, split, training, MLflow logging, model persistence, and
metrics serialisation. Edit this file to add the seed discipline
that makes the run reproducible; do not change anything else.
"""
import os
import json
import joblib
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

TRAIN_CSV = "/root/code/fraud-detection/data/train.csv"
MODEL_PATH = "/root/code/fraud-detection/models/model.pkl"
METRICS_OUT = os.environ.get(
    "METRICS_OUT", "/root/code/fraud-detection/reports/last_metrics.json"
)
RUN_NAME = os.environ.get("MLFLOW_RUN_NAME", "repro-run")

# একটি নির্দিষ্ট সিড (Seed) ডিফাইন করা হলো রিপ্রোডুসিবিলিটির জন্য
SEED = 42

def main():
    df = pd.read_csv(TRAIN_CSV)
    X = df.drop(columns=["is_fraud"])
    y = df["is_fraud"]

    # ১. এখানে random_state=SEED যোগ করা হয়েছে
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=SEED
    )

    # ২. এখানেও random_state=SEED যোগ করা হয়েছে
    model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=SEED)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    metrics = {
        "accuracy": round(accuracy_score(y_test, preds), 6),
        "f1_score": round(f1_score(y_test, preds), 6),
    }

    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("fraud-detection-repro")
    with mlflow.start_run(run_name=RUN_NAME):
        # এই লাইনটি ঠিক করা হয়েছে ("max_depth=5" এর বদলে "max_depth" দেওয়া হয়েছে)
        mlflow.log_params({"n_estimators": 100, "max_depth": 5})
        for key, value in metrics.items():
            mlflow.log_metric(key, value)
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        joblib.dump(model, MODEL_PATH)
        mlflow.sklearn.log_model(model, name="model")

    # Probe payload is a superset of `metrics` plus feature_importances.
    # The list lives here — not in `metrics` — because MLflow's
    # log_metric only accepts scalars. feature_importances_ is an
    # average over 100 trees' bootstrap + feature-subset randomness;
    # two unseeded runs can coincidentally produce the same accuracy
    # / f1 bucket on a 40-row stratified test set, but their importance
    # triplets essentially never match, so the probe's byte-diff can
    # distinguish a real deterministic run from a lucky collision.
    probe_payload = {
        **metrics,
        "feature_importances": model.feature_importances_.tolist(),
    }
    os.makedirs(os.path.dirname(METRICS_OUT), exist_ok=True)
    with open(METRICS_OUT, "w") as f:
        json.dump(probe_payload, f, indent=2, sort_keys=True)

    print(f"{RUN_NAME}: accuracy={metrics['accuracy']}, f1_score={metrics['f1_score']}")


if __name__ == "__main__":
    main()



    unsolve:

    """Training script for the fraud-detection model.

This scaffold is deliberately non-deterministic — running it twice
produces different metrics on the same input data. A reproducibility
fix is required so downstream tooling (checksum-based caching,
experiment comparison, audit trails) can rely on run-to-run
stability.

Every non-reproducibility concern is already handled here — data
loading, split, training, MLflow logging, model persistence, and
metrics serialisation. Edit this file to add the seed discipline
that makes the run reproducible; do not change anything else.
"""
import os
import json
import joblib
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

TRAIN_CSV = "/root/code/fraud-detection/data/train.csv"
MODEL_PATH = "/root/code/fraud-detection/models/model.pkl"
METRICS_OUT = os.environ.get(
    "METRICS_OUT", "/root/code/fraud-detection/reports/last_metrics.json"
)
RUN_NAME = os.environ.get("MLFLOW_RUN_NAME", "repro-run")


def main():
    df = pd.read_csv(TRAIN_CSV)
    X = df.drop(columns=["is_fraud"])
    y = df["is_fraud"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y
    )

    model = RandomForestClassifier(n_estimators=100, max_depth=5)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    metrics = {
        "accuracy": round(accuracy_score(y_test, preds), 6),
        "f1_score": round(f1_score(y_test, preds), 6),
    }

    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("fraud-detection-repro")
    with mlflow.start_run(run_name=RUN_NAME):
        mlflow.log_params({"n_estimators": 100, "max_depth": 5})
        for key, value in metrics.items():
            mlflow.log_metric(key, value)
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        joblib.dump(model, MODEL_PATH)
        mlflow.sklearn.log_model(model, name="model")

    # Probe payload is a superset of `metrics` plus feature_importances.
    # The list lives here — not in `metrics` — because MLflow's
    # log_metric only accepts scalars. feature_importances_ is an
    # average over 100 trees' bootstrap + feature-subset randomness;
    # two unseeded runs can coincidentally produce the same accuracy
    # / f1 bucket on a 40-row stratified test set, but their importance
    # triplets essentially never match, so the probe's byte-diff can
    # distinguish a real deterministic run from a lucky collision.
    probe_payload = {
        **metrics,
        "feature_importances": model.feature_importances_.tolist(),
    }
    os.makedirs(os.path.dirname(METRICS_OUT), exist_ok=True)
    with open(METRICS_OUT, "w") as f:
        json.dump(probe_payload, f, indent=2, sort_keys=True)

    print(f"{RUN_NAME}: accuracy={metrics['accuracy']}, f1_score={metrics['f1_score']}")


if __name__ == "__main__":
    main()




    <!-- shell -->

    #!/usr/bin/env bash
# Determinism probe for the fraud-detection trainer.
#
# Runs the training script three times back to back, writes each
# run's metrics to a separate JSON file, and compares all three
# files byte for byte. Three runs (rather than two) drive the
# probability of a spurious "pass" from two unseeded runs
# coincidentally landing on the same metrics down to roughly 1 %.
# Exits 0 when all three files are identical (reproducible training),
# non-zero otherwise, and prints a diff for diagnosis.
set -u

TRAIN_PY="/root/code/fraud-detection/src/models/train.py"
REPORTS="/root/code/fraud-detection/reports"
METRICS_1="${REPORTS}/metrics_run_1.json"
METRICS_2="${REPORTS}/metrics_run_2.json"
METRICS_3="${REPORTS}/metrics_run_3.json"

mkdir -p "${REPORTS}"
rm -f "${METRICS_1}" "${METRICS_2}" "${METRICS_3}"

echo "=== running train.py (repro-run-1)"
METRICS_OUT="${METRICS_1}" MLFLOW_RUN_NAME="repro-run-1" python3 "${TRAIN_PY}" || {
  echo "FAIL: first run errored out — see stderr above."
  exit 2
}

echo "=== running train.py (repro-run-2)"
METRICS_OUT="${METRICS_2}" MLFLOW_RUN_NAME="repro-run-2" python3 "${TRAIN_PY}" || {
  echo "FAIL: second run errored out — see stderr above."
  exit 2
}

echo "=== running train.py (repro-run-3)"
METRICS_OUT="${METRICS_3}" MLFLOW_RUN_NAME="repro-run-3" python3 "${TRAIN_PY}" || {
  echo "FAIL: third run errored out — see stderr above."
  exit 2
}

if diff -q "${METRICS_1}" "${METRICS_2}" >/dev/null \
  && diff -q "${METRICS_2}" "${METRICS_3}" >/dev/null; then
  echo "OK: all three runs produced byte-identical metrics."
  exit 0
fi

echo "FAIL: the three runs did not produce byte-identical metrics."
echo
echo "--- diff ${METRICS_1} ${METRICS_2} ---"
diff "${METRICS_1}" "${METRICS_2}" || true
echo "--- diff ${METRICS_2} ${METRICS_3} ---"
diff "${METRICS_2}" "${METRICS_3}" || true
echo "-------------------------------------"
exit 1