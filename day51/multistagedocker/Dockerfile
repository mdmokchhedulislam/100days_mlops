
    # builder stage
    FROM python:3.11-slim AS builder

    WORKDIR /app
    
    RUN pip install --no-cache-dir \
        scikit-learn \
        pandas \
        numpy \
        joblib
    
    COPY train_model.py .
    
    RUN python3 train_model.py
    

    # runtime stage
    FROM python:3.11-slim
    
    WORKDIR /app
    
    RUN pip install --no-cache-dir \
        flask \
        joblib \
        numpy \
        scikit-learn
    
    COPY serve.py .
    
    COPY --from=builder /app/model.pkl .
    
    EXPOSE 8080
    
    CMD ["python3", "serve.py"]