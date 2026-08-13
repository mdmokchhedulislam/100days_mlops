FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir flask numpy scikit-learn joblib

COPY src/ /app/src/

ENV PYTHONPATH=/app
EXPOSE 5000

CMD ["python3", "-m", "src.serve"]