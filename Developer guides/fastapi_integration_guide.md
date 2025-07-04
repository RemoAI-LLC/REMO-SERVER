# FastAPI Integration Guide

## 🎯 Learning Outcomes

- Understand how Remo-Server uses FastAPI for its backend
- Learn about the app structure, endpoint registration, and dependency management
- See how FastAPI integrates with memory, agents, and user-specific data
- Know where to find deeper technical details and code references

---

## 1. Overview

Remo-Server uses [FastAPI](https://fastapi.tiangolo.com/) as its web framework for building a modern, async, and type-safe API backend. FastAPI powers all endpoints, dependency injection, and request validation.

---

## 2. App Structure

- **`app.py`**: Main FastAPI app, endpoint registration, and dependency setup
- **`src/`**: All business logic (agents, memory, orchestration, utils)
- **`requirements.txt`**: FastAPI and all dependencies

---

## 3. Endpoint Registration

Endpoints are defined directly in `app.py` using FastAPI decorators:

```python
from fastapi import FastAPI, Request
app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/chat")
async def chat(request: ChatRequest):
    # ...
```

- **Request models**: Use Pydantic for type-safe request/response validation
- **Dependency injection**: Use FastAPI's dependency system for shared resources

---

## 4. Key Endpoints

- `/chat`: Main chat endpoint (see [API Integration Guide](./api_integration_guide.md))
- `/user/{user_id}/data`: User data management
- `/auth/google/login` and `/auth/google/callback`: Google OAuth
- `/calendar/create-event`: Calendar integration
- `/feedback/submit`: Feedback collection

See [app.py](../app.py) for the full list and implementation details.

---

## 5. Request/Response Models

All endpoints use Pydantic models for validation and documentation. Example:

```python
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[dict]] = []
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    success: bool
    timestamp: str
    error: Optional[str] = None
    user_id: Optional[str] = None
```

---

## 6. Dependency Management

- Use FastAPI's dependency injection for shared services (e.g., DynamoDB, Google Calendar)
- Example:

```python
from fastapi import Depends

def get_dynamodb_service():
    # Return a singleton or per-request instance
    ...

@app.post("/chat")
async def chat(request: ChatRequest, db=Depends(get_dynamodb_service)):
    ...
```

---

## 7. Memory & User Data Integration

- All endpoints support user-specific data via the `user_id` parameter
- Conversation memory is managed per user (see [Conversation Memory Guide](./conversation_memory_guide.md))
- Data is persisted in DynamoDB (see [DynamoDB Integration Guide](./dynamodb_integration_guide.md))

---

## 8. Interactive API Docs

- FastAPI provides interactive docs at `/docs` (Swagger UI) and `/redoc`
- Try endpoints, see schemas, and test requests live

---

## 9. Best Practices

- Use Pydantic models for all request/response validation
- Document endpoints with clear docstrings
- Use dependency injection for shared resources
- Keep business logic in `src/`, not in `app.py`

---

## 10. Next Steps

- [API Integration Guide](./api_integration_guide.md)
- [Conversation Memory Guide](./conversation_memory_guide.md)
- [DynamoDB Integration Guide](./dynamodb_integration_guide.md)
- [Orchestration & Routing Guide](./orchestration_and_routing.md)

---

**For more details, see the FastAPI docs and the Remo-Server source code.**
