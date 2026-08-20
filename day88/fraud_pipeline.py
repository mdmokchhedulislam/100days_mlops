"""Prefect 3.x flow for the fraud-detection pipeline.

Structure: prep -> train -> evaluate. Each step is a `@task`-decorated
function.
"""

from __future__ import annotations

from prefect import flow, task


@task(name="prep")
def prep() -> dict:
    print("[prep] preparing training data")
    return {"rows": 100, "path": "/tmp/train.csv"}


@task(name="train")
def train(data: dict) -> str:
    print(f"[train] fitting model on {data['rows']} rows from {data['path']}")
    return "model-v1"


@task(name="evaluate")
def evaluate(model: str) -> float:
    print(f"[evaluate] scoring model {model}")
    return 0.75


@flow(name="fraud-pipeline")
def fraud_pipeline() -> float:
    data = prep()
    model = train(data)
    score = evaluate(model)

    print(f"[flow] final score={score}")

    return score


if __name__ == "__main__":
    fraud_pipeline.serve(
        name="fraud-pipeline",
        tags=["lab"]
    )