# Logging structuré
# app/middleware/logging.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import json
import logging

logger = logging.getLogger("ai_backend")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        request_log = {
            "type": "request",
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host,
        }
        logger.info(json.dumps(request_log))
        
        # Process
        response = await call_next(request)
        
        # Log response
        duration_ms = (time.time() - start_time) * 1000
        response_log = {
            "type": "response",
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2)
        }
        logger.info(json.dumps(response_log))
        
        return response