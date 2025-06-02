import asyncio
import logging
import time
from typing import Dict, Any, List

from solana.rpc.async_api import AsyncClient
from solana.publickey import PublicKey

from solana_parser import extract_events_from_log_block, ParsedEvent
from task_scheduler import submit_task

logger = logging.getLogger("EVENT_LISTENER")

# Configure this with the deployed Solana program ID for PARALLAX
PARALLAX_PROGRAM_ID = PublicKey("Parallx1111111111111111111111111111111111")
RPC_URL = "https://api.mainnet-beta.solana.com"

POLL_INTERVAL = 5
LOOKBACK_SLOTS = 50

async def fetch_recent_logs(client: AsyncClient, start_slot: int, end_slot: int) -> List[Dict[str, Any]]:
    logs = []
    for slot in range(start_slot, end_slot + 1):
        try:
            res = await client.get_logs_for_slot(slot)
            if "result" in res and res["result"]:
                logs.append({
                    "slot": slot,
                    "logs": res["result"]["logs"]
                })
        except Exception as e:
            logger.warning(f"Failed to get logs for slot {slot}: {e}")
    return logs

async def listen_for_triggers():
    client = AsyncClient(RPC_URL)
    last_slot = await client.get_slot()
    last_slot = last_slot.value if hasattr(last_slot, "value") else last_slot.get("result", 0)

    logger.info(f"Starting from slot {last_slot - LOOKBACK_SLOTS}")
    current_slot = last_slot - LOOKBACK_SLOTS

    while True:
        try:
            latest_slot = await client.get_slot()
            latest_slot = latest_slot.value if hasattr(latest_slot, "value") else latest_slot.get("result", 0)

            if current_slot >= latest_slot:
                await asyncio.sleep(POLL_INTERVAL)
                continue

            logs = await fetch_recent_logs(client, current_slot, latest_slot)
            for log_block in logs:
                events = extract_events_from_log_block(log_block)
                for event in events:
                    await handle_event(event)

            current_slot = latest_slot + 1
            await asyncio.sleep(POLL_INTERVAL)
        except Exception as e:
            logger.error(f"Listener error: {e}")
            await asyncio.sleep(10)

async def handle_event(event: ParsedEvent):
    if event.event_type == "AI_TRIGGER":
        task_id = event.data.get("task_id")
        model_id = event.data.get("model_id")
        input_data = event.data.get("input")
        logger.info(f"Trigger received [{task_id}] -> {model_id}")
        submit_task(model_id, input_data)
    elif event.event_type == "RESULT_READY":
        logger.info(f"Result reported for task {event.data.get('task_id')}")
    elif event.event_type == "ERROR":
        logger.warning(f"Error event: {event.data}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(listen_for_triggers())
