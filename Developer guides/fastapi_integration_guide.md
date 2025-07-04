# ⚡ FastAPI Integration Guide

## 🎯 Learning Outcomes

- Understand how Remo-Server uses FastAPI for its backend
- Learn about app structure, endpoint registration, and dependency management
- See how FastAPI integrates with memory, agents, and user-specific data
- Follow best practices for API design, validation, and troubleshooting
- Know where to find deeper technical details and related guides

---

## 1. Overview

Remo-Server uses [FastAPI](https://fastapi.tiangolo.com/) as its web framework for building a modern, async, and type-safe API backend. FastAPI powers all endpoints, dependency injection, and request validation.

For a high-level system view, see the [Architecture Overview](./architecture_overview.md).

---

## 2. App Structure

- `app.py`: Main FastAPI app, endpoint registration, and dependency setup
- `src/`: All business logic (agents, memory, orchestration, utils)
- `requirements.txt`: FastAPI and all dependencies

---

## 3. Step-by-Step: FastAPI Integration

### 3.1 Endpoint Registration

- Endpoints are defined in `app.py` using FastAPI decorators
- Use Pydantic models for type-safe request/response validation
- Example:

  ```python
  from fastapi import FastAPI, Request
  app = FastAPI()

  @app.get("/health")
  async def health_check():
      return {"status": "healthy"}
  ```

### 3.2 Request/Response Models

- Use Pydantic models for all endpoints
- Example:

  ```python
  from pydantic import BaseModel

  class ChatRequest(BaseModel):
      message: str
      conversation_history: Optional[List[dict]] = []
      user_id: Optional[str] = None
  ```

### 3.3 Dependency Management

- Use FastAPI's dependency injection for shared services (e.g., DynamoDB, Google Calendar)
- Example:

  ```python
  from fastapi import Depends

  def get_dynamodb_service():
      ...

  @app.post("/chat")
  async def chat(request: ChatRequest, db=Depends(get_dynamodb_service)):
      ...
  ```

### 3.4 Memory & User Data Integration

- All endpoints support user-specific data via the `user_id` parameter
- Conversation memory is managed per user (see [Conversation Memory Guide](./conversation_memory_guide.md))
- Data is persisted in DynamoDB (see [DynamoDB Integration Guide](./dynamodb_integration_guide.md))

### 3.5 Interactive API Docs

- FastAPI provides interactive docs at `/docs` (Swagger UI) and `/redoc`
- Try endpoints, see schemas, and test requests live

---

## 4. Best Practices

- Use Pydantic models for all request/response validation
- Document endpoints with clear docstrings
- Use dependency injection for shared resources
- Keep business logic in `src/`, not in `app.py`
- Always include `user_id` for user-specific operations

---

## 5. Troubleshooting

- **Validation errors:** Check Pydantic model definitions and request payloads
- **Dependency issues:** Ensure all dependencies are properly injected and initialized
- **CORS issues:** Configure CORS for frontend-backend communication
- **API errors:** Use `/health` and `/docs` for debugging

---

## 6. Next Steps & Related Guides

- [API Integration Guide](./api_integration_guide.md)
- [Conversation Memory Guide](./conversation_memory_guide.md)
- [DynamoDB Integration Guide](./dynamodb_integration_guide.md)
- [Orchestration & Routing Guide](./orchestration_and_routing.md)
- [User-Specific Implementation Summary](./user_specific_implementation_summary.md)

---

**For more details, see the code in `app.py`, the API docs, and the related guides above.**
