# scripts/download_bert_model.py
from transformers import pipeline

def download_model():
    """
    Downloads the DistilBERT model to a local cache directory
    for offline use in the sentiment analysis pipeline.
    """
    print("Downloading DistilBERT model...")
    pipeline(
        'sentiment-analysis',
        model='distilbert-base-uncased-finetuned-sst-2-english',
        cache_dir='./ml_models'
    )
    print("Model downloaded to ml_models/")

if __name__ == '__main__':
    download_model()
