import re
from typing import List, Dict, Optional
import unicodedata
import logging

try:
    from transformers import AutoTokenizer
except ImportError:
    AutoTokenizer = None

logger = logging.getLogger("TOKENIZER_UTILS")

# Global registry of model tokenizers (optional lazy loading)
TOKENIZER_CACHE: Dict[str, any] = {}

def normalize_text(text: str) -> str:
    """
    Clean and normalize text to a canonical form.
    - Lowercase
    - Strip accents
    - Remove extra whitespace
    """
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("utf-8")
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text

def get_tokenizer(model_id: str):
    """
    Loads a tokenizer (Hugging Face or custom) for a given model ID.
    Caches the tokenizer to avoid reloading.
    """
    if model_id in TOKENIZER_CACHE:
        return TOKENIZER_CACHE[model_id]

    if not AutoTokenizer:
        raise ImportError("Transformers not installed. Cannot use Hugging Face tokenizers.")

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        TOKENIZER_CACHE[model_id] = tokenizer
        return tokenizer
    except Exception as e:
        logger.error(f"Failed to load tokenizer for {model_id}: {e}")
        raise RuntimeError("Tokenizer loading failed")

def tokenize_input(model_id: str, input_text: str) -> List[int]:
    """
    Tokenizes a string input for a specific model.
    Returns a list of token IDs.
    """
    tokenizer = get_tokenizer(model_id)
    input_ids = tokenizer.encode(input_text, add_special_tokens=True)
    return input_ids

def decode_tokens(model_id: str, token_ids: List[int]) -> str:
    """
    Converts token IDs back to string output for a specific model.
    """
    tokenizer = get_tokenizer(model_id)
    return tokenizer.decode(token_ids, skip_special_tokens=True)

def count_tokens(model_id: str, input_text: str) -> int:
    """
    Utility to count the number of tokens a model would generate for a given input.
    """
    return len(tokenize_input(model_id, input_text))

# Optional testing
if __name__ == "__main__":
    demo_model = "bert-base-uncased"
    demo_text = "Hello from the PARALLAX network."
    
    try:
        print("Original:", demo_text)
        print("Normalized:", normalize_text(demo_text))
        tokens = tokenize_input(demo_model, demo_text)
        print("Tokens:", tokens)
        print("Decoded:", decode_tokens(demo_model, tokens))
        print("Token count:", count_tokens(demo_model, demo_text))
    except Exception as e:
        print("Tokenizer test failed:", e)
