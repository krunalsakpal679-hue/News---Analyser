# backend/app/agents/bert/model_loader.py
import os
import logging
import torch
import builtins
from transformers import pipeline as hf_pipeline
from app.config import settings

# CRITICAL: transformers v4.38-4.40 on Windows (some environments) 
# sometimes fails to see 'torch' from its global scope in various pipelines.
# Monkey-patching builtins ensures torch is always visible to pipeline initialization.
if not hasattr(builtins, "torch"):
    setattr(builtins, "torch", torch)

logger = logging.getLogger(__name__)

class BERTModelLoader:
    _model = None

    @classmethod
    def get_model(cls):
        """Loads and returns the BERT sentiment analysis pipeline as a singleton."""
        if cls._model is None:
            # Stage 1: Check for mocks in development
            if settings.ENVIRONMENT == "development" and not cls.is_model_cached():
                logger.warning("BERT model not found locally (~250MB). Using MOCK BERT for rapid development.")
                def mock_classifier(text, **kwargs):
                    return [{'label': 'POSITIVE', 'score': 0.88}]
                cls._model = mock_classifier
                return cls._model

            # Stage 2: Initialize real transformer pipeline
            logger.info("Initializing BERT pipeline (this may download if not cached)...")
            # CPU only: device=-1
            cls._model = hf_pipeline(
                'sentiment-analysis',
                model='distilbert-base-uncased-finetuned-sst-2-english',
                cache_dir=settings.HF_MODEL_DIR,
                device=-1,
                truncation=True,
                max_length=512
            )
            logger.info("BERT pipeline initialized successfully.")
        return cls._model

    @classmethod
    def is_model_cached(cls) -> bool:
        """
        Checks if the model files exist in the cache directory.
        """
        if not os.path.exists(settings.HF_MODEL_DIR):
            return False
            
        for root, dirs, files in os.walk(settings.HF_MODEL_DIR):
            for file in files:
                if file in ['pytorch_model.bin', 'model.safetensors', 'tf_model.h5']:
                    return True
        return False
