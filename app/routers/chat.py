# Endpoints chat
# app/routers/chat.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from uuid import uuid4
import json

from app.models.schemas import ChatRequest, ChatResponse, Message, Role
from app.services.llm_service import llm_service
from app.services.conversation import conversation_service

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Endpoint de chat simple."""
    try:
        # Construire les messages
        messages = []
        
        # System prompt
        if request.system_prompt:
            messages.append(Message(role=Role.SYSTEM, content=request.system_prompt))
        
        # Historique de conversation (si existant)
        if request.conversation_id:
            history = await conversation_service.get_history(request.conversation_id)
            messages.extend(history)
        else:
            request.conversation_id = str(uuid4())
        
        # Message utilisateur
        messages.append(Message(role=Role.USER, content=request.message))
        
        # Appel LLM
        result = await llm_service.complete(
            messages=messages,
            temperature=request.temperature
        )
        
        # Sauvegarder dans l'historique
        await conversation_service.add_message(
            request.conversation_id,
            Message(role=Role.USER, content=request.message)
        )
        await conversation_service.add_message(
            request.conversation_id,
            Message(role=Role.ASSISTANT, content=result["content"])
        )
        
        return ChatResponse(
            response=result["content"],
            conversation_id=request.conversation_id,
            tokens_used=result["tokens"],
            model=result["model"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """Endpoint de chat avec streaming."""
    
    async def generate():
        messages = []
        if request.system_prompt:
            messages.append(Message(role=Role.SYSTEM, content=request.system_prompt))
        messages.append(Message(role=Role.USER, content=request.message))
        
        async for chunk in await llm_service.complete(
            messages=messages,
            temperature=request.temperature,
            stream=True
        ):
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )