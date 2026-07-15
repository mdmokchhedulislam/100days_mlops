"""
BentoML service exposing the fraud-detection RandomForest.

Loads `fraud_detector:latest` from the BentoML model store (saved at
startup) and serves it with the modern `@bentoml.service` class API:
  - POST /predict           — score one transaction.
  - POST /last_predictions  — audit log of every POST /predict
                              handled since the server booted.

`bentoml serve service:FraudService` starts the HTTP server on port
3000 and auto-generates a Swagger UI at the server's root — the
primary GUI surface for this lab.
"""

from typing import Any, Dict, List

import bentoml
import numpy as np


@bentoml.service(name="fraud_service")
class FraudService:
    # Declare the model dependency from the BentoML model store
    bento_model = bentoml.models.BentoModel("fraud_detector:latest")

    def __init__(self) -> None:
        # Load the registered model
        self.model = bentoml.sklearn.load_model(self.bento_model)

        # Store prediction history
        self._history: List[Dict[str, Any]] = []

    @bentoml.api
    def predict(
        self,
        amount: float,
        hour: int,
        num_tx_past_day: int,
    ) -> Dict[str, Any]:
        """
        Predict whether a transaction is fraudulent.

        Args:
            amount: Transaction amount
            hour: Hour of transaction (0-23)
            num_tx_past_day: Number of transactions in the last day

        Returns:
            {"is_fraud": 0} or {"is_fraud": 1}
        """

        # Build feature vector (2D array required by scikit-learn)
        features = np.array([[amount, hour, num_tx_past_day]])

        # Predict
        prediction = self.model.predict(features)

        # Convert numpy type to Python int
        is_fraud = int(prediction[0])

        # Save request to history
        self._history.append(
            {
                "amount": amount,
                "hour": hour,
                "num_tx_past_day": num_tx_past_day,
                "is_fraud": is_fraud,
            }
        )

        # Return prediction
        return {"is_fraud": is_fraud}

    @bentoml.api
    def last_predictions(self) -> Dict[str, Any]:
        """
        Return all predictions made since the server started.
        """


        return {
            "count": len(self._history),
            "predictions": self._history,
        }