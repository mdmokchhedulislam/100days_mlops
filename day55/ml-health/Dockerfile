FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir flask

COPY app.py /app/app.py

EXPOSE 8085

HEALTHCHECK --interval=5s --timeout=3s --start-period=3s --retries=3 \
CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8085/health')" || exit 1

CMD ["python3", "/app/app.py"]