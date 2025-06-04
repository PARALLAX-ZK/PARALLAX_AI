import unittest
from typing import Dict

# Mocked interface (replace with actual sentiment model wrapper in integration)
class MockSentimentModel:
    def __init__(self, max_tokens=512):
        self.max_tokens = max_tokens

    def classify(self, text: str) -> Dict[str, str]:
        if not text.strip():
            raise ValueError("Input text is empty.")
        if len(text.split()) > self.max_tokens:
            raise ValueError("Token limit exceeded.")
        if "good" in text.lower():
            return {"sentiment": "positive", "confidence": "0.91"}
        elif "bad" in text.lower():
            return {"sentiment": "negative", "confidence": "0.88"}
        else:
            return {"sentiment": "neutral", "confidence": "0.70"}

class TestSentimentModel(unittest.TestCase):
    def setUp(self):
        self.model = MockSentimentModel()

    def test_positive_sentiment(self):
        result = self.model.classify("This project is really good.")
        self.assertEqual(result["sentiment"], "positive")
        self.assertGreater(float(result["confidence"]), 0.8)

    def test_negative_sentiment(self):
        result = self.model.classify("This update was bad.")
        self.assertEqual(result["sentiment"], "negative")

    def test_neutral_sentiment(self):
        result = self.model.classify("The agent returned a result.")
        self.assertEqual(result["sentiment"], "neutral")

    def test_empty_input(self):
        with self.assertRaises(ValueError):
            self.model.classify("")

    def test_token_limit_exceeded(self):
        long_text = "token " * 600
        with self.assertRaises(ValueError):
            self.model.classify(long_text)

    def test_confidence_range(self):
        result = self.model.classify("Just okay.")
        confidence = float(result["confidence"])
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

    def test_output_structure(self):
        result = self.model.classify("Uncertain outcome.")
        self.assertIn("sentiment", result)
        self.assertIn("confidence", result)
        self.assertIsInstance(result["sentiment"], str)
        self.assertIsInstance(result["confidence"], str)

if __name__ == "__main__":
    unittest.main()
