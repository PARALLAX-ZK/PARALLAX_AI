import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env file if present
BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)

# --- Network Configuration ---
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
PARALLAX_CHAIN_URL = os.getenv("PARALLAX_CHAIN_URL", "http://localhost:8545")
INFERENCE_TIMEOUT_SECONDS = int(os.getenv("INFERENCE_TIMEOUT_SECONDS", 15))

# --- Model Defaults ---
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "bert-base-uncased")
MAX_INPUT_TOKENS = int(os.getenv("MAX_INPUT_TOKENS", 512))

# --- Committee Parameters ---
MIN_SIGNATURES_REQUIRED = int(os.getenv("MIN_SIGNATURES_REQUIRED", 3))
DACERT_EXPIRATION_MINUTES = int(os.getenv("DACERT_EXPIRATION_MINUTES", 10))

# --- API Keys and Security ---
DASHBOARD_API_KEY = os.getenv("PARALLAX_DASHBOARD_API_KEY", "demo-key")
ENCRYPTION_KEY_HEX = os.getenv("PARALLAX_AES_KEY", "")  # Must be 32-byte hex

# --- Logging ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# --- Storage and Database ---
DB_URI = os.getenv("DATABASE_URI", "sqlite:///parallax.db")
REDIS_URI = os.getenv("REDIS_URI", "redis://localhost:6379")

# --- Compression ---
COMPRESSION_METHOD = os.getenv("COMPRESSION_METHOD", "gzip-base64")

# --- Deployment ---
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

def print_summary():
    print("[PARALLAX SETTINGS]")
    print(f"Environment: {ENVIRONMENT}")
    print(f"Solana RPC: {SOLANA_RPC_URL}")
    print(f"Chain URL: {PARALLAX_CHAIN_URL}")
    print(f"Model: {DEFAULT_MODEL}")
    print(f"Timeout: {INFERENCE_TIMEOUT_SECONDS}s")
    print(f"Committee quorum: {MIN_SIGNATURES_REQUIRED}")
    print(f"Logging: {LOG_LEVEL}")

# Optional: Print on startup
if __name__ == "__main__":
    print_summary()
