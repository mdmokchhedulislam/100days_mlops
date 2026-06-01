

The xFusionCorp Industries ML team is adopting MLflow for experiment tracking. Your task is to bring up a local MLflow tracking server on the ML pipeline workstation so experiments can be logged from the team's training code.


MLflow 3.x is pre-installed on the controlplane. Launch the tracking server in the background so that every end-state requirement below holds.

The server is listening on port 5000 and is reachable on all interfaces.

The backend store is a SQLite database at /root/code/mlflow-backend/mlflow.db. The database file must exist after the server has started.

The artifact root is /root/code/mlflow-artifacts/.

Any parent directories the server needs must be in place before it starts—MLflow will abort if the backend directory is missing.

The MLflow UI button at the top of the lab must open a responsive dashboard in the browser. The button routes through the lab proxy, so the server must accept requests from any origin (--cors-allowed-origins '*') and any host header (--allowed-hosts '*') to avoid proxy-related rejections.

The server process must persist in the background so it survives terminal closure.

Once the server is running, the Default experiment can be viewed from the MLflow UI button. The experiment is empty—runs will be logged in subsequent labs.



SOLVE:

create essential file/folder
mkdir -p /root/code/mlflow-backend /root/code/mlflow-artifacts


run mlflow server with requrement

nohup mlflow server \
  --host 0.0.0.0 \
  --port 5000 \
  --backend-store-uri sqlite:////root/code/mlflow-backend/mlflow.db \
  --default-artifact-root /root/code/mlflow-artifacts/ \
  --cors-allowed-origins '*' \
  --allowed-hosts '*' > /root/code/mlflow.log 2>&1 &

check 
ps aux | grep mlflow
