import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from typing import Tuple

class EncryptionUtils:
    def __init__(self, key: bytes = None):
        """
        AES-GCM requires 128, 192, or 256-bit keys (16, 24, or 32 bytes).
        """
        self.key = key or self.generate_key()

    @staticmethod
    def generate_key(length: int = 32) -> bytes:
        """
        Generate a secure random AES key.
        """
        if length not in (16, 24, 32):
            raise ValueError("Key must be 128, 192, or 256 bits.")
        return AESGCM.generate_key(bit_length=length * 8)

    def encrypt(self, plaintext: str, associated_data: str = "") -> str:
        """
        Encrypts plaintext using AES-GCM with optional associated data (AAD).
        Returns base64-encoded ciphertext.
        """
        aesgcm = AESGCM(self.key)
        nonce = os.urandom(12)  # 96-bit nonce
        aad = associated_data.encode()
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), aad)
        return base64.b64encode(nonce + ciphertext).decode("utf-8")

    def decrypt(self, encoded: str, associated_data: str = "") -> str:
        """
        Decrypts base64-encoded AES-GCM ciphertext.
        """
        aesgcm = AESGCM(self.key)
        raw = base64.b64decode(encoded.encode("utf-8"))
        nonce = raw[:12]
        ciphertext = raw[12:]
        aad = associated_data.encode()
        plaintext = aesgcm.decrypt(nonce, ciphertext, aad)
        return plaintext.decode("utf-8")

# Example usage
if __name__ == "__main__":
    key = EncryptionUtils.generate_key()
    crypto = EncryptionUtils(key)

    message = "Inference payload: classify sentiment of the tweet."
    aad = "user_id:abc123"

    encrypted = crypto.encrypt(message, associated_data=aad)
    print("Encrypted:", encrypted)

    decrypted = crypto.decrypt(encrypted, associated_data=aad)
    print("Decrypted:", decrypted)
