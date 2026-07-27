"""Run the fraud-detector quality gates as an Evidently test suite.

Startup has already seeded the latest production batch at
``tests/current.csv`` (features + the ``is_fraud`` target + the
model's ``prediction`` column), created the Evidently workspace
behind the **Evidently UI** button, and wired this script to publish
every run there. The only missing piece is the two thresholded
metrics that turn the report into a pass/fail gate -- add them in
the TODO block below, then execute the file:

    python3 /root/code/monitoring/tests/test_suite.py
"""
from __future__ import annotations

import json

import pandas as pd
from evidently import Dataset, DataDefinition, Report
from evidently.core.datasets import BinaryClassification
from evidently.metrics import Accuracy, DatasetMissingValueCount
from evidently.tests import gt, lt
from evidently.ui.workspace import Workspace

BATCH_CSV = "/root/code/monitoring/tests/current.csv"
RESULTS_JSON = "/root/code/monitoring/tests/test_results.json"
WORKSPACE_DIR = "/root/code/monitoring/workspace"
PROJECT_NAME = "fraud-detector quality gates"

# ----------------------------------------------------------------------
# TODO 1: Gate data quality -- fail the suite when the batch carries
#         10 or more missing values.
#
#         METRICS.append(DatasetMissingValueCount(tests=[lt(10)]))
#
# TODO 2: Gate model quality -- fail the suite when batch accuracy
#         is 0.80 or lower. Use `Accuracy` with `tests=[gt(0.80)]`,
#         appended the same way.
# ----------------------------------------------------------------------
METRICS = []

# (append the two thresholded metrics here)


def main() -> None:
    if not METRICS:
        print("METRICS is empty -- complete the TODO block first.")
        return

    df = pd.read_csv(BATCH_CSV)
    dd = DataDefinition(
        classification=[
            BinaryClassification(
                target="is_fraud", prediction_labels="prediction"
            )
        ]
    )
    ds = Dataset.from_pandas(df, data_definition=dd)

    # include_tests=True turns every thresholded metric into a
    # pass/fail assertion -- Evidently's "test suite" mode.
    result = Report(metrics=METRICS, include_tests=True).run(current_data=ds)

    d = result.dict()
    with open(RESULTS_JSON, "w") as fh:
        json.dump(d, fh, indent=2, default=str)

    # Publish the run to the workspace behind the Evidently UI button.
    ws = Workspace.create(WORKSPACE_DIR)
    found = ws.search_project(PROJECT_NAME)
    project = found[0] if found else ws.create_project(PROJECT_NAME)
    ws.add_run(project.id, result)

    tests = d.get("tests", [])
    passed = sum(1 for t in tests if t.get("status") == "SUCCESS")
    print(f"Tests: {passed}/{len(tests)} passed -> {RESULTS_JSON}")
    for t in tests:
        status = str(t.get("status", "")).split(".")[-1]
        print(f"  - {t.get('name')}: {status}")
    print("Run published -- refresh the Evidently UI to inspect it.")


if __name__ == "__main__":
    main()






"""Run the fraud-detector quality gates as an Evidently test suite.

Startup has already seeded the latest production batch at
``tests/current.csv`` (features + the ``is_fraud`` target + the
model's ``prediction`` column), created the Evidently workspace
behind the **Evidently UI** button, and wired this script to publish
every run there. The only missing piece is the two thresholded
metrics that turn the report into a pass/fail gate -- add them in
the TODO block below, then execute the file:

    python3 /root/code/monitoring/tests/test_suite.py
"""
from __future__ import annotations

import json

import pandas as pd
from evidently import Dataset, DataDefinition, Report
from evidently.core.datasets import BinaryClassification
from evidently.metrics import Accuracy, DatasetMissingValueCount
from evidently.tests import gt, lt
from evidently.ui.workspace import Workspace

BATCH_CSV = "/root/code/monitoring/tests/current.csv"
RESULTS_JSON = "/root/code/monitoring/tests/test_results.json"
WORKSPACE_DIR = "/root/code/monitoring/workspace"
PROJECT_NAME = "fraud-detector quality gates"

# ----------------------------------------------------------------------
# Quality Gates
# ----------------------------------------------------------------------
METRICS = [
    # Fail if missing values are 10 or more
    DatasetMissingValueCount(
        tests=[lt(10)]
    ),

    # Fail if accuracy is 0.80 or lower
    Accuracy(
        tests=[gt(0.80)]
    ),
]


def main() -> None:
    if not METRICS:
        print("METRICS is empty -- complete the TODO block first.")
        return

    df = pd.read_csv(BATCH_CSV)

    dd = DataDefinition(
        classification=[
            BinaryClassification(
                target="is_fraud",
                prediction_labels="prediction",
            )
        ]
    )

    ds = Dataset.from_pandas(df, data_definition=dd)

    # include_tests=True turns threshold metrics into pass/fail tests
    result = Report(
        metrics=METRICS,
        include_tests=True,
    ).run(current_data=ds)

    d = result.dict()

    with open(RESULTS_JSON, "w") as fh:
        json.dump(d, fh, indent=2, default=str)

    # Publish to Evidently Workspace
    ws = Workspace.create(WORKSPACE_DIR)
    found = ws.search_project(PROJECT_NAME)
    project = found[0] if found else ws.create_project(PROJECT_NAME)
    ws.add_run(project.id, result)

    tests = d.get("tests", [])
    passed = sum(1 for t in tests if t.get("status") == "SUCCESS")

    print(f"Tests: {passed}/{len(tests)} passed -> {RESULTS_JSON}")

    for t in tests:
        status = str(t.get("status", "")).split(".")[-1]
        print(f"  - {t.get('name')}: {status}")

    print("Run published -- refresh the Evidently UI to inspect it.")


if __name__ == "__main__":
    main()