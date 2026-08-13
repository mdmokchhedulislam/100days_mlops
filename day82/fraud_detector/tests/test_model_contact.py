"""Contract tests for the serialised fraud-detector model.

The contract jobs asserts the shape of the model produced by
``src.train.train`` -- that it ships a ``predict`` method, emits
integer 0/1 labels, and its input dimensionality matches what the
serving layer expects. Synthetic fixtures only.
"""
from __future__ import annotations

import numpy as np

from src.train import FEATURES, train


def test_model_exposes_predict() -> None:
    model = train()["model"]
    assert hasattr(model, "predict"), "model must expose a predict(...) method"


def test_prediction_shape_matches_batch_size() -> None:
    model = train()["model"]
    batch = np.zeros((7, FEATURES))
    out = model.predict(batch)
    assert out.shape == (7,), f"Unexpected prediction shape: {out.shape}"


def test_prediction_labels_are_binary() -> None:
    model = train()["model"]
    batch = np.zeros((10, FEATURES))
    preds = model.predict(batch)
    assert set(np.unique(preds).tolist()).issubset({0, 1}), (
        "Model must return 0/1 labels only"
    )