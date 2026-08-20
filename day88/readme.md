The xFusionCorp Industries ML platform team is piloting Prefect 3.x as a second orchestrator alongside Argo Workflows. A teammate wired up a fraud-pipeline deployment with three steps—prep, train, evaluate—but on every run the Prefect Flow Run graph only shows two tracked nodes (prep and train); evaluate is missing. Your task is to fix the flow source, redeploy, trigger a new run from the Deployments page, and confirm the 3-node DAG.


The Prefect UI button at the top of the lab opens the UI on port 5000. Its Deployments page lists fraud-pipeline. Trigger a Quick Run and open the resulting Flow Run: its DAG renders only two nodes, and comparing that graph against the flow source is where the gap shows up.

The flow source is at /root/code/prefect/fraud_pipeline.py; the evaluate function runs as part of the flow but does not surface in the run graph the way the other two functions do. A shipped Makefile in that directory wraps the kill + restart cycle needed for the serve loop to pick up the new source (/var/log/prefect-serve.log confirms the new process is up).

After redeploying and triggering a fresh Quick Run, the Flow Run's DAG should render three nodes — prep → train → evaluate — each reaching Completed.

The end state must include:

Prefect's /api/deployments/name/fraud-pipeline/fraud-pipeline returns the deployment.
At least one Completed flow run under that deployment has three task runs whose names are exactly prep, train, and evaluate — Prefect's run graph now records evaluate alongside the other two.
Prefect's flow-run graph is built from the task-run records its orchestrator emits during execution. A function that runs as part of the flow but is not registered as a task disappears from the run graph entirely — it executes, but the orchestrator has no record of it.