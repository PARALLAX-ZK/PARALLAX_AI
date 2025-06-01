import subprocess
import json
import os
import logging
import tempfile
import time
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SNARK_INTERFACE")

ZK_SYSTEM = "zokrates"  # Replace with "halo2", "risc0", etc.
ZK_BINARY_PATH = "/usr/local/bin/zokrates"
PROOF_OUTPUT_PATH = "./zkml/snark_proofs"

os.makedirs(PROOF_OUTPUT_PATH, exist_ok=True)

def prepare_input_file(input_data: Dict[str, Any]) -> str:
    """Creates a temporary file with formatted input data for the ZK circuit."""
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w") as tmp:
        json.dump(input_data, tmp)
    logger.info(f"Prepared temporary input file at {path}")
    return path

def run_zk_compile(circuit_path: str) -> bool:
    """Compiles the ZK circuit using the specified SNARK system."""
    try:
        logger.info("Compiling ZK circuit...")
        result = subprocess.run(
            [ZK_BINARY_PATH, "compile", "-i", circuit_path],
            capture_output=True,
            check=True
        )
        logger.info("ZK circuit compiled successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Compilation failed: {e.stderr.decode()}")
        return False

def run_zk_setup() -> bool:
    """Runs setup phase to generate proving and verifying keys."""
    try:
        result = subprocess.run(
            [ZK_BINARY_PATH, "setup"],
            capture_output=True,
            check=True
        )
        logger.info("ZK setup phase complete")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Setup failed: {e.stderr.decode()}")
        return False

def run_zk_prove(input_file_path: str) -> Dict[str, Any]:
    """Generates a SNARK proof using the external ZK tool."""
    try:
        logger.info("Generating ZK proof...")
        subprocess.run(
            [ZK_BINARY_PATH, "compute-witness", "-i", "out", "-o", "witness", "-a", input_file_path],
            check=True
        )
        subprocess.run(
            [ZK_BINARY_PATH, "generate-proof"],
            check=True
        )

        proof_file = os.path.join(PROOF_OUTPUT_PATH, f"proof_{int(time.time())}.json")
        os.rename("proof.json", proof_file)

        with open(proof_file, "r") as f:
            proof = json.load(f)

        logger.info(f"Proof generated and saved to {proof_file}")
        return proof

    except subprocess.CalledProcessError as e:
        logger.error(f"Proof generation failed: {e.stderr.decode()}")
        return {"error": "proof_generation_failed"}

def verify_zk_proof(proof_file: str) -> bool:
    """Verifies a generated ZK proof using the backend tool."""
    try:
        logger.info(f"Verifying proof at {proof_file}")
        subprocess.run(
            [ZK_BINARY_PATH, "verify"],
            check=True
        )
        logger.info("Proof verified successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Verification failed: {e.stderr.decode()}")
        return False

def simulate_end_to_end(input_data: Dict[str, Any], circuit_file: str):
    """Full pipeline: compile, setup, prove, verify."""
    input_path = prepare_input_file(input_data)

    if not run_zk_compile(circuit_file):
        return None

    if not run_zk_setup():
        return None

    proof = run_zk_prove(input_path)
    valid = verify_zk_proof("proof.json")

    return {
        "proof": proof,
        "valid": valid
    }

if __name__ == "__main__":
    input_sample = {
        "model_output": 0.92,
        "threshold": 0.90
    }
    circuit = "circuits/threshold_check.zok"
    result = simulate_end_to_end(input_sample, circuit)
    print(json.dumps(result, indent=2))
