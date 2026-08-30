import os

# ফোল্ডারগুলোর তালিকা
folders = [
    ".gitea/workflows",
    "data/raw",
    "data/processed",
    "src/data",
    "src/training",
    "src/serving",
    "tests",
    "configs",
    "models",
    "metrics",
    "docker",
    "k8s/kserve",
    "argo",
    "monitoring/prometheus",
    "monitoring/grafana",
    "monitoring/evidently",
]

# ফাইলগুলোর তালিকা
files = [
    ".gitea/workflows/ci.yml",
    ".gitea/workflows/cd.yml",
    ".gitea/workflows/release.yml",
    "dvc.yaml",
    "dvc.lock",
    "params.yaml",
    "src/__init__.py",
    "src/data/__init__.py",
    "src/data/ingest.py",
    "src/data/validate.py",
    "src/data/preprocess.py",
    "src/training/__init__.py",
    "src/training/train.py",
    "src/training/evaluate.py",
    "src/serving/__init__.py",
    "src/serving/predictor.py",
    "tests/__init__.py",
    "tests/test_data.py",
    "tests/test_train.py",
    "tests/test_api.py",
    "configs/config.yaml",
    "metrics/metrics.json",
    "docker/training.Dockerfile",
    "docker/serving.Dockerfile",
    "k8s/namespace.yaml",
    "k8s/serviceaccount.yaml",
    "k8s/kserve/inference-service.yaml",
    "k8s/kserve/predictor.yaml",
    "argo/training-workflow.yaml",
    "argo/retraining-cronworkflow.yaml",
    "docker-compose.yml",
    "Makefile",
    "pyproject.toml",
    ".pre-commit-config.yaml",
    "README.md",
]

def create_project_structure():
    print("Creating project folders and files...")
    
    # ফোল্ডার তৈরি
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"Created Folder: {folder}")
        
    # ফাইল তৈরি
    for file in files:
        if not os.path.exists(file):
            with open(file, "w", encoding="utf-8") as f:
                pass  # খালি ফাইল তৈরি করবে
            print(f"Created File: {file}")
            
    print("\nProject structure created successfully! 🚀")

if __name__ == "__main__":
    create_project_structure()