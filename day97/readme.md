The xFusionCorp Industries MLOps team is standing up the serving path of their fraud-detector platform — the route a model takes from a training run to a live prediction endpoint. The backing stack is already running: a SeaweedFS object store (with a seeded training dataset) and an MLflow tracking server. Your task is to drive that path end to end: run the training script to produce a run, complete register.py so it registers the run as the fraud-detector model and assigns the production alias, then start the FastAPI inference server so it serves live predictions from the aliased model.


The MLflow UI and SeaweedFS Filer buttons at the top of the lab open those UIs. Pre-staged state:

SeaweedFS bucket data holds transactions.csv; the mlflow-artifacts bucket is empty until a run logs to it.
MLflow experiment fraud-detection does not exist yet and the Model Registry is empty.
Under /root/code/: train.py, serve.py, and config.yaml are reference scripts (no edits needed); register.py ships with its register + promote step as an unfinished TODO for you to complete. train.py reads the dataset from SeaweedFS and logs the run + artefacts to MLflow; the FastAPI server's background loader polls the registry for models:/fraud-detector@production and loads the model once the alias exists.
The end state must include:

MLflow experiment fraud-detection has at least one run; run artefacts are in the mlflow-artifacts SeaweedFS bucket.
A Registered Model named fraud-detector exists with the production alias assigned to the version sourced from the run, set in code by register.py.
POST http://localhost:8085/predict with {"features": [100.5, 12, 3]} returns {"prediction": 0} or {"prediction": 1} (tests poll up to 60 s).
This task builds the serving path of the platform: training logs a run + artefacts to MLflow (backed by SeaweedFS object storage), the registry production alias is the stable handle production code targets (models:/fraud-detector@production), and the serving process resolves that alias at load time — so promoting a new model later is an alias move, not a redeploy.




