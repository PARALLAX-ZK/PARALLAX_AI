import asyncio
import logging
from typing import Dict, List, Optional
from solana.rpc.async_api import AsyncClient
from solana.publickey import PublicKey

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VOTE_TRACKER")

RPC_URL = "https://api.mainnet-beta.solana.com"
VOTE_TRACK_INTERVAL = 60

class ValidatorVoteState:
    def __init__(self, pubkey: str):
        self.pubkey = pubkey
        self.total_votes = 0
        self.last_vote_slot = 0
        self.active = True

    def update_vote(self, slot: int):
        if slot > self.last_vote_slot:
            self.last_vote_slot = slot
            self.total_votes += 1

class VoteTracker:
    def __init__(self):
        self.validators: Dict[str, ValidatorVoteState] = {}

    def update_from_vote_data(self, vote_data: List[Dict[str, any]]):
        for entry in vote_data:
            pubkey = entry.get("nodePubkey")
            vote_state = self.validators.get(pubkey, ValidatorVoteState(pubkey))
            last_vote = int(entry.get("lastVote", 0))
            vote_state.update_vote(last_vote)
            vote_state.active = entry.get("activatedStake", 0) > 0
            self.validators[pubkey] = vote_state

    def get_top_voters(self, limit: int = 10) -> List[ValidatorVoteState]:
        sorted_votes = sorted(
            self.validators.values(),
            key=lambda x: x.total_votes,
            reverse=True
        )
        return sorted_votes[:limit]

    def export_snapshot(self) -> Dict[str, Dict]:
        return {
            pubkey: {
                "last_vote": v.last_vote_slot,
                "total_votes": v.total_votes,
                "active": v.active
            } for pubkey, v in self.validators.items()
        }

async def fetch_vote_accounts(client: AsyncClient) -> Optional[List[Dict[str, any]]]:
    try:
        res = await client.get_vote_accounts()
        if "result" in res:
            return res["result"]["current"]
        if hasattr(res, "value"):
            return res.value["current"]
        return []
    except Exception as e:
        logger.error(f"Failed to fetch vote accounts: {e}")
        return []

async def track_votes():
    client = AsyncClient(RPC_URL)
    tracker = VoteTracker()

    while True:
        try:
            vote_data = await fetch_vote_accounts(client)
            if vote_data:
                tracker.update_from_vote_data(vote_data)
                top_voters = tracker.get_top_voters(5)
                logger.info("Top 5 active validators:")
                for v in top_voters:
                    logger.info(f"  {v.pubkey}: {v.total_votes} votes (last slot: {v.last_vote_slot})")
        except Exception as e:
            logger.error(f"Vote tracking error: {e}")
        await asyncio.sleep(VOTE_TRACK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(track_votes())
