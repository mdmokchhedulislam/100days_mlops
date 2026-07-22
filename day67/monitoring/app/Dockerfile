FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir flask prometheus-client

COPY metric_emitter.py /app/metric_emitter.py

EXPOSE 5000
CMD ["python3", "/app/metric_emitter.py"]