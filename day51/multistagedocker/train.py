"""Fit a RandomForest on the shared 10-row synthetic fraud set and
persist the trained estimator to `/app/model.pkl` for the runtime
stage to load at container start-up.
"""
import io

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

DATA = """amount,hour,num_tx_past_day,is_fraud
25.50,8,1,0
1250.00,22,4,1
45.00,12,2,0
890.00,2,3,0
3200.00,23,5,1
12.99,9,1,0
567.00,17,2,0
2100.00,1,4,1
33.50,13,2,0
78.00,10,1,0"""

df = pd.read_csv(io.StringIO(DATA))
X = df.drop("is_fraud", axis=1).values
y = df["is_fraud"].values

model = RandomForestClassifier(n_estimators=10, random_state=42)
model.fit(X, y)

joblib.dump(model, "/app/model.pkl")
print("Model saved to /app/model.pkl")