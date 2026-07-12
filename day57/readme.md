 Serve an ML Model with Flask

 The xFusionCorp Industries ML platform team serves the fraud-detection model over HTTP with a Flask app so downstream services can score transactions synchronously. A draft app.py at /root/code/serving/ loads the pre-trained model and declares /health + /predict, but the server binds to the wrong port and the /predict handler is left unimplemented. Your task is to author the /predict handler and bind the server to the exposed port, start the server, and confirm two distinct payloads produce two distinct responses.


Flask is installed at startup (it is not part of the lab image by default).

The project layout under /root/code/serving/:

model.pkl – Deterministic RandomForest trained at startup on the shared amount / hour / num_tx_past_day → is_fraud synthetic set. Correct and must remain intact.
train.csv – The 10-row training source used to fit model.pkl.
app.py – Flask app loading model.pkl and declaring GET /health + POST /predict. The /predict handler body is left as a TODO to author, and the app.run(...) bind port needs attention.
The end state must include:

curl http://localhost:8085/health returns {"status":"ok"} with HTTP 200.
curl -X POST http://localhost:8085/predict -H 'Content-Type: application/json' -d '{"amount":3200,"hour":23,"num_tx_past_day":5}' returns a JSON body with an is_fraud key.
The same POST with a low-amount daytime payload (e.g. {"amount":25.5,"hour":10,"num_tx_past_day":1}) returns a different is_fraud value – Confirming the endpoint actually reads the posted body rather than falling back to zeros.
The lab's port forwarding targets 8085; the running server must bind there to be reachable.





