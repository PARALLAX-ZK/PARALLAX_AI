import logging
import uuid
import time
from typing import List, Dict, Tuple
from task_scheduler import submit_task, InferenceTask

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BATCH_DISPATCHER")

MAX_TASKS_PER_BATCH = 100

class BatchReport:
    def __init__(self):
        self.accepted: List[str] = []
        self.rejected: List[Tuple[str, str]] = []  # (task_id, reason)
        self.timestamp = int(time.time())

    def add_success(self, task_id: str):
        self.accepted.append(task_id)

    def add_failure(self, task_id: str, reason: str):
        self.rejected.append((task_id, reason))

    def summary(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "accepted_count": len(self.accepted),
            "rejected_count": len(self.rejected),
            "accepted_ids": self.accepted,
            "rejected_reasons": self.rejected
        }

def validate_task_payload(payload: Dict) -> Tuple[bool, str]:
    if "model_id" not in payload or "input" not in payload:
        return False, "Missing required fields"

    if not isinstance(payload["input"], str):
        return False, "Input must be a string"

    if len(payload["input"]) > 1000:
        return False, "Input too long"

    return True, ""

def dispatch_batch(batch: List[Dict[str, str]]) -> Dict:
    report = BatchReport()

    if len(batch) > MAX_TASKS_PER_BATCH:
        logger.warning("Batch size exceeds maximum. Truncating.")
        batch = batch[:MAX_TASKS_PER_BATCH]

    logger.info(f"Dispatching batch of {len(batch)} tasks")

    for entry in batch:
        valid, error = validate_task_payload(entry)
        task_id = str(uuid.uuid4())

        if not valid:
            report.add_failure(task_id, error)
            logger.warning(f"Rejected task {task_id}: {error}")
            continue

        model_id = entry["model_id"]
        input_data = entry["input"]

        try:
            submit_task(model_id, input_data)
            report.add_success(task_id)
        except Exception as e:
            report.add_failure(task_id, str(e))
            logger.error(f"Failed to dispatch task {task_id}: {e}")

    summary = report.summary()
    logger.info(f"Batch dispatch complete: {summary}")
    return summary

if __name__ == "__main__":
    # Example batch
    sample_batch = [
        {"model_id": "parallax-llm-v1", "input": "Analyze: The crypto market is volatile today."},
        {"model_id": "quant-forecast-lite", "input": "Predict BTC next week."},
        {"model_id": "vision-encoder-v2", "input": "https://example.com/chart.png"},
        {"model_id": "unknown-model", "input": "What’s up with DOGE?"},  # This will be accepted (validation is lenient)
        {"model_id": "parallax-llm-v1", "input": 123456},  # Will be rejected (input not string)
        {"model_id": "parallax-llm-v1"}  # Will be rejected (missing input)
    ]

    result = dispatch_batch(sample_batch)
    print(result)
