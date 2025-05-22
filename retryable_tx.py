import aiohttp
import asyncio
import logging
import json
from typing import Dict

logger = logging.getLogger("RETRYABLE_TX")
logging.basicConfig(level=logging.INFO)

MAX_RETRIES = 5
INITIAL_DELAY = 2  # seconds
RETRY_ENDPOINT = "/submit_result"

async def submit_result_retryable(session: aiohttp.ClientSession, task_id: str, result: Dict, dacert: Dict) -> bool:
    """
    Submits an inference result and DACert to the sequencer with retry logic.
    """
    attempt = 0
    delay = INITIAL_DELAY
    endpoint = f"http://localhost:5050{RETRY_ENDPOINT}"

    payload = {
        "task_id": task_id,
        "result": result,
        "dacert": dacert
    }

    while attempt < MAX_RETRIES:
        try:
            async with session.post(endpoint, json=payload) as resp:
                if resp.status == 200:
                    logger.info(f" Result successfully submitted on attempt {attempt + 1}")
                    return True
                else:
                    error = await resp.text()
                    logger.warning(f"Attempt {attempt + 1} failed: {resp.status} - {error}")

        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} raised exception: {e}")

        attempt += 1
        logger.info(f" Retrying in {delay}s...")
        await asyncio.sleep(delay)
        delay *= 2  # Exponential backoff

    logger.error(f" Failed to submit result after {MAX_RETRIES} attempts")
    return False


async def simulate_submission():
    """Test function for standalone execution"""
    test_task_id = "task-567"
    test_result = {
        "model_id": "parallax-llm-v1",
        "input": "What is PARALLAX?",
        "output": {"label": "POSITIVE", "score": 0.92},
        "latency": 0.45
    }

    test_dacert = {
        "cert_payload": {
            "node_id": "node-999",
            "task_id": "task-567",
            "model_id": "parallax-llm-v1",
            "output_hash": "fakehash123",
            "timestamp": 1716345678
        },
        "signature": "deadbeef...",
        "public_key": "abc123..."
    }

    async with aiohttp.ClientSession() as session:
        await submit_result_retryable(session, test_task_id, test_result, test_dacert)


if __name__ == "__main__":
    asyncio.run(simulate_submission())
