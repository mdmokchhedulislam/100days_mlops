Your task is to finalize the app.py file by defining the typed request model and implementing the /predict handler. Additionally, ensure the server operates on port 8085, and verify that it successfully scores transactions through the Swagger UI while rejecting any invalid input.


FastAPI + uvicorn are baked into the lab image. The FastAPI Swagger UI button opens /docs once the server is running on port 8085.

The project layout under /root/code/serving/:

model.pkl – Deterministic RandomForest trained at startup on the shared amount / hour / num_tx_past_day → is_fraud synthetic dataset.
train.csv – The 10-row source used to fit the model.
app.py – FastAPI app. /health, the root→/docs redirect, the response models, and GET /last-predictions are wired. Two things are left as TODOs to author:
TODO 1 – the PredictRequest model's three typed fields (amount, hour, num_tx_past_day), with types and range constraints that drive FastAPI's request validation + Swagger schema.
TODO 2 – the POST /predict handler body (which returns 501 until authored): build the feature row, score it with MODEL.predict(...), record it, and return PredictResponse.
The end state must include:

The Swagger UI at /docs is reachable (the FastAPI Swagger UI button loads it).
POST /predict with a valid payload returns {"is_fraud": 0} or {"is_fraud": 1} (HTTP 200).
Two distinct payloads return different is_fraud values – The handler reads the posted features.
POST /predict with an out-of-range field (e.g. hour: 25) returns HTTP 422 – The typed model rejects invalid input before the handler runs.
Suggested payloads: {"amount": 3200, "hour": 23, "num_tx_past_day": 5} (high-value, late-night—expected to flag fraud); {"amount": 25.5, "hour": 10, "num_tx_past_day": 1} (low-value, daytime—expected to pass).




