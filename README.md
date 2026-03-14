# NewSense AI

An AI-powered newspaper sentiment analysis agent that accepts PDF, PNG, and JPG newspaper documents, extracts their text using OCR, and determines the emotional tone (GOOD / BAD / NEUTRAL) via a dual-model sentiment analysis pipeline.

## Stack
* Backend: Python 3.11 + FastAPI + Celery
* Frontend: React 18 + Vite + Tailwind CSS + Zustand
* Database: PostgreSQL 16 via SQLAlchemy 2.0 async
* Queue/Cache: Redis 7
* Storage: MinIO (local dev) / S3 (prod)
* AI/Local: Tesseract OCR + VADER + DistilBERT

## Running the app
1. `make dev`
2. Backend is running at `http://localhost:8000` Let's test the health check via `http://localhost:8000/api/v1/health`
3. Frontend running at `http://localhost:3000`
