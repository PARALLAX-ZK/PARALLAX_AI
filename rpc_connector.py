import requests
import json
import logging
from typing import Optional, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RPC_CONNECTOR")

DEFAULT_ENDPOINT = "https://api.mainnet-beta.solana.com"
HEADERS = {"Content-Type": "application/json"}

class SolanaRPC:
    def __init__(self, endpoint: str = DEFAULT_ENDPOINT):
        self.endpoint = endpoint

    def _post(self, method: str, params: list) -> Optional[Dict[str, Any]]:
        body = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }

        try:
            response = requests.post(self.endpoint, headers=HEADERS, data=json.dumps(body), timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"RPC error: {response.status_code}")
        except Exception as e:
            logger.error(f"RPC connection failed: {e}")
        return None

    def get_account_info(self, pubkey: str, encoding: str = "base64") -> Optional[Dict[str, Any]]:
        params = [pubkey, {"encoding": encoding}]
        result = self._post("getAccountInfo", params)
        return result.get("result") if result else None

    def get_program_accounts(self, program_id: str, filters: Optional[list] = None) -> Optional[Dict[str, Any]]:
        options = {
            "encoding": "jsonParsed",
            "filters": filters or []
        }
        params = [program_id, options]
        result = self._post("getProgramAccounts", params)
        return result.get("result") if result else None

    def get_slot(self) -> Optional[int]:
        result = self._post("getSlot", [])
        return result.get("result") if result else None

    def get_latest_blockhash(self) -> Optional[str]:
        result = self._post("getLatestBlockhash", [])
        try:
            return result["result"]["value"]["blockhash"]
        except:
            return None

    def simulate_transaction(self, tx_base64: str) -> Optional[Dict[str, Any]]:
        params = [tx_base64, {"encoding": "base64"}]
        result = self._post("simulateTransaction", params)
        return result.get("result") if result else None

    def send_transaction(self, tx_base64: str) -> Optional[str]:
        params = [tx_base64, {"encoding": "base64"}]
        result = self._post("sendTransaction", params)
        if result and "result" in result:
            logger.info(f"Transaction submitted: {result['result']}")
            return result["result"]
        logger.error(f"Transaction failed: {result}")
        return None

    def get_logs(self, start_slot: int, end_slot: Optional[int] = None) -> Optional[Dict[str, Any]]:
        params = [{"startSlot": start_slot}]
        if end_slot:
            params[0]["endSlot"] = end_slot
        result = self._post("getLogs", params)
        return result.get("result") if result else None

if __name__ == "__main__":
    rpc = SolanaRPC()
    print("Current slot:", rpc.get_slot())
    print("Latest blockhash:", rpc.get_latest_blockhash())

    test_account = "11111111111111111111111111111111"
    info = rpc.get_account_info(test_account)
    print("Account info:", info)
