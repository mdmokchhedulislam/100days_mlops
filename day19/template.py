import os

folders = [
    "fraud-detection/data/raw",
    "fraud-detection/data/processed",
    "fraud-detection/models",
    "fraud-detection/metrics",
    "fraud-detection/src/data",
    "fraud-detection/src/train",
    "fraud-detection/src/evaluate",
    "fraud-detection/.dvc"
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)

files = [
    "fraud-detection/dvc.yaml",
    "fraud-detection/params.yaml"
]

for file in files:
    open(file, "a").close()

print("Fraud Detection Project Structure Created Successfully!")