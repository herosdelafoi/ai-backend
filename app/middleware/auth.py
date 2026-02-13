# app/middleware/auth.py
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Vérifie la clé API."""
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    # En production : vérifier contre une DB ou cache
    valid_keys = {"demo-key-123", "prod-key-456"}
    
    if api_key not in valid_keys:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    return api_key