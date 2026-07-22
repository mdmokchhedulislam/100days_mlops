The xFusionCorp Industries ML platform team is in the process of implementing Grafana-based monitoring for their fraud-detection model. Although Prometheus and Grafana are already running in Docker, alongside a Flask metric emitter that provides live ML signals, Grafana currently lacks a configured data source, preventing the UI from accessing any metrics.

Your objective is to access the Grafana interface, configure the running Prometheus container as a data source through the Grafana UI, and create an initial dashboard panel that queries a live metric. This will ensure that the connection functions correctly end to end.


The Grafana UI is already running on port 3000. The Grafana button at the top of the lab opens the login page. Admin credentials: admin / grafana2026.

The stack running under /root/code/monitoring/ (via docker compose):

metric-emitter – Flask app exposing /metrics with flask_http_request_total{version}, prediction_accuracy, data_drift_score{column}, and model_inference_duration_seconds metrics. A background thread nudges the values every 5 seconds so panels built on top see real motion.
mon-prometheus – Prometheus, scraping metric-emitter:5000 every 5 seconds. Reachable inside the compose network as http://prometheus:9090.
mon-grafana – Grafana, no data sources configured.
The end state must include:

A data source of type prometheus exists in Grafana's configuration.
Its URL is http://prometheus:9090 (the compose service name – localhost:9090 does NOT work from inside the Grafana container).
Grafana's /api/datasources/uid/<uid>/health check reports status: OK.
At least one saved dashboard exists carrying a panel whose query targets a metric (a non-empty PromQL expression) — proof the data source actually returns data.
Grafana and Prometheus share a Docker network. Inside the Grafana container, localhost refers to Grafana itself, not to Prometheus.




