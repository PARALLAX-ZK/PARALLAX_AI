from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import logging
import time
import uuid
from typing import Dict, List

from cache_manager import CacheManager
from task_scheduler import submit_task

logger = logging.getLogger("API_BACKEND")
router = APIRouter()
cache = CacheManager()

class InferenceRequest(BaseModel):
    model_id: str
    input_data: str
    user_id: str

class InferenceResponse(BaseModel):
    task_id: str
    status: str

class TaskQuery(BaseModel):
    task_id: str

@router.post("/inference/request", response_model=InferenceResponse)
async def request_inference(req: InferenceRequest):
    task_id = str(uuid.uuid4())
    logger.info(f"New inference request: {task_id} from {req.user_id}")
    
    submit_task(req.model_id, req.input_data)
    
    recent_tasks: List[Dict] = cache.get("recent_tasks") or []
    recent_tasks.insert(0, {
        "task_id": task_id,
        "model_id": req.model_id,
        "timestamp": int(time.time()),
        "latency": 0
    })
    cache.set("recent_tasks", recent_tasks[:25])

    return InferenceResponse(task_id=task_id, status="submitted")

@router.post("/inference/result")
async def get_result(q: TaskQuery):
    result = cache.get(f"task_result:{q.task_id}")
    if not result:
        raise HTTPException(status_code=404, detail="Result not available")
    return result

@router.post("/agent/report")
async def agent_report(data: Dict):
    logger.info(f"Agent report received: {data}")
    node_health: Dict = cache.get("node_health") or {}
    node_id = data.get("node_id", "unknown")
    node_health[node_id] = {
        "latency": data.get("latency"),
        "status": data.get("status"),
        "last_seen": int(time.time())
    }
    cache.set("node_health", node_health)
    return {"ok": True}

@router.get("/agents")
async def list_agents():
    return cache.get("node_health") or {}

@router.get("/inference/recent")
async def recent():
    return cache.get("recent_tasks") or []
