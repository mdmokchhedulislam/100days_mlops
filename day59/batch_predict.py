"""Batch scorer for the fraud-detection RandomForest.

Reads `input.csv` (one row per transaction, columns: amount, hour,
num_tx_past_day), runs every row through the pre-trained model, and
writes `predictions.csv` with the original columns plus an integer
`prediction` class-label column.
"""
import joblib
import pandas as pd

MODEL_PATH = "/root/code/serving/model.pkl"
INPUT_CSV = "/root/code/serving/input.csv"
OUTPUT_CSV = "/root/code/serving/predictions.csv"

# 1. load the model from MODEL_PATH (joblib.load)
model = joblib.load(MODEL_PATH)

# 2. read INPUT_CSV into a DataFrame (pd.read_csv)
df = pd.read_csv(INPUT_CSV)

# 3. select the feature columns: amount, hour, num_tx_past_day
features = ['amount', 'hour', 'num_tx_past_day']
X = df[features]

# 4. add a `prediction` column of INTEGER class labels with
#    model.predict(...) — class labels (0/1), NOT the float
#    probabilities that predict_proba(...) would return
df['prediction'] = model.predict(X).astype(int)

# 5. write the DataFrame to OUTPUT_CSV with to_csv(..., index=False)
df.to_csv(OUTPUT_CSV, index=False)

# 6. print how many rows were written
print(f"Successfully wrote {len(df)} rows to {OUTPUT_CSV}")