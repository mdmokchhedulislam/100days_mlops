The xFusionCorp Industries ML platform team ships a full fraud-detection training pipeline—data validation, Optuna tuning across two model families, model selection against a release threshold, Model Registry registration with a release-lane alias, and a consolidated training report—all wired together behind a single make train-pipeline command. The pre-staged system does not currently run end-to-end: each make train-pipeline invocation surfaces a wiring issue, and the integration across the Makefile, src/select_model.py, and src/register.py needs attention before the release checklist passes. Your task is to correct the wiring so make train-pipeline runs cleanly end-to-end, the MLflow Model Registry holds a fraud-detector version under the staging alias, and reports/training_report.json aggregates every upstream artefact.


The MLflow tracking server is already running on port 5000. The MLflow UI button at the top of the lab can be opened to confirm—the dashboard loads with an empty fraud-detection-tuning experiment.

The project layout under /root/code/fraud-detection/:

data/train.csv – The 200-row synthetic binary-classification dataset the rest of the Training section uses.
src/validate_data.py – Schema + null-check gate. Writes reports/validation_status.json. Correct.
src/tune.py – Runs 10 Optuna trials across RandomForest and GradientBoosting, each logged as an MLflow run tagged with model_type + params.{n_estimators,max_depth} + metrics.f1_score + the fitted model artefact. Correct.
src/select_model.py – Picks the winning run by the training metric and writes reports/selection.json. Needs attention.
src/register.py – Registers the selected run's model as fraud-detector and assigns the release-lane alias. Needs attention.
src/report.py – Aggregates every upstream artefact into reports/training_report.json. Correct.
Makefile – train-pipeline target runs the five stages in order. Needs attention.
Run make train-pipeline from /root/code/fraud-detection/ to surface each issue in turn. Open the offending file in the VS Code editor, correct the wiring, and re-run until the pipeline completes without non-zero exit.

The end state must include:

make train-pipeline completes without non-zero exit.
The fraud-detection-tuning MLflow experiment carries at least five trial runs, each with metrics.f1_score.
reports/selection.json, reports/validation_status.json, and reports/training_report.json are all present. The training report carries best_model, best_params, metrics, total_trials, and validation_status keys; validation_status is "ok" and total_trials is an integer ≥ 5.
The MLflow Model Registry (MLflow UI → Models) shows a fraud-detector registered model with at least one version. That version carries the staging alias and no production alias.
Run make train-pipeline once against the scaffold as-is; the first wiring issue surfaces immediately. Each subsequent re-run reveals the next stage's problem. Every fix is a one-line edit in one of the three files listed above.




registry.py
"""Stage 4 — Register the selected model.

Reads the selection written by the previous stage, registers the
selected run's model as `fraud-detector` in the MLflow Model
Registry, and assigns the release-lane alias so the serving layer
can fetch the right version by name.
"""
import json
import os
import sys

import mlflow
from mlflow.tracking import MlflowClient

TRACKING_URI = "http://localhost:5000"
REPORTS_DIR = "/root/code/fraud-detection/reports"
SELECTION_JSON = os.path.join(REPORTS_DIR, "selection.json")

REGISTERED_MODEL_NAME = "fraud-detector"
RELEASE_ALIAS = "production"


def main():
    if not os.path.exists(SELECTION_JSON):
        sys.exit(
            f"[register] {SELECTION_JSON} missing — the select stage "
            "has not produced a selection yet."
        )
    with open(SELECTION_JSON) as f:
        selection = json.load(f)

    mlflow.set_tracking_uri(TRACKING_URI)
    client = MlflowClient()

    model_uri = f"runs:/{selection['run_id']}/model"
    version = mlflow.register_model(model_uri, REGISTERED_MODEL_NAME)

    client.set_registered_model_alias(
        REGISTERED_MODEL_NAME, RELEASE_ALIAS, version.version,
    )
    print(
        f"[register] {REGISTERED_MODEL_NAME} v{version.version} "
        f"aliased as {RELEASE_ALIAS!r}"
    )


if __name__ == "__main__":
    main()




