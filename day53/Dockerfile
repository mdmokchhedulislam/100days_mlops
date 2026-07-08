FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cpu \
    torch

CMD ["python3", "-c", "import torch; print(torch.__version__, 'cuda?', torch.cuda.is_available())"]