The xFusionCorp Industries ML platform team has deployed the fraud-detection model using BentoML. The model is registered in BentoML's local store and is served over HTTP with the command bentoml serve, which automatically generates a Swagger UI at the server's root. Within the scaffold located at /root/code/serving/service.py, the modern @bentoml.service class API is utilized. This script loads the pre-registered fraud_detector:latest model from the store and defines the APIs, although the POST /predict handler remains unimplemented. Your objective is to implement the /predict handler to score a transaction using the loaded model. Additionally, you need to start the server on port 3000 and verify that it returns predictions.


The fraud_detector model is registered in BentoML's local store. The BentoML server is NOT pre-started — the BentoML UI button opens the Swagger surface once the server is running on port 3000.

The project layout under /root/code/serving/:

service.py – BentoML service (@bentoml.service class FraudService). The model-store load (bentoml.models.BentoModel + bentoml.sklearn.load_model in __init__) and the last_predictions API are wired. The predict handler body is left as a TODO — it returns an error until authored. The handler takes the amount/hour/num_tx_past_day parameters and returns {"is_fraud": <int>}.
train.csv – The 10-row source used at startup to train and register the model with bentoml.sklearn.save_model("fraud_detector", model).
The end state must include:

bentoml models list lists fraud_detector in the store.
curl http://localhost:3000/ returns HTTP 200 – The Swagger UI is reachable once the server is running.
POST /predict with a valid payload returns {"is_fraud": 0} or {"is_fraud": 1}.
Two distinct payloads return different is_fraud values – The handler scores the posted features.
Suggested payloads: {"amount": 3200, "hour": 23, "num_tx_past_day": 5} (high-value, late-night—expected to flag fraud); {"amount": 25.5, "hour": 10, "num_tx_past_day": 1} (low-value, daytime).