import logging
import re
import time
from typing import List, Dict, Any
from transformers import pipeline, Pipeline
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SENTIMENT_MODEL")

# Load the model once
MODEL_ID = "cardiffnlp/twitter-roberta-base-sentiment"
sentiment_pipeline: Pipeline = pipeline("sentiment-analysis", model=MODEL_ID)

# Optionally define class mapping if model uses numeric labels
LABEL_MAPPING = {
    "LABEL_0": "Negative",
    "LABEL_1": "Neutral",
    "LABEL_2": "Positive"
}

def clean_text(text: str) -> str:
    """Clean tweet text by removing mentions, URLs, and extra spaces."""
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def analyze_sentiment(texts: List[str]) -> List[Dict[str, Any]]:
    """Runs sentiment analysis on a list of texts."""
    cleaned = [clean_text(t) for t in texts]
    results = sentiment_pipeline(cleaned)

    output = []
    timestamp = int(time.time())
    for original, result in zip(texts, results):
        label = LABEL_MAPPING.get(result["label"], result["label"])
        entry = {
            "text": original,
            "cleaned_text": clean_text(original),
            "sentiment": label,
            "confidence": round(result["score"], 4),
            "timestamp": timestamp
        }
        output.append(entry)
    return output

def process_tweet_batch(tweets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Processes a batch of tweet dictionaries and returns annotated sentiment entries."""
    texts = [tweet["text"] for tweet in tweets]
    results = analyze_sentiment(texts)
    enriched = []

    for tweet, result in zip(tweets, results):
        merged = {
            "id": tweet.get("id"),
            "author_id": tweet.get("author_id"),
            "created_at": tweet.get("created_at"),
            "lang": tweet.get("lang"),
            **result
        }
        enriched.append(merged)

    return enriched

def process_streamed_tweet(tweet: Dict[str, Any]) -> Dict[str, Any]:
    """Processes a single tweet dictionary for real-time use cases."""
    result = analyze_sentiment([tweet["text"]])[0]
    return {
        "id": tweet.get("id"),
        "author_id": tweet.get("author_id"),
        "created_at": tweet.get("created_at"),
        "lang": tweet.get("lang"),
        **result
    }

def batch_worker(tweet_batches: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """Runs batches of tweet groups in parallel."""
    results = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(process_tweet_batch, batch) for batch in tweet_batches]
        for future in futures:
            try:
                results.extend(future.result())
            except Exception as e:
                logger.warning(f"Error in sentiment batch: {e}")
    return results

if __name__ == "__main__":
    # Test input
    test_tweets = [
        {"text": "Solana is the future of finance!", "id": 1, "author_id": "user1", "created_at": "2025-05-27", "lang": "en"},
        {"text": "The crypto market is collapsing again. Bad news.", "id": 2, "author_id": "user2", "created_at": "2025-05-27", "lang": "en"},
        {"text": "Not sure what's going on with zkML models lately.", "id": 3, "author_id": "user3", "created_at": "2025-05-27", "lang": "en"}
    ]

    batch = [test_tweets]
    sentiment_results = batch_worker(batch)

    for item in sentiment_results:
        print(item)
