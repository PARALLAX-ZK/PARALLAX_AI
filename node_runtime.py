import asyncio
import logging
import uuid
import json
from typing import Dict, Any

from inference_executor import run_inference
from dacert_generator import generate_dacert
from registration_client import register_node
from retryable_tx import submit_result_retryable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PARALLAX_NODE")

# Unique identifier for the node
NODE_ID = str(uuid.uuid4())

# Mock Sequencer URL
SEQUENCER_URL = "http://localhost:5050"

# Polling interval in seconds
POLL_INTERVAL = 5

# Sample local cache of registered capabilities
REGISTERED_MODELS = ["parallax-llm-v1", "vision-encoder-v2", "quant-forecast-lite"]


async def fetch_task(session) -> Dict[str, Any] | None:
    """Poll the sequencer for an inference task."""
    try:
        async with session.get(f"{SEQUENCER_URL}/get_task?node_id={NODE_ID}") as response:
            if response.status == 200:
                task = await response.json()
                logger.info(f"Fetched task: {task}")
                return task
    except Exception as e:
        logger.warning(f"Failed to fetch task: {e}")
    return None


async def main():
    """Main loop for node execution lifecycle."""
    logger.info(f" Booting PARALLAX AI Node ID: {NODE_ID}")

    # Load capabilities (models) and register
    registration_payload = {
        "node_id": NODE_ID,
        "capabilities": REGISTERED_MODELS,
        "public_key": "dummy_pubkey_123"
    }

    logger.info(" Registering node with sequencer...")
    async with register_node(SEQUENCER_URL, registration_payload) as success:
        if not success:
            logger.error(" Registration failed. Exiting.")
            return

    logger.info(" Registration successful. Entering task loop...")

    async with aiohttp.ClientSession() as session:
        while True:
            task = await fetch_task(session)

            if not task:
                logger.info("No task. Waiting...")
                await asyncio.sleep(POLL_INTERVAL)
                continue

            try:
                logger.info(f" Executing task {task['task_id']}...")
                result = run_inference(task["model"], task["input"])
                dacert = generate_dacert(NODE_ID, task["task_id"], result)

                logger.info(f" Submitting result with DACert...")
                success = await submit_result_retryable(session, task["task_id"], result, dacert)

                if success:
                    logger.info(f" Successfully submitted result for task {task['task_id']}")
                else:
                    logger.warning(f" Submission failed for task {task['task_id']}")

            except Exception as e:
                logger.error(f"Unhandled exception: {e}")

            await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    import aiohttp
    asyncio.run(main())
