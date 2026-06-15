The xFusionCorp Industries MLOps team needs the fraud-detection-v2 candidate promoted all the way from the tracking server to live inference and monitored end to end. The backing stack (PostgreSQL, SeaweedFS, MLflow tracking server, three candidate runs) is already in place. Your task is to cover the remaining lifecycle work: model promotion, serving, and health monitoring.


The infrastructure is fully up: PostgreSQL container mlflow-db on port 5432, SeaweedFS on ports 8333 (S3 API) and 8888 (Filer UI), MLflow tracking server on port 5000 with the PostgreSQL backend and the mlflow-artifacts S3 bucket. The fraud-detection-v2 experiment contains three candidate runs (baseline, improved, regression) with logged f1_score metrics. The MLflow UI and SeaweedFS Filer buttons at the top of the lab can be opened to view each web UI.

The complete end state requires the following.

A registered model named fraud-detector-v2 exists in the MLflow Model Registry.
A champion alias on that model points at the version sourced from the fraud-detection-v2 run with the highest f1_score.
An mlflow models serve process listens on port 5001, serving the champion version (--env-manager=local is the supported choice for the lab). Export MLFLOW_TRACKING_URI=http://localhost:5000 in the serving shell so the models:/ URI can be resolved against the tracking server. The tracking server proxies the model download from SeaweedFS itself, so no S3 credentials are needed in the serving shell.
The served endpoint returns 200 on GET /health.
A shell script at /root/code/monitor.sh exists, is executable, probes the served model's /health endpoint once, and exits with status 0 when the endpoint is healthy.
The top run can be identified either through the MLflow UI Compare view or with a one-off MlflowClient.search_runs() call—whichever is preferable. The registration and alias assignment are likewise available from the UI (Models tab) or the SDK.

mlflow models serve is long-running; start it in the background, and ensure that the new process is listening on port 5001 before writing the monitoring script.






1 STEP:
CHECK mlflow rui tracking : 
export MLFLOW_TRACKING_URI=http://localhost:5000

curl http://localhost:5000


2 STEP:
CHECK EXPERIMENT NAME 

from mlflow import MlflowClient
client = MlflowClient()
client.list_experiments()


3 STEP:
FIND CHAMPION MODEL


from mlflow import MlflowClient

client = MlflowClient()

exp = client.get_experiment_by_name("fraud-detection-v2")

runs = client.search_runs([exp.experiment_id])

best_run = None
best_score = -1

for r in runs:
    score = r.data.metrics.get("f1_score")
    print(r.info.run_id, score)

    if score and score > best_score:
        best_score = score
        best_run = r.info.run_id

print("\nBEST RUN:", best_run, best_score)



step 4:
register model registry


import mlflow

model_uri = f"runs:/{best_run}/model"

result = mlflow.register_model(
    model_uri,
    "champion"
)

print(result.version)

client.set_registered_model_alias(
    name="fraud-detector-v2",
    alias="champion",
    version=result.version
)



model serve:

nohup mlflow models serve \
-m models:/champion@champion \
-p 5001 \
--env-manager=local \
> serve.log 2>&1 &

