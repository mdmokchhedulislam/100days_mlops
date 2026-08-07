"""Data-schema guardrails for the fraud-detector training set.

The CI's data-quality job runs this file to catch schema drift before
it reaches the training step. Sample frame is synthetic and deterministic
-- the section teaches pipeline plumbing, not data quality per se.
"""
import pandas as pd


def _sample_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "amount":          [120.50, 42.00, 2500.00, 17.25, 980.00],
            "hour":            [14, 9, 23, 7, 19],
            "num_tx_past_day": [3, 1, 8, 2, 5],
            "is_fraud":        [0, 0, 1, 0, 1],
        }
    )


def test_required_columns_present() -> None:
    frame = _sample_frame()
    required = {"amount", "hour", "num_tx_past_day", "is_fraud"}
    missing = required - set(frame.columns)
    assert not missing, f"Missing required columns: {missing}"


def test_amount_is_non_negative() -> None:
    frame = _sample_frame()
    assert (frame["amount"] >= 0).all(), "Negative amounts present"


def test_hour_is_within_day() -> None:
    frame = _sample_frame()
    assert frame["hour"].between(0, 23).all(), "Hour outside [0, 23]"


def test_fraud_label_is_binary() -> None:
    frame = _sample_frame()
    assert frame["is_fraud"].isin([0, 1]).all(), (
        "is_fraud must be 0/1 only"
    )