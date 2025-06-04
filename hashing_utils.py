import hashlib
import logging
from typing import Union

logger = logging.getLogger("HASHING_UTILS")

def hash_sha256(data: Union[str, bytes]) -> str:
    """
    Generates SHA-256 hash of input data.
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    digest = hashlib.sha256(data).hexdigest()
    logger.debug(f"SHA-256 hash generated: {digest}")
    return digest

def hash_blake2b(data: Union[str, bytes], digest_size: int = 32) -> str:
    """
    Generates BLAKE2b hash of input data.
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    digest = hashlib.blake2b(data, digest_size=digest_size).hexdigest()
    logger.debug(f"BLAKE2b hash generated: {digest}")
    return digest

def hash_sha3_512(data: Union[str, bytes]) -> str:
    """
    Generates SHA-3 (512-bit) hash of input data.
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    digest = hashlib.sha3_512(data).hexdigest()
    logger.debug(f"SHA3-512 hash generated: {digest}")
    return digest

def verify_hash(data: Union[str, bytes], expected_hash: str, algo: str = "sha256") -> bool:
    """
    Verifies a hash against expected value using specified algorithm.
    """
    algo_map = {
        "sha256": hash_sha256,
        "blake2b": hash_blake2b,
        "sha3_512": hash_sha3_512
    }
    if algo not in algo_map:
        raise ValueError(f"Unsupported hash algorithm: {algo}")
    result = algo_map[algo](data)
    match = result == expected_hash
    logger.info(f"Hash match: {match}")
    return match

# Example usage
if __name__ == "__main__":
    test_data = "Parallax AI inference payload"
    print("Original Data:", test_data)

    h1 = hash_sha256(test_data)
    h2 = hash_blake2b(test_data)
    h3 = hash_sha3_512(test_data)

    print("SHA-256:", h1)
    print("BLAKE2b:", h2)
    print("SHA3-512:", h3)

    print("Verify SHA-256:", verify_hash(test_data, h1, "sha256"))
    print("Verify BLAKE2b:", verify_hash(test_data, h2, "blake2b"))
    print("Verify SHA3:", verify_hash(test_data, h3, "sha3_512"))
