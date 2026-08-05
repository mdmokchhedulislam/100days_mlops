"""Evidently drift scorer for the Monitoring-section labs.

Builds a fixed *reference* window of fraud-transaction features once,
then loops forever. Every cycle it:

1. Synthesizes a fresh *current* window whose distribution slowly walks
   away from (and back toward) the reference — so drift rises and falls
   the way a real production feed would.
2. Scores per-column drift with Evidently (`ValueDrift`, PSI) and the
   dataset-level drifted-columns share (`DriftedColumnsCount`).
3. Atomically rewrites `drift_scores.json` next to this script. The
   metric-emitter container bind-mounts this directory read-only and
   republishes the scores as the `data_drift_score{column}` and
   `evidently_drift_share` Prometheus gauges.
4. Every few cycles, saves the full Evidently report as
   `drift_report.html` so the latest scoring window can be inspected.
5. If `DRIFT_WORKSPACE` is set, also publishes every few cycles' run
   to that Evidently workspace — the project behind the lab's
   Evidently UI button accumulates one report per publish, so the
   UI's Dashboard tab plots drift over time.
"""
import json
import math
import os
import time

import numpy as np
import pandas as pd
from evidently import Dataset, DataDefinition, Report
from evidently.metrics import DriftedColumnsCount, ValueDrift

HERE = os.path.dirname(os.path.abspath(__file__))
SCORES_PATH = os.path.join(HERE, "drift_scores.json")
REPORT_PATH = os.path.join(HERE, "drift_report.html")

COLUMNS = ["amount", "hour", "num_tx_past_day"]
ROWS = 300
CYCLE_SECONDS = 15
REPORT_EVERY_N_CYCLES = 4

# Optional: publish runs to an Evidently workspace (the UI button).
WORKSPACE_DIR = os.environ.get("DRIFT_WORKSPACE", "")
PROJECT_NAME = os.environ.get("DRIFT_PROJECT", "fraud-detector drift monitoring")
PUBLISH_EVERY_N_CYCLES = 4


def _make_window(rng: np.random.Generator, shift: float) -> pd.DataFrame:
    """One window of fraud-transaction features.

    `shift = 0.0` reproduces the reference distribution; larger values
    push every column further away from it.
    """
    amount = rng.normal(120.0 * (1.0 + shift), 40.0, ROWS).clip(min=1.0)

    # A `shift`-sized slice of transactions migrates into late-night hours.
    late_share = min(max(shift, 0.0), 0.9)
    late_mask = rng.random(ROWS) < late_share
    hour = rng.integers(0, 24, ROWS)
    hour[late_mask] = rng.integers(18, 24, int(late_mask.sum()))

    num_tx = rng.poisson(4.0 * (1.0 + shift), ROWS)

    return pd.DataFrame(
        {"amount": amount.round(2), "hour": hour, "num_tx_past_day": num_tx}
    )


def _build_metrics():
    """Per-column PSI metrics + the dataset-level drifted-columns share.

    PSI keeps the published score on the 'higher = more drift' scale the
    labs' Grafana panels describe. If this Evidently build doesn't take
    a `method` kwarg, fall back to the column default — the score stays
    in [0, 1] either way.
    """
    try:
        per_column = [ValueDrift(column=c, method="psi") for c in COLUMNS]
    except TypeError:
        per_column = [ValueDrift(column=c) for c in COLUMNS]
    return per_column + [DriftedColumnsCount()]


def _extract(result_dict: dict):
    """Pull {column: score} + drift share out of `Report(...).run().dict()`."""
    scores: dict = {}
    share = 0.0
    drifted = 0
    for m in result_dict.get("metrics", []) or []:
        name = str(m.get("metric_name") or m.get("metric_id") or "")
        value = m.get("value")
        if name.startswith("ValueDrift(column="):
            column = name[len("ValueDrift(column="):].split(",")[0].rstrip(")")
            try:
                scores[column] = round(float(value), 4)
            except (TypeError, ValueError):
                continue
        elif "DriftedColumnsCount" in name and isinstance(value, dict):
            share = round(float(value.get("share", 0.0)), 4)
            drifted = int(float(value.get("count", 0)))
    return scores, share, drifted


def _write_json_atomic(path: str, payload: dict) -> None:
    """tmp-file + rename so the emitter never reads a half-written JSON."""
    tmp = f"{path}.tmp"
    with open(tmp, "w") as fh:
        json.dump(payload, fh, indent=2)
    os.replace(tmp, path)


def main() -> None:
    rng_ref = np.random.default_rng(42)
    reference = _make_window(rng_ref, shift=0.0)
    ref_ds = Dataset.from_pandas(reference, data_definition=DataDefinition())

    workspace = project = None
    if WORKSPACE_DIR:
        # Lazy import: headless labs never pay for the UI machinery.
        from evidently.ui.workspace import Workspace

        workspace = Workspace.create(WORKSPACE_DIR)
        found = workspace.search_project(PROJECT_NAME)
        project = found[0] if found else workspace.create_project(PROJECT_NAME)

    rng_cur = np.random.default_rng(99)
    cycle = 0
    while True:
        # Drift breathes: a slow sine sweep plus per-cycle noise, so the
        # per-column PSI climbs and recedes over the life of the lab.
        shift = 0.20 + 0.18 * math.sin(2 * math.pi * cycle / 40.0)
        shift += float(rng_cur.uniform(-0.03, 0.03))
        current = _make_window(rng_cur, shift=max(shift, 0.0))
        cur_ds = Dataset.from_pandas(current, data_definition=DataDefinition())

        try:
            result = Report(_build_metrics()).run(
                current_data=cur_ds, reference_data=ref_ds
            )
            scores, share, drifted = _extract(result.dict())
            if scores:
                payload = {
                    "source": "evidently",
                    "method": "psi",
                    "drift_scores": scores,
                    "drift_share": share,
                    "drifted_columns": drifted,
                    "rows_scored": ROWS,
                    "cycle": cycle,
                }
                _write_json_atomic(SCORES_PATH, payload)
            if cycle % REPORT_EVERY_N_CYCLES == 0:
                result.save_html(REPORT_PATH)
            if workspace is not None and cycle % PUBLISH_EVERY_N_CYCLES == 0:
                workspace.add_run(project.id, result)
        except Exception as exc:  # noqa: BLE001 — keep the loop alive
            print(f"[drift-scorer] cycle {cycle} failed: {exc}", flush=True)

        cycle += 1
        time.sleep(CYCLE_SECONDS)


if __name__ == "__main__":
    main()