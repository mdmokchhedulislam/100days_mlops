The xFusionCorp Industries ML platform team requires the fraud-detector model to undergo retraining on a fixed schedule without manual intervention. A CronWorkflow scaffold is available at /root/code/argo/fraud-retraining.yaml, but it is incomplete; it currently lacks a schedules cron expression and the retraining step is only a placeholder. Your objective is to complete the CronWorkflow by adding the appropriate schedule and defining the retraining step. Once completed, apply the CronWorkflow to the argo namespace and verify in the Argo UI that it activates and initiates retraining runs as scheduled.


The scaffold is at /root/code/argo/fraud-retraining.yaml. It is NOT applied yet — the Argo UI's Cron Workflows page (port 5000) stays empty until the CronWorkflow is applied to the argo namespace.

Two TODO-marked pieces are missing from the YAML:

TODO 1 — schedule: the schedules: list with its cron expression is absent, so the cron has no cadence to fire on. It needs to fire frequently enough that a run appears within the grading window (a minute or so).
TODO 2 — retraining step: the step is only a stub. It should run a stand-in retraining command that exits 0 — an echo is enough, since this section teaches orchestration, not model quality.
With the CronWorkflow applied, the Cron Workflows page should show fraud-retraining active (no Suspended badge) with a nextScheduledTime ≤ 60 s out, and within one schedule tick a child Workflow should appear under it and run to Succeeded.

The end state must include:

GET /api/v1/cron-workflows/argo/fraud-retraining returns the cron with a non-empty schedules and spec.suspend not true.
At least one Workflow labelled workflows.argoproj.io/cron-workflow=fraud-retraining (the owner-label Argo adds to every cron-spawned run) reaches Succeeded. Tests poll up to 240 s.
A CronWorkflow is Argo's scheduled-run primitive: schedules is the cron cadence and workflowSpec is the Workflow it fires each tick. This is how retraining runs on autopilot—no human clicking Submit—with concurrencyPolicy: Forbid ensuring a slow run never overlaps the next tick.