import time
import logging
from typing import Dict, List, Optional

logger = logging.getLogger("ROUTER")

# Sample in-memory registry snapshots (would be imported from sequencer_core in a real app)
REGISTERED_NODES: Dict[str, Dict] = {}
PENDING_TASKS: List[Dict] = []

ROUTING_STRATEGY = "round_robin"

_last_assigned_node_index = 0  # For round-robin fallback


def find_compatible_node(task: Dict) -> Optional[str]:
    """Select a compatible node for a given task."""
    compatible_nodes = [
        node_id for node_id, info in REGISTERED_NODES.items()
        if task["model"] in info["capabilities"]
    ]

    if not compatible_nodes:
        logger.warning("No compatible nodes found for model: " + task["model"])
        return None

    if ROUTING_STRATEGY == "round_robin":
        global _last_assigned_node_index
        selected = compatible_nodes[_last_assigned_node_index % len(compatible_nodes)]
        _last_assigned_node_index += 1
        return selected

    elif ROUTING_STRATEGY == "lowest_latency":
        # Placeholder for latency-aware node selection
        return compatible_nodes[0]

    return compatible_nodes[0]


def assign_task_to_node(task: Dict) -> Optional[str]:
    """Assigns the given task to an available node and updates the task record."""
    node_id = find_compatible_node(task)
    if node_id:
        task["assigned"] = node_id
        task["assigned_at"] = int(time.time())
        logger.info(f" Routed task {task['task_id']} to node {node_id}")
        return node_id
    return None


def enqueue_task(model: str, input_data: str) -> Dict:
    """Enqueues a new task to the system and routes it if possible."""
    task_id = f"task-{int(time.time() * 1000)}"
    task = {
        "task_id": task_id,
        "model": model,
        "input": input_data,
        "created_at": int(time.time()),
        "assigned": None
    }

    PENDING_TASKS.append(task)
    logger.info(f" Task enqueued: {task_id}")

    node_id = assign_task_to_node(task)
    return {
        "task_id": task_id,
        "status": "assigned" if node_id else "queued",
        "assigned_to": node_id
    }


def get_task_for_node(node_id: str) -> Optional[Dict]:
    """Returns a task assigned to the given node."""
    for task in PENDING_TASKS:
        if task.get("assigned") == node_id:
            return task
    return None


def mark_task_completed(task_id: str) -> None:
    """Removes task from the pending queue."""
    global PENDING_TASKS
    PENDING_TASKS = [t for t in PENDING_TASKS if t["task_id"] != task_id]
    logger.info(f" Task {task_id} marked as completed")


def health_check(node_id: str) -> bool:
    """Checks if the node has recently pinged (placeholder for now)."""
    node = REGISTERED_NODES.get(node_id)
    if not node:
        return False
    last_seen = node.get("last_seen", 0)
    return (time.time() - last_seen) < 60  # 1 minute timeout


def reassign_stale_tasks() -> int:
    """Finds stale tasks and attempts to reassign them."""
    reassigned_count = 0
    for task in PENDING_TASKS:
        if "assigned_at" in task and (time.time() - task["assigned_at"] > 30):
            logger.info(f" Reassigning stale task {task['task_id']}")
            assign_task_to_node(task)
            reassigned_count += 1
    return reassigned_count


if __name__ == "__main__":
    # Demo mode
    REGISTERED_NODES["node-A"] = {"capabilities": ["parallax-llm-v1"], "last_seen": time.time()}
    REGISTERED_NODES["node-B"] = {"capabilities": ["quant-forecast-lite"], "last_seen": time.time()}

    enqueue_task("parallax-llm-v1", "What is Solana?")
    enqueue_task("quant-forecast-lite", "How will BTC move?")
    enqueue_task("vision-encoder-v2", "https://image.url/image.png")

    print(get_task_for_node("node-A"))
    print(get_task_for_node("node-B"))
    print(f"Reassigned: {reassign_stale_tasks()} tasks")
