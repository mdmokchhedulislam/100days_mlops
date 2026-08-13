"""Trivial unit tests for src.train -- the CI section does not
care about ML quality, only that the pipeline plumbing executes."""
from src.train import train


def test_train_returns_expected_keys() -> None:
    result = train()
    assert set(result) >= {"model", "metrics"}


def test_metrics_are_numeric() -> None:
    metrics = train()["metrics"]
    for key in ("accuracy", "f1_score"):
        assert isinstance(metrics[key], (int, float))


def test_training_rows_positive() -> None:
    assert train()["metrics"]["training_rows"] > 0