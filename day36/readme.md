The xFusionCorp Industries ML platform team is running a three-way bake-off between a RandomForest, a GradientBoosting, and a LogisticRegression candidate for fraud detection, with every candidate tracked as an MLflow run in the bakeoff experiment. Three correct trainer scripts are already in place, but the orchestrator at /root/code/fraud-detection/src/models/bakeoff.py picks the wrong winner and writes an incomplete report. Your task is to correct the orchestrator so the saved winner is the highest-F1 candidate and the report identifies which model family won.


The MLflow tracking server is already running on port 5000. The MLflow UI button at the top of the lab can be opened to confirm—the dashboard loads with an empty bakeoff experiment.

The project layout under /root/code/fraud-detection/:

data/train.csv – The same 200-row synthetic binary-classification dataset Day 34 uses (imbalanced roughly 70 / 30).
src/models/train_rf.py, src/models/train_gb.py, src/models/train_lr.py – Three independent trainer scripts. Each one fits its named estimator with 3-fold stratified CV and logs one MLflow run tagged candidate=<model family> with the mean f1_score metric and its hyperparameters. These three files are correct and need no edits.
src/models/bakeoff.py – The orchestrator. It queries the bakeoff experiment with mlflow.search_runs(...) and writes /root/code/fraud-detection/reports/winner.json. Two specific corrections are required.
Run each of the three trainer scripts once so every candidate is logged, open src/models/bakeoff.py in the VS Code editor, correct the two problems that keep the report from meeting the release checklist, save, and run the orchestrator.

The end state must include:

Three runs exist in the bakeoff MLflow experiment, one per candidate, each with tags.candidate, the candidate's hyperparameters, and metrics.f1_score.
A JSON file at /root/code/fraud-detection/reports/winner.json with exactly three keys: model_type (one of random_forest, gradient_boosting, logistic_regression), run_id, and f1_score.
The model_type, run_id, and f1_score stored in winner.json correspond to the candidate with the highest f1_score in the bakeoff experiment.
The MLflow Compare view—select all three runs in the experiment's run list and click Compare—is the fastest way to eyeball which candidate won and spot-check the report.



backoff.py

import json
import os
import mlflow

TRACKING_URI = "http://localhost:5000"
EXPERIMENT = "bakeoff"
REPORTS_DIR = "/root/code/fraud-detection/reports"
WINNER_JSON = os.path.join(REPORTS_DIR, "winner.json")


def main():
    mlflow.set_tracking_uri(TRACKING_URI)
    client = mlflow.MlflowClient()

    exp = client.get_experiment_by_name(EXPERIMENT)
    if exp is None:
        raise SystemExit(f"Experiment {EXPERIMENT!r} not found.")

    runs = mlflow.search_runs(
        experiment_ids=[exp.experiment_id],
        order_by=["metrics.f1_score DESC"],   # ✅ FIX 1
        max_results=10,
    )

    if runs.empty:
        raise SystemExit("No runs found.")

    winner = runs.iloc[0]

    report = {
        "model_type": winner["tags.candidate"],  # ✅ FIX 2
        "run_id": winner["run_id"],
        "f1_score": float(winner["metrics.f1_score"]),
    }

    os.makedirs(REPORTS_DIR, exist_ok=True)

    with open(WINNER_JSON, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Winner written: {report}")


if __name__ == "__main__":
    main()




traingb.py

"""Train a GradientBoosting candidate for the bake-off.

Logs a single MLflow run in the `bakeoff` experiment with:
  - tags.candidate = "gradient_boosting"
  - params: n_estimators, max_depth, learning_rate
  - metrics.f1_score (mean of 3-fold CV, stratified, random_state=42)
"""
import mlflow
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedKFold

TRACKING_URI = "http://localhost:5000"
EXPERIMENT = "bakeoff"
TRAIN_CSV = "/root/code/fraud-detection/data/train.csv"

CANDIDATE = "gradient_boosting"
PARAMS = {"n_estimators": 150, "max_depth": 3, "learning_rate": 0.1}


def main():
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT)

    df = pd.read_csv(TRAIN_CSV)
    X = df.drop(columns=["is_fraud"])
    y = df["is_fraud"]

    model = GradientBoostingClassifier(random_state=42, **PARAMS)
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    scores = []
    for tr, te in cv.split(X, y):
        model.fit(X.iloc[tr], y.iloc[tr])
        scores.append(f1_score(y.iloc[te], model.predict(X.iloc[te])))
    mean_f1 = float(sum(scores) / len(scores))

    with mlflow.start_run(run_name=CANDIDATE) as run:
        mlflow.set_tag("candidate", CANDIDATE)
        mlflow.log_params(PARAMS)
        mlflow.log_metric("f1_score", mean_f1)
        print(f"{CANDIDATE}: f1_score={mean_f1:.4f}  run_id={run.info.run_id}")


