import json
import hashlib
import os
import logging
from typing import Dict, List
from nacl.signing import SigningKey, VerifyKey
from nacl.encoding import HexEncoder
from nacl.exceptions import BadSignatureError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SIGNATURE_UTILS")

DEFAULT_PRIVATE_KEY_PATH = "./keys/node_signing_key.hex"

def hash_dict(data: Dict) -> str:
    """Hash a dictionary deterministically using SHA256."""
    serialized = json.dumps(data, sort_keys=True).encode()
    return hashlib.sha256(serialized).hexdigest()

def generate_key_pair() -> (str, str):
    """Generates a new Ed25519 key pair and returns hex-encoded values."""
    sk = SigningKey.generate()
    pk = sk.verify_key.encode(encoder=HexEncoder).decode()
    sk_hex = sk.encode(encoder=HexEncoder).decode()
    return sk_hex, pk

def save_private_key(sk_hex: str, path: str = DEFAULT_PRIVATE_KEY_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(sk_hex)
    logger.info(f"Private key saved to {path}")

def load_private_key(path: str = DEFAULT_PRIVATE_KEY_PATH) -> SigningKey:
    if not os.path.exists(path):
        raise FileNotFoundError("Private key not found")
    with open(path, "r") as f:
        sk_hex = f.read().strip()
    return SigningKey(sk_hex, encoder=HexEncoder)

def sign_payload(payload: Dict, sk: SigningKey) -> str:
    message = json.dumps(payload, sort_keys=True).encode()
    signature = sk.sign(message).signature
    return signature.hex()

def verify_signature(payload: Dict, signature: str, public_key_hex: str) -> bool:
    try:
        message = json.dumps(payload, sort_keys=True).encode()
        vk = VerifyKey(public_key_hex, encoder=HexEncoder)
        vk.verify(message, bytes.fromhex(signature))
        return True
    except BadSignatureError:
        logger.warning("Signature verification failed")
        return False
    except Exception as e:
        logger.error(f"Verification error: {e}")
        return False

def verify_batch_signatures(
    payload: Dict,
    signatures: List[str],
    public_keys: List[str]
) -> int:
    """Returns the number of valid signatures over the same payload."""
    valid_count = 0
    for sig, pk in zip(signatures, public_keys):
        if verify_signature(payload, sig, pk):
            valid_count += 1
    return valid_count

if __name__ == "__main__":
    # Demo of signing/verification flow
    sk_hex, pk_hex = generate_key_pair()
    save_private_key(sk_hex)

    sk = load_private_key()
    payload = {
        "task_id": "abc123",
        "model_id": "parallax-llm-v1",
        "output_hash": "9f23fa0bc4",
        "timestamp": 1716340000
    }

    sig = sign_payload(payload, sk)
    print(f"Signature: {sig}")

    valid = verify_signature(payload, sig, pk_hex)
    print(f"Verification result: {valid}")

    # Simulate batch verification
    signatures = [sig, sig, "bad123"]
    public_keys = [pk_hex, pk_hex, pk_hex]
    count = verify_batch_signatures(payload, signatures, public_keys)
    print(f"Valid signatures in batch: {count}")
