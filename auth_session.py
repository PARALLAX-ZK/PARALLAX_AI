from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import os
import logging

logger = logging.getLogger("AUTH_SESSION")

# You can configure this via env or a secure vault
API_KEY = os.environ.get("PARALLAX_DASHBOARD_API_KEY", "demo-key")

# Use FastAPI's HTTP Bearer Auth scheme
security = HTTPBearer()

class AuthSession:
    def __init__(self, api_key: str = API_KEY):
        self.api_key = api_key

    def verify_token(self, token: str) -> bool:
        return token == self.api_key

    def protect_route(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        token = credentials.credentials
        if not self.verify_token(token):
            logger.warning(f"Unauthorized access attempt with token: {token}")
            raise HTTPException(status_code=403, detail="Invalid authentication token")

# Optional: attach to specific admin routes
auth = AuthSession()

# Example usage inside a FastAPI route:
# from auth_session import auth
# @app.get("/admin/secure-data")
# async def secure_endpoint(deps=Depends(auth.protect_route)):
#     return {"msg": "Only accessible with correct token"}
