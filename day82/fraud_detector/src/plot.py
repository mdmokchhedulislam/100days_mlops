"""Generate a confusion-matrix PNG alongside the metrics JSON.

Synthetic data -- the numbers are seeded so every workflow run produces
a deterministic image suitable for pinning as a CI artefact. No real
model quality reasoning (MLOps-not-ML).
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ARTIFACTS = Path("artifacts")


def _confusion_matrix() -> np.ndarray:
    # Deterministic synthetic confusion matrix.
    return np.array(
        [
            [148, 12],
            [18, 22],
        ]
    )


def main() -> None:
    ARTIFACTS.mkdir(exist_ok=True)
    metrics_path = ARTIFACTS / "metrics.json"
    metrics = (
        json.loads(metrics_path.read_text()) if metrics_path.exists() else {}
    )

    matrix = _confusion_matrix()
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.imshow(matrix, cmap="Blues")
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(["not_fraud", "fraud"])
    ax.set_yticklabels(["not_fraud", "fraud"])
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title(
        f"Fraud-detector confusion matrix (acc={metrics.get('accuracy', 'n/a')})"
    )
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(
                j, i, str(matrix[i, j]),
                ha="center", va="center",
                color="black" if matrix[i, j] < matrix.max() / 2 else "white",
            )
    fig.tight_layout()
    out = ARTIFACTS / "confusion_matrix.png"
    fig.savefig(out, dpi=110)
    plt.close(fig)
    print(f"Wrote {out.resolve()}")


if __name__ == "__main__":
    main()