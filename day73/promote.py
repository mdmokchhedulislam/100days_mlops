"""Champion/challenger promotion gate.

A drift-triggered retrain registered a new challenger version of
`fraud-detector` (v2). The incumbent (v1) currently serves production
traffic via the `production` alias.
"""

from mlflow import MlflowClient

TRACKING_URI = "http://localhost:5000"
MODEL = "fraud-detector"
PROD_ALIAS = "production"
CHALLENGER_VERSION = "2"

client = MlflowClient(tracking_uri=TRACKING_URI)


def f1_of(version: str) -> float:
    """Read the f1_score metric logged on a model version's run."""
    mv = client.get_model_version(MODEL, version)
    run = client.get_run(mv.run_id)
    return run.data.metrics["f1_score"]


def main() -> None:
    # Get the current production model (champion)
    champion = client.get_model_version_by_alias(MODEL, PROD_ALIAS)
    champion_version = champion.version

    # Read evaluation metrics
    champion_f1 = f1_of(champion_version)
    challenger_f1 = f1_of(CHALLENGER_VERSION)

    print(f"Champion (v{champion_version}) f1_score = {champion_f1}")
    print(f"Challenger (v{CHALLENGER_VERSION}) f1_score = {challenger_f1}")

    # Promote only if challenger is strictly better
    if challenger_f1 > champion_f1:
        client.set_registered_model_alias(
            MODEL,
            PROD_ALIAS,
            CHALLENGER_VERSION,
        )
        print(f"Promoted version {CHALLENGER_VERSION} to alias '{PROD_ALIAS}'")
    else:
        print(
            f"Rejected challenger v{CHALLENGER_VERSION}; "
            f"production remains on v{champion_version}"
        )


if __name__ == "__main__":
    main()