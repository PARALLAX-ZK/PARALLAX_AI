import json
import logging
import time
import hashlib
from typing import Dict, Any

from nacl.signing import SigningKey, VerifyKey
from nacl.encoding import HexEncoder
from nacl.exceptions import BadSignatureError

logger = logging.getLogger("DACERT")
logging.basicConfig(level=logging.INFO)

# Generate or load private key for this node (for mock signing)
PRIVATE_KEY = SigningKey.generate()
PUBLIC_KEY = PRIVATE_KEY.verify_key.encode(encoder=HexEncoder).decode()

def hash_payload(data: dict) -> str:
    """Hash a dictionary to generate a fingerprint for the DACert."""
    serialized = json.dumps(data, sort_keys=True).encode()
    return hashlib.sha256(serialized).hexdigest()

def generate_dacert(node_id: str, task_id: str, result: dict) -> dict:
    """
    Generate a DACert for an inference result.
    This certificate will include the result hash, node metadata, and a signature.
    """
    timestamp = int(time.time())

    cert_payload = {
        "node_id": node_id,
        "task_id": task_id,
        "model_id": result["model_id"],
        "output_hash": hash_payload(result),
        "timestamp": timestamp,
    }

    message = json.dumps(cert_payload, sort_keys=True).encode()
    signature = PRIVATE_KEY.sign(message).signature.hex()

    dacert = {
        "cert_payload": cert_payload,
        "signature": signature,
        "public_key": PUBLIC_KEY
    }

    logger.info(f" DACert generated for task {task_id}")
    return dacert

def verify_dacert(dacert: dict) -> bool:
    """Verify the DACert signature using the included public key."""
    try:
        verify_key = VerifyKey(dacert["public_key"], encoder=HexEncoder)
        message = json.dumps(dacert["cert_payload"], sort_keys=True).encode()
        verify_key.verify(message, bytes.fromhex(dacert["signature"]))
        logger.info(" DACert verified successfully")
        return True
    except BadSignatureError:
        logger.warning(" DACert verification failed")
        return False
    except Exception as e:
        logger.error(f"Unexpected verification error: {e}")
        return False

if __name__ == "__main__":
    # Test run
    test_result = {
        "model_id": "parallax-llm-v1",
        "input": "Test string",
        "output": {"label": "POSITIVE", "score": 0.98},
        "latency": 0.51
    }

    cert = generate_dacert("node-001", "task-123", test_result)
    print(json.dumps(cert, indent=2))

    is_valid = verify_dacert(cert)
    print(f"Verification result: {is_valid}")
