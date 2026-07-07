 Set Up Local ML Dev Environment with Docker Compose


The xFusionCorp Industries ML platform team ships a local dev stack—Jupyter Lab for notebooks, MLflow for experiment tracking, SeaweedFS for S3-compatible artefact storage—as a three-service docker compose deployment. A draft docker-compose.yml exists at /root/code/ml-dev/, but as it ships the stack does not bring all three browser UIs up on their standard ports. Your task is to correct the docker-compose.yml so every service is reachable on its standard port without login prompts, bring the stack up with docker compose up -d, and confirm via the browser-UI buttons at the top of the lab.


The Docker daemon is already running and every image has been pre-pulled in the background at startup, so docker compose up -d returns in seconds on the first run.

The project layout under /root/code/ml-dev/:

docker-compose.yml – Three services:
jupyter – Container ml-jupyter on jupyter/base-notebook:python-3.11, host port 8888.
mlflow – Container ml-mlflow on ghcr.io/mlflow/mlflow:v2.15.1, host port 5000. Correct.
seaweedfs – Container ml-seaweedfs on chrislusf/seaweedfs:4.22. SeaweedFS serves the S3 API on container port 8333 and the Filer UI on container port 8888. The lab's convention is host port 9000 for the S3 API and host port 9001 for the Filer UI.
Open docker-compose.yml in the VS Code editor, align it with the end state below, save, and run docker compose up -d from inside /root/code/ml-dev/.

The end state must include:

All three containers (ml-jupyter, ml-mlflow, ml-seaweedfs) reported Up by docker compose ps.
curl http://localhost:8888/ returns 200 or 302 – The Jupyter UI answers without prompting for a token.
curl http://localhost:5000/ returns 200 – The MLflow UI answers on the standard port.
curl http://localhost:9001/ returns 200, 302, or 403 – The SeaweedFS Filer UI answers on its standard host port (the SeaweedFS S3 API stays on host 9000).
The three browser UIs (Jupyter, MLflow, SeaweedFS Filer) are the primary verification surface — open them from the buttons at the top of the lab.















 docker compose file
services:
  jupyter:
    image: jupyter/base-notebook:python-3.11
    container_name: ml-jupyter
    ports:
      - "8888:8888"
    command:
      - start-notebook.py
      - --IdentityProvider.token=
      - --PasswordIdentityProvider.password_required=False
    volumes:
      - ./notebooks:/home/jovyan/work

  mlflow:
    image: ghcr.io/mlflow/mlflow:v2.15.1
    container_name: ml-mlflow
    ports:
      - "5000:5000"
    volumes:
      - mlflow-data:/mlflow
    command: >-
      mlflow server
      --host 0.0.0.0
      --port 5000
      --backend-store-uri sqlite:////mlflow/mlflow.db
      --default-artifact-root /mlflow/artifacts

  seaweedfs:
    image: chrislusf/seaweedfs:4.22
    container_name: ml-seaweedfs
    ports:
      - "9000:8333"
      - "9001:8888"
    volumes:
      - seaweedfs-data:/data
    command: server -dir=/data -s3

volumes:
  mlflow-data:
  seaweedfs-data: