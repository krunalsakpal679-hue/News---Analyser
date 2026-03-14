FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    libmagic1 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    poppler-utils \
    wget \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for Docker layer caching
COPY requirements.txt .

# Install CPU-only PyTorch FIRST (before other packages)
# This avoids downloading the 2GB GPU version
RUN pip install --no-cache-dir \
    torch==2.2.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# Install all other requirements
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy English model
RUN python -m spacy download en_core_web_sm

# Pre-download DistilBERT model during build
# This prevents 30-second cold start on first request
RUN python -c "\
from transformers import AutoTokenizer, AutoModelForSequenceClassification; \
model_name = 'distilbert-base-uncased-finetuned-sst-2-english'; \
AutoTokenizer.from_pretrained(model_name); \
AutoModelForSequenceClassification.from_pretrained(model_name); \
print('DistilBERT model downloaded successfully')"

# Copy application code
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Expose port (Railway sets $PORT dynamically)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=15s --start-period=90s \
    CMD curl -f http://localhost:${PORT:-8000}/api/v1/health || exit 1

# Start command — Railway injects $PORT automatically
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
