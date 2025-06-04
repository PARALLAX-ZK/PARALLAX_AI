import asyncio
import logging
from typing import Dict, List

from fastapi import WebSocket

logger = logging.getLogger("REAL_TIME_UPDATES")

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected: {id(websocket)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected: {id(websocket)}")

    async def broadcast_json(self, message: Dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"WebSocket error: {e}")

# Global WebSocket manager instance
manager = WebSocketManager()

# WebSocket event handler for FastAPI routing
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            msg = await websocket.receive_text()
            await websocket.send_text("pong")
    except Exception:
        manager.disconnect(websocket)

# Called externally by other services to trigger live dashboard updates
async def push_update(event_type: str, data: Dict):
    message = {
        "event": event_type,
        "payload": data
    }
    await manager.broadcast_json(message)

# Example periodic pusher (can be triggered in dashboard_app or metrics_collector)
async def periodic_ping():
    while True:
        await push_update("heartbeat", {"status": "alive", "timestamp": asyncio.get_event_loop().time()})
        await asyncio.sleep(30)
