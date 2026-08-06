"""Deterministic synthetic training script for the CI/CD section.

Emits a model plus a metrics report under ``artifacts/``. No real model
quality reasoning -- the numbers are seeded off ``SEED`` so every
workflow run produces identical outputs. The section teaches CI/CD
plumbing, not ML.
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
from sklearn.dummy import DummyClassifier

SEED = 42
ROWS = 200
FEATURES = 4


def _make_dataset(seed: int = SEED) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    features = rng.normal(size=(ROWS, FEATURES))
    labels = (rng.normal(size=ROWS) > 0).astype(int)
    return features, labels


def train(seed: int = SEED) -> dict:
    features, labels = _make_dataset(seed)
    model = DummyClassifier(strategy="most_frequent").fit(features, labels)
    metrics = {
        "accuracy": 0.82,
        "f1_score": 0.78,
        "training_rows": int(features.shape[0]),
        "seed": seed,
    }
    return {"model": model, "metrics": metrics}


def main() -> None:
    artefacts = Path("artifacts")
    artefacts.mkdir(exist_ok=True)
    result = train()
    joblib.dump(result["model"], artefacts / "model.joblib")
    (artefacts / "metrics.json").write_text(
        json.dumps(result["metrics"], indent=2) + "\n"
    )
    print(f"Wrote artefacts to {artefacts.resolve()}")


if __name__ == "__main__":
    main()