The xFusionCorp Industries ML platform team attempted to implement a complete end-to-end monitoring stack for the fraud-detection model. This stack includes an Evidently drift scorer connected to a Flask metric-emitter, which is then scraped by Prometheus and visualized using Grafana. However, the monitoring flow is currently non-functional. Grafana displays empty panels, Prometheus indicates that the metric-emitter is DOWN on the Targets page, and attempts to access the emitter's /metrics endpoint result in a 404 error. The Evidently scorer itself is operational, as evidenced by the presence of drift scores in the hand-off file; however, all downstream components are failing, preventing any signals from reaching the dashboard. Within the stack's configuration, there are three wiring issues that need to be addressed. Your primary objective is to identify and resolve all three issues, and subsequently, to construct a tagged monitoring overview dashboard in Grafana.


The stack is at /root/code/monitoring/ with three services defined in docker-compose.yml, plus the host-side Evidently scorer:

metric-emitter – Flask exporter (Python source bind-mounted). Republishes the Evidently drift scores as data_drift_score{column} / evidently_drift_share next to its own serving signals.
mon-prometheus – Port 9090.
mon-grafana – Port 3000, admin / grafana2026. The Prometheus datasource is provisioned on boot.
Evidently drift scorer – host process (drift/drift_scorer.py), rescores per-feature PSI every 15 s into drift/drift_scores.json and publishes a run to the Evidently UI (port 8000) every ~minute. Healthy—not part of the bug hunt. The Evidently UI button -> fraud-detector drift monitoring -> Dashboard tab confirms drift data is flowing at the source; everything downstream of it is what's broken.
Three integration bugs must be diagnosed and fixed — each lives in exactly one configuration file under /root/code/monitoring/. The symptoms:

metric-emitter's /metrics endpoint returns 404.

Prometheus's Targets page lists metric-emitter as DOWN.

Grafana renders empty panels even when Prometheus has fresh samples.

Start from the emitter itself — curl -i http://localhost:5000/metrics shows the 404, and docker compose ps from /root/code/monitoring/ shows what is running. The affected services must be reloaded for the fixed configs to take effect.

A tagged monitoring-overview dashboard must also be built in Grafana (port 3000, the Grafana button, admin / grafana2026): three panels covering request rate, p95 inference latency, and prediction accuracy (or similar signals from the shared metric-emitter, e.g. the Evidently-computed data_drift_score), saved with a title and at least one tag (e.g. mlops or monitoring) so the ops team can find it from the Dashboards search.

The end state must include:

curl -sf http://localhost:5000/metrics returns HTTP 200.
Prometheus GET /api/v1/targets lists the metric-emitter job with health: "up".
Grafana GET /api/datasources shows the Prometheus datasource URL ending in :9090.
One user-created dashboard has 3 or more panels and at least one tag.
The Evidently UI's project keeps accumulating scoring runs (pre-wired—nothing to change).
A monitoring stack is only as useful as its weakest link. Evidently can score drift perfectly and still page nobody: each of these three bugs is silent on its own—none of them crashes a container—but together they cost you every metric Grafana would otherwise surface. The capstone is reading failure symptoms back to their config file, not retyping Python.