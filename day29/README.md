The xFusionCorp Industries ML platform team rolled out a shared MLflow deployment backed by a production-style tracking store (PostgreSQL) and a production-style artefact store (SeaweedFS, S3-compatible). The MLflow server is running and metadata writes to PostgreSQL succeed, but a teammate noticed that no artefact ever lands in the mlflow-artifacts SeaweedFS bucket — the connection from MLflow to SeaweedFS is not wired correctly. Diagnose what is broken in the MLflow server's startup configuration, fix it, and re-run the pre-staged smoke-test so one round trip lands metadata in PostgreSQL and the model artefact in SeaweedFS.


The pre-staged state:

PostgreSQL container mlflow-db is running on port 5432 (database mlflow, credentials mlflow / mlflow123).
SeaweedFS is running on port 8333 (S3 API) / 8888 (Filer UI), credentials weedadmin / weedadmin123, with a pre-created bucket mlflow-artifacts.
MLflow tracking server is running on port 5000 and was launched by /root/code/start-mlflow.sh. Its log is at /tmp/mlflow.log.
Reference scripts: /root/code/start-mlflow.sh (the MLflow startup command), /root/code/restart-mlflow.sh (kills the running server and re-launches via start-mlflow.sh), and /root/code/log_test_run.py (the smoke-test that exercises one full round trip).
Run the smoke-test once to observe the failure:

   python3 /root/code/log_test_run.py

The MLflow run appears in the MLflow UI (the metadata write to PostgreSQL succeeds), but the model artefact upload step raises an error because the MLflow server cannot reach the SeaweedFS bucket. The SeaweedFS Filer confirms /buckets/mlflow-artifacts/ is still empty.

Inspect /root/code/start-mlflow.sh and reconcile its environment with the SeaweedFS endpoint. Save the file, then restart the MLflow server:
   bash /root/code/restart-mlflow.sh

Re-run the smoke-test:
   python3 /root/code/log_test_run.py

The end state must include:
The test-remote experiment exists on the MLflow server with at least one successful run, visible in the MLflow UI.
The mlflow-artifacts bucket on SeaweedFS holds the run's model artefact (MLmodel + model.pkl), visible in the SeaweedFS Filer under /buckets/mlflow-artifacts/.
The PostgreSQL mlflow database holds the MLflow schema (the run's metadata).
PostgreSQL listens on port 5432 with a binary protocol — it is not reachable from a web browser. Use docker exec mlflow-db psql -U mlflow -d mlflow for manual inspection if needed.



log_test_run.py

"""Log one test run against the remote MLflow setup.

Prerequisites before this script is run:
- The MLflow tracking server is already serving on http://localhost:5000
  with the PostgreSQL backend and the SeaweedFS (S3-compatible) artefact
  store, started with --artifacts-destination s3://mlflow-artifacts.
- Because the server runs in proxied artefact-serving mode, this client
  uploads artefacts *through* the MLflow server (via the mlflow-artifacts:
  proxy URI). The server — not this client — is what writes them to
  SeaweedFS, using its own AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY /
  MLFLOW_S3_ENDPOINT_URL. This client therefore needs only the tracking
  URI set below.

The DummyClassifier and the synthetic metrics values have no meaning
beyond exercising one full metadata-to-artefact round-trip (§2.5).
"""
import numpy as np
import mlflow
import mlflow.sklearn
from sklearn.dummy import DummyClassifier

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("test-remote")

X = np.array([[0.0], [1.0]])
y = np.array([0, 1])
model = DummyClassifier(strategy="most_frequent").fit(X, y)

with mlflow.start_run(run_name="remote-smoke-test"):
    mlflow.log_param("source", "remote-smoke-test")
    mlflow.log_metric("accuracy", 0.87)
    mlflow.log_metric("f1_score", 0.86)
    mlflow.sklearn.log_model(model, name="model")

print("test-remote run logged successfully")




start-mlflow.sh
#!/bin/bash
# Start the MLflow tracking server with the production-style wiring:
# - PostgreSQL backend for run metadata
# - SeaweedFS (S3-compatible) for artefact storage
# - host/CORS flags so the MLflow UI button works through the lab proxy
set -e

export AWS_ACCESS_KEY_ID=weedadmin
export AWS_SECRET_ACCESS_KEY=weedadmin123

exec mlflow server \
  --backend-store-uri postgresql://mlflow:mlflow123@localhost:5432/mlflow \
  --artifacts-destination s3://mlflow-artifacts \
  --host 0.0.0.0 --port 5000 \
  --allowed-hosts '*' --cors-allowed-origins '*'



solve
#!/bin/bash
set -e

export AWS_ACCESS_KEY_ID=weedadmin
export AWS_SECRET_ACCESS_KEY=weedadmin123
export MLFLOW_S3_ENDPOINT_URL=http://localhost:8333

exec mlflow server \
  --backend-store-uri postgresql://mlflow:mlflow123@localhost:5432/mlflow \
  --artifacts-destination s3://mlflow-artifacts \
  --host 0.0.0.0 --port 5000 \
  --allowed-hosts '*' --cors-allowed-origins '*'





  restart-mlflow.sh
  #!/bin/bash
# Kill the running mlflow server and re-launch from start-mlflow.sh.
# Run this after editing start-mlflow.sh so the new env / flags
# take effect.
pkill -f 'bin/mlflow server' 2>/dev/null
sleep 2
nohup bash /root/code/start-mlflow.sh > /tmp/mlflow.log 2>&1 &
echo "MLflow restart triggered. tail /tmp/mlflow.log to follow."