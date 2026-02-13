# Guide de Test Postman - Day 5 AI Backend

## Installation et Démarrage

### 1. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 2. Configurer votre clé API OpenAI
Ouvrez le fichier `.env` et remplacez `your-openai-api-key-here` par votre vraie clé API OpenAI :
```env
OPENAI_API_KEY=sk-...votre-clé-ici...
```

### 3. Lancer le serveur
```bash
uvicorn app.main:app --reload --port 8000
```

Vous devriez voir :
```
🚀 Starting AI Backend...
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 4. Tester la santé de l'API
Ouvrez votre navigateur : http://localhost:8000/health

Vous devriez voir : `{"status": "healthy", "version": "1.0.0"}`

---

## Tests avec Postman

### 📖 Documentation Interactive
Visitez http://localhost:8000/docs pour voir la documentation Swagger interactive générée automatiquement par FastAPI.

---

## Endpoints à Tester

### 1️⃣ Health Check
**GET** `http://localhost:8000/health`

✅ **Réponse attendue:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

### 2️⃣ Chat Simple (Sans historique)
**POST** `http://localhost:8000/api/chat/`

**Headers:**
- `Content-Type: application/json`

**Body (raw JSON):**
```json
{
  "message": "Qu'est-ce que FastAPI ?",
  "temperature": 0.7
}
```

✅ **Réponse attendue:**
```json
{
  "response": "FastAPI est un framework web moderne...",
  "conversation_id": "uuid-généré-automatiquement",
  "tokens_used": 150,
  "model": "gpt-4-turbo",
  "created_at": "2026-01-23T..."
}
```

**🎯 Concept clé:** Gestion des requêtes/réponses avec Pydantic models

---

### 3️⃣ Chat avec Historique de Conversation
**POST** `http://localhost:8000/api/chat/`

**Body:**
```json
{
  "message": "Donne-moi plus de détails",
  "conversation_id": "COLLER-ICI-LE-conversation_id-DU-MESSAGE-PRECEDENT",
  "temperature": 0.7
}
```

✅ **Résultat:** L'IA se souviendra du contexte de la conversation précédente.

**🎯 Concept clé:** Gestion d'état des conversations en mémoire

---

### 4️⃣ Chat avec System Prompt Personnalisé
**POST** `http://localhost:8000/api/chat/`

**Body:**
```json
{
  "message": "Bonjour",
  "system_prompt": "Tu es un pirate qui parle comme Jack Sparrow",
  "temperature": 0.9
}
```

✅ **Résultat:** L'IA répondra en mode pirate !

**🎯 Concept clé:** Personnalisation du comportement via system prompts

---

### 5️⃣ Chat en Streaming (SSE)
**POST** `http://localhost:8000/api/chat/stream`

**Body:**
```json
{
  "message": "Écris un court poème sur le code",
  "temperature": 0.9
}
```

✅ **Réponse attendue:** Flux de données en temps réel au format SSE
```
data: {"content": "Dans"}

data: {"content": " les"}

data: {"content": " lignes"}

...

data: [DONE]
```

**🎯 Concept clé:** Streaming responses avec Server-Sent Events

---

### 6️⃣ Analyse de Document
**POST** `http://localhost:8000/api/analysis/document`

**Headers:**
- `Content-Type: application/x-www-form-urlencoded`

**Body (x-www-form-urlencoded):**
- Key: `text`
- Value: `This is an amazing product! I absolutely love the quality and the customer service was outstanding. Highly recommended to everyone!`

✅ **Réponse attendue:**
```json
{
  "summary": "Avis très positif sur un produit...",
  "sentiment": {
    "sentiment": "POSITIVE",
    "confidence": 0.95,
    "explanation": "Utilisation de mots très positifs..."
  },
  "entities": [
    {
      "text": "customer service",
      "type": "ORG",
      "start": 65,
      "end": 81
    }
  ],
  "key_points": [
    "Produit de qualité",
    "Excellent service client",
    "Fortement recommandé"
  ],
  "tokens_used": 200
}
```

**🎯 Concept clé:** Structured outputs - Parser des réponses JSON du LLM

---

### 7️⃣ Classification de Texte
**POST** `http://localhost:8000/api/analysis/classify`

**Headers:**
- `Content-Type: application/json`

**Body (raw JSON):**
```json
{
  "text": "Je n'arrive pas à réinitialiser mon mot de passe",
  "categories": ["Support Technique", "Facturation", "Question Générale", "Demande de Fonctionnalité"]
}
```

✅ **Réponse attendue:**
```json
{
  "category": "Support Technique",
  "confidence": 0.92,
  "reasoning": "La question concerne un problème technique avec la réinitialisation du mot de passe"
}
```

**🎯 Concept clé:** Classification intelligente avec LLM

---

### 8️⃣ Traitement par Batch (Parallèle)
**POST** `http://localhost:8000/api/analysis/batch`

**Body:**
```json
{
  "texts": [
    "Ce produit est incroyable !",
    "Expérience terrible, très déçu.",
    "C'est correct, rien de spécial.",
    "Le meilleur achat de ma vie !"
  ],
  "operation": "sentiment"
}
```

