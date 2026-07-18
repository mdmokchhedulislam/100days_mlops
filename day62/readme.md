The xFusionCorp Industries ML platform team has deployed a new fraud-detection model into production, utilizing an A/B router to manage traffic. The traffic distribution is set at 80% for the stable MODEL_V1 and 20% for the candidate MODEL_V2. Each response from the server includes a model_version field, enabling downstream monitoring to accurately attribute each prediction to the corresponding model. The ab_server.py scaffold, located at /root/code/serving/, is responsible for loading both models and parsing incoming requests; however, the routing logic has yet to be implemented. Your task is to develop the A/B routing functionality in ab_server.py, ensuring that approximately 80% of traffic is directed to MODEL_V1, 20% to MODEL_V2, and that all responses correctly indicate which model provided the prediction.


Flask is installed at startup (not part of the lab image by default). Two model versions are pre-trained: model_v1.pkl (10-tree RandomForest) and model_v2.pkl (50-tree RandomForest). Both live under /root/code/serving/.

The project layout under /root/code/serving/:

model_v1.pkl + model_v2.pkl – The two model versions the router multiplexes between. Correct.
ab_server.py – Flask app. /health, both model loads, and the request-body parsing in POST /predict are wired; the routing logic (split, model selection, response) is left as a TODO to author.
The end state must include:

ab_server.py splits traffic 80 % to MODEL_V1 and 20 % to MODEL_V2.
Every response to POST /predict carries both is_fraud and model_version; model_version is "v1" or "v2".
Over a batch of 200 requests, roughly 160 land on v1 (±20) and roughly 40 land on v2 (±20).
Flask reads the JSON body via request.get_json(); the scaffold already handles this.