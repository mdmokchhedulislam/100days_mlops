The xFusionCorp Industries ML platform team operates an asynchronous fraud-detection scoring system, ensuring that the HTTP entry point responds within single-digit milliseconds while the model processes data in a background worker. The scaffold for this process, located at /root/code/serving/async_app.py, is designed to delegate tasks to a background worker and is intended to persist the results of each task in Redis. However, the implementation for storing results in Redis has not yet been completed.

Your objective is to implement the Redis round-trip within async_app.py. This involves storing each result in Redis after the worker has completed its task. In addition, you must ensure that the GET /result/<task_id> endpoint retrieves the stored results. The expected workflow is for clients to submit a request through POST /predict-async, then to subsequently poll the results using GET /result/<task_id>, which should return an is_fraud flag corresponding to the submitted payload.


Flask + redis-py are installed at startup. A Redis container named async-redis is already running on host port 6379.

The project layout under /root/code/serving/:

model.pkl – Deterministic RandomForest trained at startup.
async_app.py – Flask app. The Redis connection, /health, POST /predict-async (returns a task_id, runs the model on a background thread), and the thread itself are wired. Two things are left as TODOs to author: the worker's result store in Redis, and the GET /result/<task_id> lookup that reads it back.
The end state must include:

redis.Redis(host="localhost", port=6379, ...) in async_app.py.
GET /result/<task_id> reads the stored value back from Redis and returns it as part of the JSON body.
POST /predict-async returns a JSON body carrying a task_id; after a short poll, GET /result/<task_id> returns a JSON body carrying an is_fraud flag of 0 or 1.
The background worker stores results at keys shaped result:<task_id>, with a 600-second TTL.


