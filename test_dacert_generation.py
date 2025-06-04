import unittest
import time
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import hashes
from hashlib import sha256

# Mock version of DACert logic (replace with real DACert class in integration)
class MockDACert:
    def __init__(self, data: str, signers: list, quorum: int):
        self.data = data
        self.signatures = signers
        self.timestamp = datetime.utcnow()
        self.quorum = quorum

    def is_valid(self):
        return len(self.signatures) >= self.quorum

    def is_fresh(self, max_age_seconds: int = 60):
        now = datetime.utcnow()
        return (now - self.timestamp).total_seconds() <= max_age_seconds

    def hash(self):
        return sha256(self.data.encode()).hexdigest()

class TestDACertGeneration(unittest.TestCase):
    def setUp(self):
        self.payload = "model_output:sentiment=positive"
        self.signers = ["nodeA", "nodeB", "nodeC"]
        self.quorum = 2
        self.dacert = MockDACert(self.payload, self.signers, self.quorum)

    def test_signature_quorum_met(self):
        self.assertTrue(self.dacert.is_valid(), "DACert should be valid with quorum signatures")

    def test_signature_quorum_failed(self):
        weak_cert = MockDACert(self.payload, ["nodeA"], quorum=3)
        self.assertFalse(weak_cert.is_valid(), "DACert should be invalid if quorum not met")

    def test_hash_consistency(self):
        h1 = self.dacert.hash()
        h2 = sha256(self.payload.encode()).hexdigest()
        self.assertEqual(h1, h2, "Hashes should match SHA256 of payload")

    def test_freshness_true(self):
        self.assertTrue(self.dacert.is_fresh(60), "DACert should be fresh")

    def test_freshness_expired(self):
        expired_cert = MockDACert(self.payload, self.signers, self.quorum)
        expired_cert.timestamp = datetime.utcnow() - timedelta(seconds=120)
        self.assertFalse(expired_cert.is_fresh(60), "Expired DACert should not be fresh")

    def test_dacert_integrity(self):
        original = self.dacert.hash()
        tampered = MockDACert("model_output:sentiment=negative", self.signers, self.quorum)
        self.assertNotEqual(original, tampered.hash(), "Tampered payload must not match original hash")

if __name__ == "__main__":
    unittest.main()
