import asyncio
import logging
import time
import statistics
from typing import List, Dict, Any

from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TokenAccountOpts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("METRICS_COLLECTOR")

RPC_URL = "https://api.mainnet-beta.solana.com"
COLLECTION_INTERVAL = 20

class SlotMetrics:
    def __init__(self):
        self.slot_times: List[float] = []
        self.last_slot = None
        self.last_timestamp = None

    def update(self, current_slot: int):
        now = time.time()

        if self.last_slot is not None:
            delta_slots = current_slot - self.last_slot
            delta_time = now - self.last_timestamp

            if delta_slots > 0:
                avg_slot_time = delta_time / delta_slots
                self.slot_times.append(avg_slot_time)
                if len(self.slot_times) > 100:
                    self.slot_times.pop(0)

        self.last_slot = current_slot
        self.last_timestamp = now

    def get_average_slot_time(self) -> float:
        return statistics.mean(self.slot_times) if self.slot_times else 0.0

async def fetch_leader_schedule(client: AsyncClient) -> Dict[str, Any]:
    res = await client.get_leader_schedule()
    return res.value if hasattr(res, "value") else {}

async def fetch_fee_rate(client: AsyncClient) -> float:
    res = await client.get_fees()
    try:
        lamports_per_sig = res.value.fee_calculator.lamports_per_signature
        return lamports_per_sig / 1_000_000_000  # Convert to SOL
    except:
        return 0.000005  # fallback value

async def fetch_vote_accounts(client: AsyncClient) -> List[str]:
    res = await client.get_vote_accounts()
    try:
        current_validators = res.value["current"]
        return [v["nodePubkey"] for v in current_validators]
    except:
        return []

async def metrics_loop():
    client = AsyncClient(RPC_URL)
    slot_metrics = SlotMetrics()

    while True:
        try:
            slot_resp = await client.get_slot()
            current_slot = slot_resp.value if hasattr(slot_resp, "value") else slot_resp.get("result", 0)
            slot_metrics.update(current_slot)

            avg_slot_time = slot_metrics.get_average_slot_time()
            leader_schedule = await fetch_leader_schedule(client)
            fee_estimate = await fetch_fee_rate(client)
            validators = await fetch_vote_accounts(client)

            logger.info(f"Slot: {current_slot}")
            logger.info(f"Avg slot time: {avg_slot_time:.2f}s")
            logger.info(f"Fee estimate: {fee_estimate:.6f} SOL")
            logger.info(f"Active validators: {len(validators)}")
        except Exception as e:
            logger.error(f"Error in metrics collection: {e}")

        await asyncio.sleep(COLLECTION_INTERVAL)

if __name__ == "__main__":
    asyncio.run(metrics_loop())
