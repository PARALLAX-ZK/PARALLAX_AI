from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import time
import uuid
from typing import List, Dict

from metrics_collector import collect_metrics
from cache_manager import CacheManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DASHBOARD_APP")

app = FastAPI(title="PARALLAX Dashboard")

# Mount frontend if needed
app.mount("/static", StaticFiles(directory="dashboards/static"), name="static")

# CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cache = CacheManager()
active_websockets: List[WebSocket] = []

@app.get("/")
async def root():
    return HTMLResponse(content="<h1>PARALLAX Dashboard is Running</h1>", status_code=200)

@app.get("/status")
async def status():
    return {
        "timestamp": time.time(),
        "registered_nodes": cache.get("node_count") or 0,
        "pending_tasks": cache.get("pending_tasks") or 0,
        "completed_tasks": cache.get("completed_tasks") or 0,
    }

@app.get("/analytics/tasks")
async def task_analytics():
    return {
        "average_latency": cache.get("average_latency") or 0,
        "boot_time": cache.get("boot_time") or int(time.time()) - 120
    }

@app.get("/analytics/models")
async def model_analytics():
    return {
        "model_usage": cache.get("model_usage") or {}
    }

@app.get("/analytics/nodes")
async def node_health():
    return {
        "nodes": cache.get("node_health") or {}
    }

@app.get("/analytics/recent")
async def recent_tasks():
    return {
        "recent_tasks": cache.get("recent_tasks") or []
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = str(uuid.uuid4())
    logger.info(f"WebSocket connected: {session_id}")
    active_websockets.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            logger.debug(f"Received from {session_id}: {data}")
            await websocket.send_text("pong")
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
        active_websockets.remove(websocket)

async def broadcast_update(event: str, payload: Dict):
    for ws in active_websockets:
        try:
            await ws.send_json({"event": event, "data": payload})
        except Exception as e:
            logger.warning(f"Failed to send update: {e}")

@app.on_event("startup")
async def startup_event():
    cache.set("boot_time", int(time.time()))
    logger.info("Dashboard started. Initializing metric loop...")

    import asyncio
    loop = asyncio.get_event_loop()
    loop.create_task(collect_metrics(cache, broadcast_update))
