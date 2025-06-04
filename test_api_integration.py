import unittest
from fastapi.testclient import TestClient
from fastapi import FastAPI, Depends, HTTPException
from typing import Dict

# Simulated secure dependency
def fake_auth():
    def dependency():
        token = "test-token"
        if token != "test-token":
            raise HTTPException(status_code=403, detail="Forbidden")
    return Depends(dependency)

# Minimal example API (simulate real API logic here)
app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/inference", dependencies=[fake_auth()])
def run_inference(payload: Dict[str, str]):
    text = payload.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="Missing text")
    return {"output": "positive", "confidence": 0.92}

@app.get("/config")
def get_config():
    return {"model": "bert-base-uncased", "token_limit": 512}

# Attach test client
client = TestClient(app)

class TestAPIIntegration(unittest.TestCase):
    def test_health_endpoint(self):
        res = client.get("/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"status": "ok"})

    def test_inference_success(self):
        res = client.post("/inference", json={"text": "this is great"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("output", data)
        self.assertIn("confidence", data)
        self.assertEqual(data["output"], "positive")

    def test_inference_missing_text(self):
        res = client.post("/inference", json={})
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["detail"], "Missing text")

    def test_config_response(self):
        res = client.get("/config")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["model"], "bert-base-uncased")
        self.assertEqual(data["token_limit"], 512)

    def test_invalid_route(self):
        res = client.get("/invalid")
        self.assertEqual(res.status_code, 404)

if __name__ == "__main__":
    unittest.main()
