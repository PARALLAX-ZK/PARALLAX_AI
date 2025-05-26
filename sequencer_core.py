from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import logging
import uuid
import time

from typing import Dict, List

app = FastAPI()
logger = logging.getLogger("SEQUENCER")
logging.basicConfig(level=logging.INFO)

# In-memory registries (can later use Redis/Postgres)
REGISTERED_NODES: Dict[str, Dict] = {}
PENDING_TASKS: List[Dict] = []
COMPLETED_TASKS: Dict[str, Dict] = {}

@app.post("/register_node")
async def register_node(request: Request):
    data = await request.json()
    required_fields = ["node_id", "capabilities", "public_key"]

    if not all(field in data for field in required_fields):
        raise HTTPException(status_code=400, detail="Missing required fields.")

    REGISTERED_NODES[data["node_id"]] = {
        "capabilities": data["capabilities"],
        "public_key": data["public_key"],
        "registered_at": int(time.time()),
        "last_seen": int(time.time())
    }

    logger.info(f" Node registered: {data['node_id']}")
    return {"status": "ok", "message": "Node registered"}

@app.get("/get_task")
async def get_task(node_id: str):
    # Find a task for this node (naive filter by model support)
    node = REGISTERED_NODES.get(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    for task in PENDING_TASKS:
        if task["model"] in node["capabilities"] and not task.get("assigned"):
            task["assigned"] = node_id
            logger.info(f" Task {task['task_id']} assigned to {node_id}")
            return task

    return JSONResponse(content={"message": "No tasks available"}, status_code=204)

@app.post("/submit_result")
async def submit_result(request: Request):
    body = await request.json()
    required_fields = ["task_id", "result", "dacert"]

    if not all(key in body for key in required_fields):
        raise HTTPException(status_code=400, detail="Missing fields in submission.")

    task_id = body["task_id"]
    result = body["result"]
    dacert = body["dacert"]

    if task_id not in [t["task_id"] for t in PENDING_TASKS]:
        raise HTTPException(status_code=404, detail="Task not found")

    # Basic DACert validation placeholder
    payload = dacert.get("cert_payload", {})
    if payload.get("task_id") != task_id:
        raise HTTPException(status_code=400, detail="DACert task ID mismatch")

    COMPLETED_TASKS[task_id] = {
        "result": result,
        "dacert": dacert,
        "completed_at": int(time.time())
    }

    # Remove from pending
    global PENDING_TASKS
    PENDING_TASKS = [t for t in PENDING_TASKS if t["task_id"] != task_id]

    logger.info(f"Task {task_id} result stored")
    return {"status": "ok", "message": "Result submitted"}

@app.get("/node_status/{node_id}")
async def node_status(node_id: str):
    node = REGISTERED_NODES.get(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not registered")
    return node

@app.post("/submit_task")
async def submit_task(request: Request):
    body = await request.json()
    required = ["model", "input"]

    if not all(k in body for k in required):
        raise HTTPException(status_code=400, detail="Missing model or input")

    task = {
        "task_id": str(uuid.uuid4()),
        "model": body["model"],
        "input": body["input"],
        "created_at": int(time.time())
    }

    PENDING_TASKS.append(task)
    logger.info(f" Task submitted: {task['task_id']}")
    return {"status": "queued", "task_id": task["task_id"]}

@app.get("/status")
async def status():
    return {
        "registered_nodes": len(REGISTERED_NODES),
        "pending_tasks": len(PENDING_TASKS),
        "completed_tasks": len(COMPLETED_TASKS)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5050)