report.py
"""Stage 5 — Training report.

Aggregates every upstream stage's output into a single JSON report
at `reports/training_report.json`. Reads:
  - `reports/validation_status.json` produced by the validate stage.
  - `reports/selection.json` produced by the select stage.
  - the MLflow experiment's run count for the total trials figure.
"""
import json
import os

import mlflow

TRACKING_URI = "http://localhost:5000"
EXPERIMENT = "fraud-detection-tuning"
REPORTS_DIR = "/root/code/fraud-detection/reports"

VALIDATION_JSON = os.path.join(REPORTS_DIR, "validation_status.json")
SELECTION_JSON = os.path.join(REPORTS_DIR, "selection.json")
TRAINING_REPORT_JSON = os.path.join(REPORTS_DIR, "training_report.json")


def main():
    with open(VALIDATION_JSON) as f:
        validation = json.load(f)
    with open(SELECTION_JSON) as f:
        selection = json.load(f)

    mlflow.set_tracking_uri(TRACKING_URI)
    client = mlflow.MlflowClient()
    exp = client.get_experiment_by_name(EXPERIMENT)
    runs = mlflow.search_runs([exp.experiment_id], max_results=500) if exp else []
    total_trials = int(len(runs)) if hasattr(runs, "__len__") else 0

    run_id = selection["run_id"]
    client = mlflow.MlflowClient()
    run = client.get_run(run_id)
    best_params = {k: v for k, v in run.data.params.items()}
    best_metrics = {k: float(v) for k, v in run.data.metrics.items()}

    report = {
        "best_model": selection.get("model_type", ""),
        "best_params": best_params,
        "metrics": best_metrics,
        "total_trials": total_trials,
        "validation_status": validation.get("status", ""),
    }

    os.makedirs(REPORTS_DIR, exist_ok=True)
    with open(TRAINING_REPORT_JSON, "w") as f:
        json.dump(report, f, indent=2)
    print(f"[report] {TRAINING_REPORT_JSON}")


if __name__ == "__main__":
    main()


select_model.py

"""Stage 3 — Model selection.

Reads every run in the `fraud-detection-tuning` experiment, picks
the best candidate by the training metric, validates it against the
release threshold, and persists the selection to
`reports/selection.json` for the register stage.
"""
import json
import os
import sys

import mlflow

TRACKING_URI = "http://localhost:5000"
EXPERIMENT = "fraud-detection-tuning"
REPORTS_DIR = "/root/code/fraud-detection/reports"
SELECTION_JSON = os.path.join(REPORTS_DIR, "selection.json")

RELEASE_THRESHOLD = 0.4


def main():
    mlflow.set_tracking_uri(TRACKING_URI)
    client = mlflow.MlflowClient()
    exp = client.get_experiment_by_name(EXPERIMENT)
    if exp is None:
        sys.exit(f"[select] experiment {EXPERIMENT!r} not found.")

    runs = mlflow.search_runs(
        experiment_ids=[exp.experiment_id],
        order_by=["metrics.accuracy DESC"],
        max_results=200,
    )
    if runs.empty:
        sys.exit(
            f"[select] no runs in experiment {EXPERIMENT!r} — the tune "
            "stage has not produced any candidates yet."
        )

    best = runs.iloc[0]
    score = float(best["metrics.accuracy"])
    if score < RELEASE_THRESHOLD:
        sys.exit(
            f"[select] best candidate ({score:.4f}) is below the "
            f"release threshold ({RELEASE_THRESHOLD})."
        )

    selection = {
        "run_id": best["run_id"],
        "model_type": best.get("tags.model_type", ""),
        "f1_score": score,
    }
    os.makedirs(REPORTS_DIR, exist_ok=True)
    with open(SELECTION_JSON, "w") as f:
        json.dump(selection, f, indent=2)
    print(f"[select] {selection}")


if __name__ == "__main__":
    main()


tune.py

"""Stage 2 — Optuna tuning across two model families.

Runs `N_TRIALS` Optuna trials, each sampling a model family
(RandomForest or GradientBoosting) plus its hyperparameters.
Every trial fits the estimator under 3-fold stratified CV on the
training CSV and logs one MLflow run tagged with the candidate
family, the sampled hyperparameters, and the mean F1 score.
The fitted estimator is also logged as an MLflow model artefact so
the register stage can reference it by URI.
"""
import mlflow
import mlflow.sklearn
import optuna
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedKFold

