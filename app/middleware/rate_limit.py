# Rate limiting
# app/middleware/rate_limit.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: dict[str, list[datetime]] = defaultdict(list)
        self._lock = asyncio.Lock()
    
    async def dispatch(self, request: Request, call_next):
        # Identifier le client (IP ou API key)
        client_id = request.client.host
        
        async with self._lock:
            now = datetime.now()
            window_start = now - timedelta(minutes=1)
            
            # Nettoyer les anciennes requêtes
            self.requests[client_id] = [
                ts for ts in self.requests[client_id]
                if ts > window_start
            ]
            
            # Vérifier la limite
            if len(self.requests[client_id]) >= self.requests_per_minute:
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Please wait before making more requests."
                )
            
            # Enregistrer cette requête
            self.requests[client_id].append(now)
        
        return await call_next(request)

# Dans main.py
# app.add_middleware(RateLimitMiddleware, requests_per_minute=100)