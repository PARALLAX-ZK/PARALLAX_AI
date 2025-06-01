import threading
import time
import uuid
import logging
from typing import Dict, List, Optional
from queue import Queue, Empty

from inference_executor import run_inference
from dacert_generator import generate_dacert
from retryable_tx import submit_result_retryable
import aiohttp
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TASK_SCHEDULER")

MAX_RETRIES = 3
RETRY_INTERVAL = 10

class InferenceTask:
    def __init__(self, model_id: str, input_data: str, retries: int = 0):
        self.task_id = str(uuid.uuid4())
        self.model_id = model_id
        self.input_data = input_data
        self.retries = retries
        self.submitted = False
        self.last_attempt = 0

    def mark_attempt(self):
        self.last_attempt = time.time()
        self.retries += 1

    def is_retryable(self):
        return self.retries < MAX_RETRIES

task_queue: Queue[InferenceTask] = Queue()
failed_tasks: List[InferenceTask] = []
active_tasks: Dict[str, InferenceTask] = {}

SEQUENCER_URL = "http://localhost:5050"

def submit_task(model_id: str, input_data: str):
    task = InferenceTask(model_id, input_data)
    task_queue.put(task)
    active_tasks[task.task_id] = task
    logger.info(f"Task {task.task_id} submitted to queue")

async def process_task(task: InferenceTask):
    logger.info(f"Processing task {task.task_id}")
    task.mark_attempt()

    try:
        result = run_inference(task.model_id, task.input_data)
        dacert = generate_dacert("node-scheduler", task.task_id, result)

        async with aiohttp.ClientSession() as session:
            success = await submit_result_retryable(session, task.task_id, result, dacert)

        if success:
            logger.info(f"Task {task.task_id} completed successfully")
            task.submitted = True
            del active_tasks[task.task_id]
        else:
            raise RuntimeError("Submission failed")

    except Exception as e:
        logger.warning(f"Error processing task {task.task_id}: {e}")
        if task.is_retryable():
            task_queue.put(task)
        else:
            failed_tasks.append(task)
            logger.error(f"Task {task.task_id} permanently failed after {task.retries} retries")

def task_worker():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while True:
        try:
            task: InferenceTask = task_queue.get(timeout=2)
            if not task.submitted:
                loop.run_until_complete(process_task(task))
        except Empty:
            time.sleep(1)
        except Exception as e:
            logger.error(f"Unhandled error in task worker: {e}")

def start_scheduler(num_workers: int = 2):
    logger.info(f"Starting task scheduler with {num_workers} worker(s)")
    for _ in range(num_workers):
        t = threading.Thread(target=task_worker, daemon=True)
        t.start()

if __name__ == "__main__":
    start_scheduler()

    submit_task("parallax-llm-v1", "How does zkML work?")
    submit_task("quant-forecast-lite", "What is the BTC forecast this week?")
    submit_task("vision-encoder-v2", "https://example.com/image.png")

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        logger.info("Scheduler shutting down")
