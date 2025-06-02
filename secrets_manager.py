import os
import logging
from typing import Dict, Optional
from cryptography.fernet import Fernet, InvalidToken

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SECRETS_MANAGER")

# Global secrets store (in-memory)
_secrets: Dict[str, str] = {}

# Environment variable for Fernet key encryption (optional)
FERNET_KEY = os.getenv("PARALLAX_SECRET_KEY")

fernet = Fernet(FERNET_KEY) if FERNET_KEY else None

def load_secret(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    if key in _secrets:
        return _secrets[key]

    value = os.getenv(key, default)

    if value is None and required:
        raise RuntimeError(f"Missing required secret: {key}")

    _secrets[key] = value
    return value

def load_encrypted_secret(key: str, required: bool = False) -> Optional[str]:
    if not fernet:
        raise RuntimeError("Fernet encryption key is not set")

    value = os.getenv(key)
    if not value:
        if required:
            raise RuntimeError(f"Encrypted secret missing: {key}")
        return None

    try:
        decrypted = fernet.decrypt(value.encode()).decode()
        _secrets[key] = decrypted
        return decrypted
    except InvalidToken:
        raise RuntimeError(f"Failed to decrypt secret: {key}")

def get_secret(key: str) -> Optional[str]:
    return _secrets.get(key)

def set_secret(key: str, value: str):
    _secrets[key] = value

def require_secrets(*keys: str):
    for key in keys:
        if get_secret(key) is None:
            raise RuntimeError(f"Missing required secret: {key}")

def print_loaded_secrets():
    logger.info("Loaded secrets:")
    for k in _secrets:
        redacted = "*" * (len(_secrets[k]) - 4) + _secrets[k][-4:]
        logger.info(f"  {k}: {redacted}")

if __name__ == "__main__":
    # Example usage
    os.environ["MODEL_API_KEY"] = "my_example_token_12345"
    os.environ["SIGNING_KEY"] = "abcdef123456"

    load_secret("MODEL_API_KEY", required=True)
    load_secret("SIGNING_KEY", required=True)

    set_secret("EXTRA_SECRET", "some_value")
    print_loaded_secrets()

    if FERNET_KEY:
        print("Encrypted secret support is enabled")