if __name__ == "__main__":
    main()



trainlr.py

"""Train a LogisticRegression candidate for the bake-off.

Logs a single MLflow run in the `bakeoff` experiment with:
  - tags.candidate = "logistic_regression"
  - params: C, max_iter
  - metrics.f1_score (mean of 3-fold CV, stratified, random_state=42)
"""
import mlflow
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedKFold

TRACKING_URI = "http://localhost:5000"
EXPERIMENT = "bakeoff"
TRAIN_CSV = "/root/code/fraud-detection/data/train.csv"

CANDIDATE = "logistic_regression"
PARAMS = {"C": 1.0, "max_iter": 1000}


def main():
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT)

    df = pd.read_csv(TRAIN_CSV)
    X = df.drop(columns=["is_fraud"])
    y = df["is_fraud"]

    model = LogisticRegression(random_state=42, **PARAMS)
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    scores = []
    for tr, te in cv.split(X, y):
        model.fit(X.iloc[tr], y.iloc[tr])
        scores.append(f1_score(y.iloc[te], model.predict(X.iloc[te])))
    mean_f1 = float(sum(scores) / len(scores))

    with mlflow.start_run(run_name=CANDIDATE) as run:
        mlflow.set_tag("candidate", CANDIDATE)
        mlflow.log_params(PARAMS)
        mlflow.log_metric("f1_score", mean_f1)
        print(f"{CANDIDATE}: f1_score={mean_f1:.4f}  run_id={run.info.run_id}")


if __name__ == "__main__":
    main()


trainrf.py

"""Train a LogisticRegression candidate for the bake-off.

Logs a single MLflow run in the `bakeoff` experiment with:
  - tags.candidate = "logistic_regression"
  - params: C, max_iter
  - metrics.f1_score (mean of 3-fold CV, stratified, random_state=42)
"""
import mlflow
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedKFold

TRACKING_URI = "http://localhost:5000"
EXPERIMENT = "bakeoff"
TRAIN_CSV = "/root/code/fraud-detection/data/train.csv"

CANDIDATE = "logistic_regression"
PARAMS = {"C": 1.0, "max_iter": 1000}


def main():
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT)

    df = pd.read_csv(TRAIN_CSV)
    X = df.drop(columns=["is_fraud"])
    y = df["is_fraud"]

    model = LogisticRegression(random_state=42, **PARAMS)
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    scores = []
    for tr, te in cv.split(X, y):
        model.fit(X.iloc[tr], y.iloc[tr])
        scores.append(f1_score(y.iloc[te], model.predict(X.iloc[te])))
    mean_f1 = float(sum(scores) / len(scores))

    with mlflow.start_run(run_name=CANDIDATE) as run:
        mlflow.set_tag("candidate", CANDIDATE)
        mlflow.log_params(PARAMS)
        mlflow.log_metric("f1_score", mean_f1)
        print(f"{CANDIDATE}: f1_score={mean_f1:.4f}  run_id={run.info.run_id}")


if __name__ == "__main__":
    main()