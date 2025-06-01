import hashlib
import json
import logging
import time
import os
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ZK_PROVER")

PROOF_OUTPUT_DIR = "./zkml/proofs"
os.makedirs(PROOF_OUTPUT_DIR, exist_ok=True)

# Constants used for hashing
HASH_ALGO = "sha256"
PROOF_VERSION = "v0.1-simulated"

def hash_payload(payload: Dict[str, Any]) -> str:
    """Hashes the input/output payload to create a fingerprint."""
    serialized = json.dumps(payload, sort_keys=True).encode()
    return hashlib.new(HASH_ALGO, serialized).hexdigest()

def generate_simulated_proof(task_id: str, model_id: str, input_text: str, output: Any) -> Dict[str, Any]:
    """
    Simulates zkML proof generation for an inference result.
    In real-world scenarios, this would interface with ZK proof engines.
    """
    timestamp = int(time.time())
    input_hash = hash_payload({"task_id": task_id, "model_id": model_id, "input": input_text})
    output_hash = hash_payload({"output": output})
    combined_hash = hash_payload({"input": input_hash, "output": output_hash})

    logger.info(f"Generating proof for task {task_id}")

    proof = {
        "task_id": task_id,
        "model_id": model_id,
        "input_hash": input_hash,
        "output_hash": output_hash,
        "combined_hash": combined_hash,
        "timestamp": timestamp,
        "version": PROOF_VERSION,
        "proof_data": f"zk-proof-sim-{combined_hash[:16]}"
    }

    output_path = os.path.join(PROOF_OUTPUT_DIR, f"{task_id}_proof.json")
    with open(output_path, "w") as f:
        json.dump(proof, f, indent=2)

    logger.info(f"Proof stored at {output_path}")
    return proof

def verify_simulated_proof(proof: Dict[str, Any], input_text: str, output: Any) -> bool:
    """
    Simulates verification of a zkML proof by recomputing hashes and comparing.
    """
    input_hash_check = hash_payload({"task_id": proof["task_id"], "model_id": proof["model_id"], "input": input_text})
    output_hash_check = hash_payload({"output": output})
    combined_check = hash_payload({"input": input_hash_check, "output": output_hash_check})

    return (
        input_hash_check == proof["input_hash"]
        and output_hash_check == proof["output_hash"]
        and combined_check == proof["combined_hash"]
    )

def simulate_demo():
    task_id = "task-007"
    model_id = "parallax-llm-v1"
    input_text = "What is the future of AI in finance?"
    output = {"sentiment": "Positive", "confidence": 0.91}

    proof = generate_simulated_proof(task_id, model_id, input_text, output)

    is_valid = verify_simulated_proof(proof, input_text, output)
    logger.info(f"Proof verification result: {is_valid}")

    return is_valid

if __name__ == "__main__":
    result = simulate_demo()
    print(f"Demo verification passed: {result}")
