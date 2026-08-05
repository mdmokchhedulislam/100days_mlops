FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir flask

COPY webhook_sink.py /app/webhook_sink.py

EXPOSE 5000
CMD ["python3", "/app/webhook_sink.py"]