import os
import json
import time
import logging
from threading import Thread
from queue import Queue
from typing import Dict, Any

import tweepy

# Configure logging
logger = logging.getLogger("STREAM_COLLECTOR")
logging.basicConfig(level=logging.INFO)

# Global queue for live tweets
tweet_queue: Queue[Dict[str, Any]] = Queue()

# Load Twitter API keys from environment
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "your-api-key")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "your-api-secret")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "your-access-token")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET", "your-access-secret")

TRACK_TERMS = ["Solana", "Bitcoin", "crypto", "AI", "zkML", "DeFi", "trading", "onchain"]

class CryptoStreamListener(tweepy.StreamingClient):
    def __init__(self, bearer_token: str):
        super().__init__(bearer_token)
        self.counter = 0

    def on_tweet(self, tweet):
        if tweet.referenced_tweets:
            return  # Skip replies and retweets

        clean_tweet = {
            "id": tweet.id,
            "text": tweet.text,
            "author_id": tweet.author_id,
            "created_at": str(tweet.created_at),
            "lang": tweet.lang
        }

        tweet_queue.put(clean_tweet)
        self.counter += 1
        logger.info(f" Tweet #{self.counter} captured")

    def on_errors(self, errors):
        logger.error(f"Stream error: {errors}")

    def on_connection_error(self):
        logger.warning("Lost connection. Reconnecting...")
        self.disconnect()

def start_streaming():
    logger.info(" Starting Twitter streaming client...")

    bearer_token = os.getenv("TWITTER_BEARER_TOKEN", "your-bearer-token")
    stream = CryptoStreamListener(bearer_token)

    # Remove existing rules
    rules = stream.get_rules().data
    if rules:
        rule_ids = [rule.id for rule in rules]
        stream.delete_rules(rule_ids)

    stream.add_rules(tweepy.StreamRule(" OR ".join(TRACK_TERMS)))
    stream.filter(tweet_fields=["author_id", "created_at", "lang"], threaded=True)

def tweet_consumer_loop():
    """Consumes tweets from queue for processing or model inference."""
    logger.info(" Tweet consumer started")
    while True:
        if not tweet_queue.empty():
            tweet = tweet_queue.get()
            process_tweet(tweet)
        else:
            time.sleep(1)

def process_tweet(tweet: Dict[str, Any]):
    """Placeholder: Store tweet, or forward to sentiment model"""
    logger.info(f"[{tweet['lang']}] {tweet['text'][:80]}...")
    # Extend this to forward tweet text to model or DB

if __name__ == "__main__":
    stream_thread = Thread(target=start_streaming, daemon=True)
    consumer_thread = Thread(target=tweet_consumer_loop, daemon=True)

    stream_thread.start()
    consumer_thread.start()

    logger.info(" Running indefinitely. Ctrl+C to stop.")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info(" Shutting down...")
