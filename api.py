from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
import logging
import uuid
import time
from sentiment_model import analyze_sentiment

app = FastAPI()

# Allow frontend dashboard or dev clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CHATBOT_API")

# In-memory cache (replace with Redis or DB later)
HISTORY: Dict[str, List[Dict[str, Any]]] = {}

# Request schema
class QueryRequest(BaseModel):
    session_id: str
    query: str
    model_id: str = "parallax-llm-v1"
    return_dacert: bool = False

# Response schema
class QueryResponse(BaseModel):
    session_id: str
    task_id: str
    result: Dict[str, Any]
    dacert: Dict[str, Any] = {}

@app.post("/query", response_model=QueryResponse)
async def run_query(request: QueryRequest):
    if not request.query:
        raise HTTPException(status_code=400, detail="Query text required")

    task_id = str(uuid.uuid4())
    timestamp = int(time.time())

    logger.info(f"Received query from session {request.session_id}: {request.query}")

    # Simulate model response
    model_output = analyze_sentiment([request.query])[0]
    result = {
        "input": request.query,
        "output": model_output["sentiment"],
        "confidence": model_output["confidence"],
        "timestamp": timestamp,
        "model_id": request.model_id
    }

    dacert = {}
    if request.return_dacert:
        dacert = {
            "task_id": task_id,
            "output_hash": hash(f"{request.query}:{model_output['sentiment']}"),
            "signers": ["validator-A", "validator-B", "validator-C"],
            "signatures": ["sig1", "sig2", "sig3"],
            "quorum": 3
        }

    # Store in memory for session tracking
    if request.session_id not in HISTORY:
        HISTORY[request.session_id] = []

    HISTORY[request.session_id].append({
        "task_id": task_id,
        "query": request.query,
        "response": result,
        "dacert": dacert
    })

    return QueryResponse(
        session_id=request.session_id,
        task_id=task_id,
        result=result,
        dacert=dacert
    )

@app.get("/history/{session_id}")
async def get_history(session_id: str):
    if session_id not in HISTORY:
        return {"session_id": session_id, "history": []}
    return {"session_id": session_id, "history": HISTORY[session_id]}

@app.get("/health")
async def health_check():
    return {"status": "ok", "uptime": f"{int(time.time())} seconds"}

@app.get("/models")
async def get_supported_models():
    return {
        "available_models": [
            "parallax-llm-v1",
            "quant-forecast-lite",
            "vision-encoder-v2"
        ]
    }

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8080, reload=False)