✅ **Réponse attendue:**
```json
{
  "results": [
    {
      "text": "Ce produit est incroyable !",
      "result": "POSITIVE",
      "tokens": 25
    },
    {
      "text": "Expérience terrible, très déçu.",
      "result": "NEGATIVE",
      "tokens": 28
    },
    {
      "text": "C'est correct, rien de spécial.",
      "result": "NEUTRAL",
      "tokens": 27
    },
    {
      "text": "Le meilleur achat de ma vie !",
      "result": "POSITIVE",
      "tokens": 26
    }
  ],
  "total_tokens": 106
}
```

**Essayez aussi avec `"operation": "summarize"`**

**🎯 Concept clé:** Traitement asynchrone parallèle avec asyncio.gather

---

### 9️⃣ Test du Rate Limiting
**Objectif:** Envoyer 101 requêtes rapidement pour déclencher le rate limiter

Dans Postman, utilisez le **Collection Runner** :
1. Créez une collection avec n'importe quel endpoint
2. Lancez le Runner avec 101 itérations
3. Observez les réponses

✅ **Résultat attendu après 100 requêtes:**
```json
{
  "detail": "Rate limit exceeded. Please wait before making more requests."
}
```
**Status Code:** `429 Too Many Requests`

**🎯 Concept clé:** Middleware de rate limiting pour protéger l'API

---

### 🔟 Test de l'Authentification (Optionnel)
L'authentification est implémentée mais pas activée par défaut. Pour tester:

**Headers:**
- `X-API-Key: demo-key-123`

**Clés valides:**
- `demo-key-123`
- `prod-key-456`

**🎯 Concept clé:** API Key authentication avec FastAPI Security

---

## 🎓 Concepts Clés à Retenir

### 1. **Architecture FastAPI**
- ✅ Séparation claire: routers / services / models / middleware
- ✅ Dependency injection avec `Depends`
- ✅ Validation automatique avec Pydantic

### 2. **LLM Service Abstraction**
- ✅ Wrapper autour d'AsyncOpenAI
- ✅ Facilite le changement de provider
- ✅ Singleton pattern pour réutilisation

### 3. **Gestion d'État**
- ✅ ConversationService en mémoire
- ✅ TTL automatique (60 minutes)
- ✅ Cleanup automatique toutes les 5 minutes

### 4. **Middleware Stack**
- ✅ CORS pour frontend
- ✅ Logging structuré (JSON)
- ✅ Rate limiting par IP
- ✅ Auth avec API keys

### 5. **Streaming**
- ✅ Server-Sent Events (SSE)
- ✅ AsyncIterator pour réponses en temps réel
- ✅ Format: `data: {json}\n\n`

### 6. **Structured Outputs**
- ✅ Prompts avec instructions JSON
- ✅ Parsing et validation
- ✅ Error handling robuste

### 7. **Traitement Parallèle**
- ✅ `asyncio.gather()` pour batch
- ✅ Efficacité avec concurrent processing
- ✅ Gestion d'erreurs individuelles

---

## 🐛 Dépannage

### Erreur: "openai_api_key not found"
➡️ **Solution:** Vérifiez que votre `.env` contient `OPENAI_API_KEY=sk-...`

### Erreur: "Module 'openai' not found"
➡️ **Solution:** `pip install -r requirements.txt`

### Le serveur ne démarre pas
➡️ **Solution:** Vérifiez que le port 8000 n'est pas déjà utilisé

### Rate limiting trop strict
➡️ **Solution:** Modifiez `RATE_LIMIT_REQUESTS` dans `.env`

### Les conversations ne persistent pas
➡️ **C'est normal !** Le système utilise la mémoire (in-memory storage). Les conversations sont perdues au redémarrage. C'est intentionnel pour l'apprentissage.

---

## 📊 Architecture Résumée

```
Client (Postman)
    ↓
FastAPI (main.py)
    ↓
Middleware Stack
    ├─ CORS
    ├─ Logging
    └─ Rate Limiting
    ↓
Routers
    ├─ /api/chat (chat.py)
    └─ /api/analysis (analysis.py)
    ↓
Services
    ├─ LLMService (llm_service.py)
    └─ ConversationService (conversation.py)
    ↓
OpenAI API
```

---

## ✅ Checklist de Validation

Avant de passer au Jour 6, assurez-vous de pouvoir :

- [ ] Créer une API FastAPI avec endpoints chat
- [ ] Gérer l'état des conversations
- [ ] Implémenter le streaming (SSE)
- [ ] Ajouter du rate limiting
- [ ] Structurer un projet backend IA proprement
- [ ] Parser les réponses JSON des LLMs
- [ ] Gérer les erreurs gracieusement

---

## 🚀 Prochaines Étapes

Maintenant que vous maîtrisez le backend, vous pouvez :
1. Ajouter une base de données PostgreSQL (remplacer in-memory)
2. Implémenter l'authentification JWT
3. Ajouter Redis pour le cache
4. Créer un frontend React
5. Déployer sur Railway/Render/Vercel

**Bon apprentissage ! 🎓**
