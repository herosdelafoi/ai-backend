# Endpoints analyse
# app/routers/analysis.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import json

from app.services.llm_service import llm_service
from app.models.schemas import Message, Role

router = APIRouter()

# Models pour l'analyse de document
class SentimentResult(BaseModel):
    sentiment: str  # POSITIVE, NEGATIVE, NEUTRAL
    confidence: float
    explanation: str

class EntityResult(BaseModel):
    text: str
    type: str  # PERSON, ORG, LOCATION, DATE
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
        # Extraire le JSON de la réponse (enlever les markdown backticks si présents)
        content = result["content"].strip()
        if content.startswith("```"):
            # Enlever les markdown code blocks
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]

        analysis = json.loads(content)

        return AnalysisResponse(
            summary=analysis["summary"],
            sentiment=SentimentResult(**analysis["sentiment"]),
            entities=[EntityResult(**e) for e in analysis.get("entities", [])],
            key_points=analysis["key_points"],
            tokens_used=result["tokens"]
        )
    except (json.JSONDecodeError, KeyError) as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse LLM response: {str(e)}"
        )

# Classification de texte
class ClassifyRequest(BaseModel):
    text: str
    categories: List[str] = Field(..., min_items=2, max_items=10)

class ClassifyResponse(BaseModel):
    category: str
    confidence: float
    reasoning: str

@router.post("/classify", response_model=ClassifyResponse)
async def classify_text(request: ClassifyRequest):
    """Classifie un texte dans des catégories données."""

    categories_str = ", ".join(request.categories)

    prompt = f"""
Classifie le texte dans UNE des catégories suivantes : {categories_str}
Texte : "{request.text}"
Réponds avec un JSON :
{{"category": "CATÉGORIE", "confidence": 0.0-1.0, "reasoning": "explication"}}
JSON uniquement :
"""

    messages = [Message(role=Role.USER, content=prompt)]
    result = await llm_service.complete(messages=messages, temperature=0.0)

    try:
        content = result["content"].strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]

        data = json.loads(content)
        return ClassifyResponse(**data)
    except (json.JSONDecodeError, KeyError) as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse classification response: {str(e)}"
        )

# Traitement par batch
class BatchRequest(BaseModel):
    texts: List[str] = Field(..., min_items=1, max_items=10)
    operation: str = Field(..., description="summarize or sentiment")

class BatchResult(BaseModel):
    text: str
    result: str
    tokens: int

class BatchResponse(BaseModel):
    results: List[BatchResult]
    total_tokens: int

@router.post("/batch", response_model=BatchResponse)
async def batch_process(request: BatchRequest):
    """Traite plusieurs textes en parallèle."""

    import asyncio

    async def process_one(text: str) -> BatchResult:
        if request.operation == "summarize":
            prompt = f"Résume en une phrase : {text}"
        elif request.operation == "sentiment":
            prompt = f"Sentiment (POSITIVE/NEGATIVE/NEUTRAL) : {text}\nRéponds avec juste le mot."
        else:
            raise HTTPException(status_code=400, detail=f"Unknown operation: {request.operation}")

        messages = [Message(role=Role.USER, content=prompt)]
        result = await llm_service.complete(messages=messages, temperature=0.0)

        return BatchResult(
            text=text[:100] + "..." if len(text) > 100 else text,
            result=result["content"],
            tokens=result["tokens"]
        )

    # Traitement parallèle
    results = await asyncio.gather(*[process_one(t) for t in request.texts])

    return BatchResponse(
        results=results,
        total_tokens=sum(r.tokens for r in results)
    )
