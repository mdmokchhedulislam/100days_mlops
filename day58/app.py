

"""FastAPI fraud-detection prediction service.

Exposes:
  - GET  /health               — liveness check.
  - POST /predict              — score one transaction.
  - GET  /last-predictions     — audit log of every POST /predict
                                 received since the server booted.
  - GET  /docs                 — auto-generated Swagger UI.
"""

from typing import List

import joblib
import numpy as np
import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

MODEL_PATH = "/root/code/serving/model.pkl"
MODEL = joblib.load(MODEL_PATH)

app = FastAPI(
    title="xFusionCorp Fraud-Detection API",
    description=(
        "Synchronous inference for the fraud-detection RandomForest. "
        "Submit predictions interactively from this Swagger UI with "
        "the `Try it out` panel on `/predict`."
    ),
    version="1.0.0",
)

prediction_history: List[dict] = []


class PredictRequest(BaseModel):
    amount: float = Field(..., ge=0, description="Transaction amount")
    hour: int = Field(..., ge=0, le=23, description="Hour of transaction (0-23)")
    num_tx_past_day: int = Field(..., ge=0, description="Number of transactions in the past day")


class PredictResponse(BaseModel):
    is_fraud: int = Field(..., description="1 if the model flags fraud, else 0.")


class HistoryEntry(BaseModel):
    amount: float
    hour: int
    num_tx_past_day: int
    is_fraud: int


class HistoryResponse(BaseModel):
    count: int
    predictions: List[HistoryEntry]


@app.get("/", include_in_schema=False)
def root():
    """Redirect root to Swagger UI."""
    return RedirectResponse(url="/docs")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest) -> PredictResponse:

    # Build feature vector
    features = np.array([
        [req.amount, req.hour, req.num_tx_past_day]
    ])

    # Predict
    prediction = int(MODEL.predict(features)[0])

    # Save prediction history
    prediction_history.append({
        "amount": req.amount,
        "hour": req.hour,
        "num_tx_past_day": req.num_tx_past_day,
        "is_fraud": prediction
    })

    # Return response
    return PredictResponse(is_fraud=prediction)


@app.get("/last-predictions", response_model=HistoryResponse)
def last_predictions() -> HistoryResponse:
    return HistoryResponse(
        count=len(prediction_history),
        predictions=[HistoryEntry(**p) for p in prediction_history],
    )


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8085,
        reload=False,
    )


# """FastAPI fraud-detection prediction service.

# Exposes:
#   - GET  /health               — liveness check.
#   - POST /predict              — score one transaction.
#   - GET  /last-predictions     — audit log of every POST /predict
#                                  received since the server booted.
#   - GET  /docs                 — auto-generated Swagger UI.
# """
# from typing import List

# import joblib
# import numpy as np
# from fastapi import FastAPI, HTTPException
# from fastapi.responses import RedirectResponse
# from pydantic import BaseModel, Field

# MODEL_PATH = "/root/code/serving/model.pkl"
# MODEL = joblib.load(MODEL_PATH)

# app = FastAPI(
#     title="xFusionCorp Fraud-Detection API",
#     description=(
#         "Synchronous inference for the fraud-detection RandomForest. "
#         "Submit predictions interactively from this Swagger UI with "
#         "the `Try it out` panel on `/predict`."
#     ),
#     version="1.0.0",
# )

# prediction_history: List[dict] = []


# # class PredictRequest(BaseModel):
# #     # TODO 1: declare the three typed request fields. Their types (and
# #     #         constraints) drive FastAPI's automatic request validation
# #     #         and the Swagger schema — an out-of-range value is rejected
# #     #         with HTTP 422 before the handler runs:
# #     #           amount           : float
# #     #           hour             : int constrained to 0-23  (ge=0, le=23)
# #     #           num_tx_past_day  : int, non-negative         (ge=0)
# #     #         Use pydantic Field(...) for the constraints, e.g.
# #     #           hour: int = Field(..., ge=0, le=23)
# #     pass


# class PredictRequest(BaseModel):
#     amount: float = Field(..., ge=0)
#     hour: int = Field(..., ge=0, le=23)
#     num_tx_past_day: int = Field(..., ge=0)


# class PredictResponse(BaseModel):
#     is_fraud: int = Field(..., description="1 if the model flags fraud, else 0.")


# class HistoryEntry(BaseModel):
#     amount: float
#     hour: int
#     num_tx_past_day: int
#     is_fraud: int


# class HistoryResponse(BaseModel):
#     count: int
#     predictions: List[HistoryEntry]






# @app.get("/", include_in_schema=False)
# def root():
#     """Redirect the bare root to the Swagger UI so the platform's
#     port-forward button lands directly on the interactive docs."""
#     return RedirectResponse(url="/docs")


# @app.get("/health")
# def health():
#     return {"status": "ok"}


# @app.post("/predict", response_model=PredictResponse)
# def predict(req: PredictRequest) -> PredictResponse:

#     features = np.array([
#         [req.amount, req.hour, req.num_tx_past_day]
#     ])

#     prediction = int(MODEL.predict(features)[0])

#     prediction_history.append({
#         "amount": req.amount,
#         "hour": req.hour,
#         "num_tx_past_day": req.num_tx_past_day,
#         "is_fraud": prediction
#     })

#     return PredictResponse(
#         is_fraud=prediction
#     )

# @app.get("/last-predictions", response_model=HistoryResponse)
# def last_predictions() -> HistoryResponse:
#     return HistoryResponse(
#         count=len(prediction_history),
#         predictions=[HistoryEntry(**p) for p in prediction_history],
#     )