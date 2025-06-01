import asyncio
import logging
import socket
import uuid
import time
import random
import platform
import aiohttp
from typing import Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NODE_REPORTER")

SEQUENCER_URL = "http://localhost:5050"
NODE_ID = f"node-{uuid.uuid4().hex[:8]}"

# Sample metadata
SUPPORTED_MODELS = ["parallax-llm-v1", "quant-forecast-lite"]
REGION = "us-central"
START_TIME = int(time.time())

# Simulated resource state
class NodeState:
    def __init__(self):
        self.inference_count = 0
        self.errors = 0
        self.cpu_load = 0.0
        self.memory_used_mb = 0.0
        self.model_usage: Dict[str, int] = {model: 0 for model in SUPPORTED_MODELS}

    def update(self):
        self.cpu_load = round(random.uniform(2.0, 40.0), 2)
        self.memory_used_mb = round(random.uniform(200.0, 1600.0), 2)
        self.inference_count += random.randint(0, 3)
        model = random.choice(SUPPORTED_MODELS)
        self.model_usage[model] += 1

state = NodeState()

async def send_status(session: aiohttp.ClientSession):
    state.update()

    payload = {
        "node_id": NODE_ID,
        "hostname": socket.gethostname(),
        "ip_address": socket.gethostbyname(socket.gethostname()),
        "region": REGION,
        "platform": platform.system(),
        "os_version": platform.version(),
        "uptime_sec": int(time.time()) - START_TIME,
        "supported_models": SUPPORTED_MODELS,
        "metrics": {
            "cpu_load": state.cpu_load,
            "memory_mb": state.memory_used_mb,
            "inference_count": state.inference_count,
            "model_usage": state.model_usage
        }
    }

    try:
        async with session.post(f"{SEQUENCER_URL}/node_status/update", json=payload) as resp:
            if resp.status == 200:
                logger.info(f"Status report sent for {NODE_ID}")
            else:
                logger.warning(f"Failed to report status: {resp.status}")
    except Exception as e:
        logger.error(f"Error reporting node status: {e}")

async def reporter_loop(interval: int = 15):
    async with aiohttp.ClientSession() as session:
        while True:
            await send_status(session)
            await asyncio.sleep(interval)

if __name__ == "__main__":
    logger.info(f"Starting node status reporter [{NODE_ID}]")
    asyncio.run(reporter_loop())
