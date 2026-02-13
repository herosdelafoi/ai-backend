# AI Backend - FastAPI + OpenAI

Backend API pour interagir avec des LLMs (OpenAI GPT-4), incluant chat, streaming, analyse de documents, classification et traitement par batch.

## Architecture

```
Client (Postman/Frontend)
    |
FastAPI (app/main.py)
    |
Middleware (CORS, Logging, Rate Limiting)
    |
Routers
    |- /api/chat       -> Chat simple + Streaming SSE
    |- /api/analysis   -> Analyse, Classification, Batch
    |
Services
    |- LLMService            -> Wrapper AsyncOpenAI
    |- ConversationService   -> Historique en memoire (TTL 60min)
    |
OpenAI API (GPT-4-turbo)
```

## Installation

```bash
# Cloner le repo
git clone <repo-url>
cd ai-backend

# Environnement virtuel
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Dependances
pip install -r requirements.txt

# Configuration
cp .env.example .env
# Editez .env et ajoutez votre cle API OpenAI

# Lancer le serveur
uvicorn app.main:app --reload --port 8000
```

Le serveur demarre sur http://localhost:8000

## Endpoints

| Methode | URL | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/api/chat/` | Chat simple |
| POST | `/api/chat/stream` | Chat en streaming (SSE) |
| POST | `/api/analysis/document` | Analyse de document |
| POST | `/api/analysis/classify` | Classification de texte |
| POST | `/api/analysis/batch` | Traitement par batch |

## Documentation

- Swagger UI : http://localhost:8000/docs
- ReDoc : http://localhost:8000/redoc
- Guide de test Postman : voir [POSTMAN_TESTING_GUIDE.md](POSTMAN_TESTING_GUIDE.md)

## Configuration

Voir [.env.example](.env.example) pour toutes les variables disponibles. La seule variable requise est `OPENAI_API_KEY`.

## Structure du projet

```
app/
  main.py              # Point d'entree FastAPI
  config.py            # Configuration (pydantic-settings)
  routers/             # Endpoints (chat, analysis)
  models/              # Schemas Pydantic + SQLAlchemy
  services/            # LLM wrapper + gestion conversations
  middleware/          # Auth, logging, rate limiting
  utils/               # Templates de prompts
```
