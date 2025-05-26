import time
import json
import logging
import random
import hashlib
from typing import List, Dict, Any
from nacl.signing import SigningKey, VerifyKey
from nacl.encoding import HexEncoder
from nacl.exceptions import BadSignatureError

logger = logging.getLogger("COMMITTEE")
logging.basicConfig(level=logging.INFO)

# Simulated validator committee of public/private key pairs
COMMITTEE_SIZE = 5
QUORUM_THRESHOLD = 3  # M of N signatures required

class CommitteeMember:
    def __init__(self):
        self.sk = SigningKey.generate()
        self.pk = self.sk.verify_key.encode(encoder=HexEncoder).decode()

    def sign(self, message: bytes) -> str:
        return self.sk.sign(message).signature.hex()

    def get_public_key(self) -> str:
        return self.pk

# Initialize a static committee
COMMITTEE: List[CommitteeMember] = [CommitteeMember() for _ in range(COMMITTEE_SIZE)]

def hash_result(result: Dict[str, Any]) -> str:
    serialized = json.dumps(result, sort_keys=True).encode()
    return hashlib.sha256(serialized).hexdigest()

def sign_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Committee signs an inference result and aggregates signatures if quorum is met."""
    payload = {
        "task_id": result["task_id"],
        "model_id": result["model_id"],
        "output_hash": hash_result(result["output"]),
        "timestamp": int(time.time())
    }

    message = json.dumps(payload, sort_keys=True).encode()

    selected_members = random.sample(COMMITTEE, QUORUM_THRESHOLD)
    signatures = [member.sign(message) for member in selected_members]
    public_keys = [member.get_public_key() for member in selected_members]

    logger.info(f" Collected {len(signatures)}/{COMMITTEE_SIZE} signatures")

    dacert = {
        "cert_payload": payload,
        "signatures": signatures,
        "signers": public_keys,
        "quorum": QUORUM_THRESHOLD
    }

    return dacert

def verify_committee_dacert(dacert: Dict[str, Any]) -> bool:
    """Verifies each signature in the DACert payload"""
    try:
        message = json.dumps(dacert["cert_payload"], sort_keys=True).encode()
        for sig, pubkey in zip(dacert["signatures"], dacert["signers"]):
            verify_key = VerifyKey(pubkey, encoder=HexEncoder)
            verify_key.verify(message, bytes.fromhex(sig))
        logger.info(" Committee DACert verified successfully")
        return True
    except BadSignatureError:
        logger.error(" One or more signatures are invalid")
        return False
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return False

if __name__ == "__main__":
    # Simulated result from a node
    inference_result = {
        "task_id": "task-abcdef",
        "model_id": "parallax-llm-v1",
        "input": "What is zkML?",
        "output": {
            "label": "INNOVATIVE",
            "score": 0.93
        },
        "latency": 0.42
    }

    dacert = sign_result(inference_result)
    print(json.dumps(dacert, indent=2))
    print(f"Verification passed: {verify_committee_dacert(dacert)}")
