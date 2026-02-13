# app/routers/analysis.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.services.llm_service import llm_service
from app.models.schemas import Message, Role

router = APIRouter()

class SentimentResult(BaseModel):
    sentiment: str  # POSITIVE, NEGATIVE, NEUTRAL
    confidence: float
    explanation: str

class EntityResult(BaseModel):
    text: str
    type: str
    start: int
    end: int

class AnalysisResponse(BaseModel):
    summary: str
    sentiment: SentimentResult
    entities: List[EntityResult]
    key_points: List[str]
    tokens_used: int

@router.post("/document", response_model=AnalysisResponse)
async def analyze_document(text: str):
    """Analyse complète d'un document."""
    
    # Prompt d'analyse structurée
    analysis_prompt = f"""
Analyse le document suivant et retourne un JSON avec cette structure exacte :

{{
    "summary": "Résumé en 2-3 phrases",
    "sentiment": {{
        "sentiment": "POSITIVE|NEGATIVE|NEUTRAL",
        "confidence": 0.0-1.0,
        "explanation": "Explication courte"
    }},
    "entities": [
        {{"text": "entité", "type": "PERSON|ORG|LOCATION|DATE", "start": 0, "end": 10}}
    ],
    "key_points": ["Point 1", "Point 2", "Point 3"]
}}

Document :
{text}

JSON (uniquement, sans markdown) :
"""
    
    messages = [Message(role=Role.USER, content=analysis_prompt)]
    
    result = await llm_service.complete(
        messages=messages,
        temperature=0.0  # Déterministe pour l'analyse
    )
    
    try:
        import json
        analysis = json.loads(result["content"])
        
        return AnalysisResponse(
            summary=analysis["summary"],
            sentiment=SentimentResult(**analysis["sentiment"]),
            entities=[EntityResult(**e) for e in analysis["entities"]],
            key_points=analysis["key_points"],
            tokens_used=result["tokens"]
        )
    except (json.JSONDecodeError, KeyError) as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse LLM response: {str(e)}"
        )

@router.post("/classify")
async def classify_text(text: str, categories: List[str]):
    """Classifie un texte dans des catégories données."""
    
    categories_str = ", ".join(categories)
    
    prompt = f"""
Classifie le texte dans UNE des catégories suivantes : {categories_str}

Texte : "{text}"

Réponds avec un JSON :
{{"category": "CATÉGORIE", "confidence": 0.0-1.0, "reasoning": "explication"}}
"""
    
    messages = [Message(role=Role.USER, content=prompt)]
    result = await llm_service.complete(messages=messages, temperature=0.0)
    
    import json
    return json.loads(result["content"])