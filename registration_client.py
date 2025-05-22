import aiohttp
import logging
from typing import Dict

logger = logging.getLogger("REGISTRATION")

async def register_node(sequencer_url: str, payload: Dict) -> bool:
    """
    Register a node with the sequencer.
    The payload should include:
      - node_id
      - capabilities (list of supported models)
      - public_key (for verifying DACerts)
    """
    endpoint = f"{sequencer_url}/register_node"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, json=payload) as resp:
                if resp.status == 200:
                    response = await resp.json()
                    logger.info(f" Node registered successfully: {response}")
                    return True
                else:
                    error = await resp.text()
                    logger.error(f" Registration failed: {resp.status} - {error}")
                    return False
    except Exception as e:
        logger.error(f"Exception during node registration: {e}")
        return False

async def check_node_status(sequencer_url: str, node_id: str) -> Dict:
    """Check the node's status from the sequencer."""
    endpoint = f"{sequencer_url}/node_status/{node_id}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint) as resp:
                if resp.status == 200:
                    response = await resp.json()
                    logger.info(f" Node status: {response}")
                    return response
                else:
                    error = await resp.text()
                    logger.warning(f"Could not fetch node status: {resp.status} - {error}")
                    return {}
    except Exception as e:
        logger.error(f"Error checking status: {e}")
        return {}

if __name__ == "__main__":
    import asyncio

    async def test():
        test_payload = {
            "node_id": "test-node-xyz",
            "capabilities": ["parallax-llm-v1", "quant-forecast-lite"],
            "public_key": "abc123publickey"
        }

        test_url = "http://localhost:5050"
        registered = await register_node(test_url, test_payload)

        if registered:
            status = await check_node_status(test_url, test_payload["node_id"])
            print(status)
        else:
            print(" Could not register node")

    asyncio.run(test())
