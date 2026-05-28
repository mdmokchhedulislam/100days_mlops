import pandas as pd
import json
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score

os.makedirs("models", exist_ok=True)

train = pd.read_csv("data/processed/train.csv")
X_train = train.drop(columns=["is_fraud", "transaction_id", "merchant"])
X_train = pd.get_dummies(X_train, columns=["category"])
y_train = train["is_fraud"]

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

preds = model.predict(X_train)
metrics = {
    "accuracy": round(accuracy_score(y_train, preds), 4),
    "f1_score": round(f1_score(y_train, preds, zero_division=0), 4),
}

joblib.dump(model, "models/model.pkl")
with open("metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

print(f"Metrics: {metrics}")