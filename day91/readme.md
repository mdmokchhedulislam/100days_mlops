The xFusionCorp Industries ML platform team is cutting the first production release of the fraud-detector pipeline. A WorkflowTemplate named fraud-training-pipeline trains a model and registers it in MLflow; a CronWorkflow named fraud-retraining re-runs the template every minute. Argo and an in-cluster MLflow are running, but the release is broken on three fronts. Your capstone task is to fix all three bugs entirely through the Argo UI and confirm that a new version of fraud-detector appears on the MLflow Models page.


Two surfaces are exposed: the Argo UI (port 5000) — Workflows list, Workflow Templates, and Cron Workflows — and the MLflow UI (port 5001), whose Models page is empty since no version of fraud-detector has been registered yet.

Three independent wiring issues sit between the run logs, the fraud-training-pipeline WorkflowTemplate spec, and the fraud-retraining CronWorkflow spec. They surface progressively: the first submission of the template is rejected outright with a parameter-resolution error (a bad output-parameter reference); once that is fixed a node fails at runtime, visible in its logs; and the Cron Workflows page reveals what fraud-retraining is failing to do over the last few minutes. Each fix is a single value change made through the Argo UI's YAML editors (the template's or the cron's Edit view).

With all three fixed, a fresh submission of fraud-training-pipeline should run green end-to-end, fraud-retraining should spawn a green child workflow within a minute, and the MLflow Models page should show one or more versions of fraud-detector.

The end state must include:

A manual submission of the fraud-training-pipeline template runs end-to-end to Succeeded (train and register both green on the DAG).
GET /api/2.0/mlflow/registered-models/get?name=fraud-detector returns at least one version (tests poll up to 300 s).
The fraud-retraining CronWorkflow spawns at least one child Workflow that completes successfully — the Cron Workflows page shows it in the resource's Workflows panel (tests look for the owner label workflows.argoproj.io/cron-workflow=fraud-retraining).
Production orchestration breaks across boundaries — a typo or a stale reference can survive a reviewer's read of any single resource. The capstone is reading them as symptoms on a running system, fixing them in place, and confirming the full pipe is back to passing.