TRACKING_URI = "http://localhost:5000"
EXPERIMENT = "fraud-detection-tuning"
TRAIN_CSV = "/root/code/fraud-detection/data/train.csv"

N_TRIALS = 10
SEED = 42


def _build(trial):
    model_type = trial.suggest_categorical(
        "model_type", ["RandomForest", "GradientBoosting"]
    )
    n_estimators = trial.suggest_int("n_estimators", 50, 200)
    max_depth = trial.suggest_int("max_depth", 3, 10)

    if model_type == "RandomForest":
        model = RandomForestClassifier(
            n_estimators=n_estimators, max_depth=max_depth, random_state=SEED,
        )
    else:
        model = GradientBoostingClassifier(
            n_estimators=n_estimators, max_depth=max_depth, random_state=SEED,
        )
    return model_type, model, {
        "n_estimators": n_estimators,
        "max_depth": max_depth,
    }


def _objective(trial, X, y):
    model_type, model, params = _build(trial)
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=SEED)
    scores = []
    for tr, te in cv.split(X, y):
        model.fit(X.iloc[tr], y.iloc[tr])
        scores.append(f1_score(y.iloc[te], model.predict(X.iloc[te])))
    mean_f1 = float(sum(scores) / len(scores))

    model.fit(X, y)
    with mlflow.start_run(run_name=f"trial-{trial.number}"):
        mlflow.set_tag("model_type", model_type)
        mlflow.log_params(params)
        mlflow.log_metric("f1_score", mean_f1)
        mlflow.sklearn.log_model(model, name="model")

    return mean_f1


def main():
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT)

    df = pd.read_csv(TRAIN_CSV)
    X = df.drop(columns=["is_fraud"])
    y = df["is_fraud"]

    sampler = optuna.samplers.TPESampler(seed=SEED)
    study = optuna.create_study(
        direction="maximize", study_name=EXPERIMENT, sampler=sampler,
    )
    study.optimize(lambda t: _objective(t, X, y), n_trials=N_TRIALS)

    print(
        f"[tune] {N_TRIALS} trials complete. "
        f"best_value={study.best_value:.4f}  best_params={study.best_params}"
    )


if __name__ == "__main__":
    main()


validate_data.py

"""Stage 1 — Data validation.

Loads the raw training CSV, verifies the expected schema and that no
nulls have leaked into the feature columns, and writes the result to
`reports/validation_status.json` as a status gate the rest of the
pipeline reads back.
"""
import json
import os
import sys

import pandas as pd

TRAIN_CSV = "/root/code/fraud-detection/data/train.csv"
REPORTS_DIR = "/root/code/fraud-detection/reports"
STATUS_JSON = os.path.join(REPORTS_DIR, "validation_status.json")

EXPECTED_COLUMNS = ["amount", "hour", "num_tx_past_day", "is_fraud"]


def main():
    df = pd.read_csv(TRAIN_CSV)

    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        sys.exit(f"[validate] schema check failed — missing columns: {missing}")

    null_counts = df[EXPECTED_COLUMNS].isna().sum().to_dict()
    if any(v > 0 for v in null_counts.values()):
        sys.exit(f"[validate] null check failed — {null_counts}")

    status = {
        "status": "ok",
        "rows": int(len(df)),
        "columns": EXPECTED_COLUMNS,
    }
    os.makedirs(REPORTS_DIR, exist_ok=True)
    with open(STATUS_JSON, "w") as f:
        json.dump(status, f, indent=2)
    print(f"[validate] {status}")


if __name__ == "__main__":
    main()

makefile

.PHONY: train-pipeline clean

# xFusionCorp Industries — Fraud Detection Training Pipeline.
# Usage: make train-pipeline

train-pipeline:
	python3 src/validate_data.py
	python3 src/tune.py
	python3 src/select_model.py
	python3 src/register.py
	python3 src/report.py

clean:
	rm -rf models/ reports/