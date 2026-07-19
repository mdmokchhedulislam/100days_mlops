Serve Multiple Models Behind Unified API Gateway

The xFusionCorp Industries ML platform team operates three models for fraud detection and customer management, accessible via a single Nginx reverse proxy on port 8085: /fraud/, /churn/, and /recommend/, each routing to its respective Flask container. The fraud and churn services are already integrated in the docker-compose.yml and nginx.conf files. The directory for the recommend service, which contains a functioning application and Dockerfile, is available on disk. Your task is to integrate the recommend service into the docker-compose.yml, add the corresponding upstream and location block to the Nginx configuration, launch the stack, and verify that all routes respond appropriately.


The Docker daemon is already running. Base images (python:3.11-slim, nginx:alpine) are being pulled in the background at startup, so the first docker compose up -d returns in seconds.

The project layout under /root/code/serving/multi-model/:

fraud/app.py + fraud/Dockerfile – Flask service returning {"service": "fraud", "is_fraud": ...}. Correct.
churn/app.py + churn/Dockerfile – Flask service returning {"service": "churn", "churn_risk": ...}. Correct.
recommend/app.py + recommend/Dockerfile – Flask service returning {"service": "recommend", "items": [...]}. Correct — but not yet referenced by compose or nginx.
docker-compose.yml – Declares fraud, churn, and nginx services. The recommend service block is missing.
nginx.conf – Routes /fraud/ and /churn/ to their container upstreams. The recommend upstream + location block is missing.
The end state must include:

docker-compose.yml declares a recommend service that builds from ./recommend and carries container_name: mm-recommend.
nginx.conf declares a recommend upstream (server recommend:5000;) and a location /recommend/ block that proxies to it.
docker compose ps reports all four containers (mm-fraud, mm-churn, mm-recommend, mm-nginx) as Up.
curl -X POST http://localhost:8085/fraud/predict -d '{...}' returns a JSON body with "service": "fraud".
curl -X POST http://localhost:8085/churn/predict -d '{...}' returns a JSON body with "service": "churn".
curl -X POST http://localhost:8085/recommend/predict -d '{...}' returns a JSON body with "service": "recommend" and a non-empty items array.
Model the new entries on the existing fraud and churn blocks—same structure, same naming convention. After editing both files, docker compose up -d reads the new compose entry and builds the recommend image; nginx mounts the updated config from the host filesystem at container start.




test:
curl -X POST http://localhost:8085/fraud/predict \
-H "Content-Type: application/json" \
-d '{"amount":5000,"hour":14}'


curl -X POST http://localhost:8085/churn/predict \
-H "Content-Type: application/json" \
-d '{"age":35,"tenure":5,"balance":25000}'


curl -X POST http://localhost:8085/recommend/predict \
-H "Content-Type: application/json" \
-d '{"customer_id":101}'