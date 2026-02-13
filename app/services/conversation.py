# Gestion conversations
# app/services/conversation.py
from typing import Dict, List
from datetime import datetime, timedelta
from app.models.schemas import Message
import asyncio

class ConversationService:
    """Gestion des conversations en mémoire (pour démo)."""
    
    def __init__(self, max_messages: int = 20, ttl_minutes: int = 60):
        self._conversations: Dict[str, List[Message]] = {}
        self._timestamps: Dict[str, datetime] = {}
        self._max_messages = max_messages
        self._ttl = timedelta(minutes=ttl_minutes)
        
        # Cleanup automatique
        asyncio.create_task(self._cleanup_loop())
    
    async def get_history(self, conversation_id: str) -> List[Message]:
        """Récupère l'historique d'une conversation."""
        return self._conversations.get(conversation_id, [])
    
    async def add_message(self, conversation_id: str, message: Message):
        """Ajoute un message à une conversation."""
        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = []
        
        self._conversations[conversation_id].append(message)
        self._timestamps[conversation_id] = datetime.now()
        
        # Limiter la taille
        if len(self._conversations[conversation_id]) > self._max_messages:
            # Garder le premier (system) et les plus récents
            self._conversations[conversation_id] = (
                self._conversations[conversation_id][:1] +
                self._conversations[conversation_id][-(self._max_messages-1):]
            )
    
    async def clear_conversation(self, conversation_id: str):
        """Supprime une conversation."""
        self._conversations.pop(conversation_id, None)
        self._timestamps.pop(conversation_id, None)
    
    async def _cleanup_loop(self):
        """Nettoie les conversations expirées."""
        while True:
            await asyncio.sleep(300)  # Check toutes les 5 minutes
            now = datetime.now()
            expired = [
                cid for cid, ts in self._timestamps.items()
                if now - ts > self._ttl
            ]
            for cid in expired:
                await self.clear_conversation(cid)

conversation_service = ConversationService()