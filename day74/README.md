The xFusionCorp Industries ML platform team requires the ability to track total fraudulent transaction amounts in USD, in addition to standard model-serving signals. This data should be sliceable by model version on demand from a Grafana dashboard.

The monitoring stack is operational, and the Flask metric emitter is located at /root/code/monitoring/app/metric_emitter.py, which is bind-mounted into the container to allow for immediate recognition of edits after a restart. Grafana is already set up with a pre-provisioned Prometheus datasource.


Metric emitter. /root/code/monitoring/app/metric_emitter.py exposes the shared serving metrics. It needs a new fraud_amount_usd_total Counter carrying a version label, incremented inside the existing _nudge_metrics loop so each tick advances every version's total. After the emitter container is reloaded, Prometheus scrapes the new series.

Grafana dashboard. The Grafana UI is running on port 3000. The Grafana button opens the login page. Admin credentials: admin / grafana2026. The dashboard needs a templating variable named version (query-sourced from the Prometheus datasource via label_values(...)), and a panel whose query references fraud_amount_usd_total and filters by $version.

The end state must include:

Prometheus returns non-empty samples for fraud_amount_usd_total, with a version label on each series.
One dashboard carries a templating variable named version whose query uses label_values(...).
The same dashboard has a panel whose query references fraud_amount_usd_total and uses $version.
Template variables decouple a dashboard's structure from the cardinality of its labels—a single panel renders per-version when the variable is v1, v2, or All. The counter -> labelled series -> label_values -> $variable flow is the backbone of any multi-tenant or multi-version ML dashboard.