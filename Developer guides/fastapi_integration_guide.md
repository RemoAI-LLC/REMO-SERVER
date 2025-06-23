# FastAPI Integration Guide

This guide covers the FastAPI integration in the Remo AI Assistant backend, including setup, configuration, and deployment.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Setup and Installation](#setup-and-installation)
4. [API Endpoints](#api-endpoints)
5. [Request/Response Models](#requestresponse-models)
6. [Error Handling](#error-handling)
7. [CORS Configuration](#cors-configuration)
8. [Environment Variables](#environment-variables)
9. [Deployment](#deployment)
10. [Testing](#testing)
11. [Monitoring and Logging](#monitoring-and-logging)
12. [Security Considerations](#security-considerations)

## Overview

The Remo backend uses FastAPI to provide a RESTful API interface to the multi-agent AI system. FastAPI was chosen for its:

- **High Performance**: Built on Starlette and Pydantic
- **Automatic Documentation**: OpenAPI/Swagger integration
- **Type Safety**: Full Python type hints support
- **Async Support**: Native async/await support
- **Easy Deployment**: Works with any ASGI server

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   Remo Core     │
│   (React)       │◄──►│   Backend       │◄──►│   (LangGraph)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Agents        │
                       │   • Reminder    │
                       │   • Todo        │
                       └─────────────────┘
```

### Key Components

1. **FastAPI Application** (`app.py`): Main API server
2. **Pydantic Models**: Request/response validation
3. **CORS Middleware**: Cross-origin resource sharing
4. **Error Handlers**: Global exception handling
5. **Health Check**: Service health monitoring

## Setup and Installation

### Prerequisites

```bash
# Python 3.11+
python --version

# Virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Required Dependencies

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
```

### Basic Setup

```python
# app.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(
    title="Remo AI Assistant API",
    description="Multi-agent AI assistant with conversation memory",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## API Endpoints

### Health Check

```python
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Remo AI Assistant API",
        "version": "1.0.0"
    }
```

### Chat Endpoint

```python
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint with conversation memory"""
    try:
        # Process the request through Remo's multi-agent system
        response = await process_chat_request(request)
        return ChatResponse(
            response=response,
            success=True,
            error=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### API Documentation

FastAPI automatically generates interactive documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## Request/Response Models

### Pydantic Models

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class Message(BaseModel):
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")

class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message", max_length=1000)
    conversation_history: List[Message] = Field(
        default=[],
        description="Previous conversation messages"
    )

class ChatResponse(BaseModel):
    response: str = Field(..., description="Assistant's response")
    success: bool = Field(..., description="Request success status")
    error: Optional[str] = Field(None, description="Error message if any")
```

### Model Validation

```python
from pydantic import validator

class ChatRequest(BaseModel):
    message: str
    conversation_history: List[Message] = []

    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        if len(v) > 1000:
            raise ValueError('Message too long (max 1000 characters)')
        return v.strip()

    @validator('conversation_history')
    def validate_history(cls, v):
        for msg in v:
            if msg.role not in ['user', 'assistant']:
                raise ValueError('Invalid message role')
        return v
```

## Error Handling

### Global Exception Handler

```python
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"Internal server error: {str(exc)}",
            "type": "internal_error"
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "type": "http_error"
        }
    )
```

### Custom Exceptions

```python
class RemoAPIException(Exception):
    """Base exception for Remo API"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ValidationError(RemoAPIException):
    """Validation error"""
    def __init__(self, message: str):
        super().__init__(message, 400)

class ServiceUnavailableError(RemoAPIException):
    """Service unavailable error"""
    def __init__(self, message: str):
        super().__init__(message, 503)
```

### Error Response Models

```python
class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
```

## CORS Configuration

### Development Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### Production Configuration

```python
from typing import List

# Load allowed origins from environment
ALLOWED_ORIGINS: List[str] = [
    "https://your-frontend-domain.com",
    "https://www.your-frontend-domain.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## Environment Variables

### Configuration Management

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Configuration
    api_title: str = "Remo AI Assistant API"
    api_version: str = "1.0.0"
    debug: bool = False

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS Configuration
    allowed_origins: List[str] = ["*"]

    # OpenAI Configuration
    openai_api_key: str

    # Optional LangSmith Configuration
    langchain_api_key: Optional[str] = None
    langchain_project: Optional[str] = None
    langchain_tracing_v2: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
```

### Environment File (.env)

```bash
# API Configuration
DEBUG=false
HOST=0.0.0.0
PORT=8000

# CORS Configuration
ALLOWED_ORIGINS=["https://your-frontend-domain.com"]

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# LangSmith Configuration (Optional)
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=remo-ai-assistant
LANGCHAIN_TRACING_V2=true
```

## Deployment

### Local Development

```bash
# Run with uvicorn
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Or run directly
python app.py
```

### Production Deployment

#### Using Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: "3.8"

services:
  remo-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LANGCHAIN_API_KEY=${LANGCHAIN_API_KEY}
    volumes:
      - ./conversations:/app/conversations
      - ./reminders.json:/app/reminders.json
      - ./todos.json:/app/todos.json
```

#### Platform Deployment

**Render:**

```yaml
# render.yaml
services:
  - type: web
    name: remo-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: OPENAI_API_KEY
        sync: false
```

**Railway:**

```json
// railway.json
{
  "build": {
    "builder": "nixpacks"
  },
  "deploy": {
    "startCommand": "uvicorn app:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "on_failure"
  }
}
```

## Testing

### Unit Tests

```python
# test_app.py
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_chat_endpoint():
    response = client.post("/chat", json={
        "message": "Hello",
        "conversation_history": []
    })
    assert response.status_code == 200
    assert "response" in response.json()

def test_chat_endpoint_invalid_message():
    response = client.post("/chat", json={
        "message": "",
        "conversation_history": []
    })
    assert response.status_code == 422
```

### Integration Tests

```python
# test_integration.py
import asyncio
from app import process_chat_request

async def test_chat_integration():
    request = ChatRequest(
        message="Set a reminder for tomorrow 9am",
        conversation_history=[]
    )

    response = await process_chat_request(request)
    assert response is not None
    assert len(response) > 0

# Run tests
if __name__ == "__main__":
    asyncio.run(test_chat_integration())
```

### Load Testing

```python
# load_test.py
import asyncio
import aiohttp
import time

async def load_test():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(100):
            task = session.post(
                "http://localhost:8000/chat",
                json={
                    "message": f"Test message {i}",
                    "conversation_history": []
                }
            )
            tasks.append(task)

        start_time = time.time()
        responses = await asyncio.gather(*tasks)
        end_time = time.time()

        print(f"Processed {len(responses)} requests in {end_time - start_time:.2f} seconds")

asyncio.run(load_test())
```

## Monitoring and Logging

### Logging Configuration

```python
import logging
from fastapi import Request
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )

    return response
```

### Health Monitoring

```python
import psutil
import os

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with system metrics"""
    return {
        "status": "healthy",
        "service": "Remo AI Assistant API",
        "version": "1.0.0",
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        },
        "process": {
            "pid": os.getpid(),
            "memory_mb": psutil.Process().memory_info().rss / 1024 / 1024
        }
    }
```

### Performance Monitoring

```python
from fastapi import Request
import time
from typing import Dict

# Simple performance tracking
request_times: Dict[str, list] = {}

@app.middleware("http")
async def track_performance(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    endpoint = request.url.path

    if endpoint not in request_times:
        request_times[endpoint] = []

    request_times[endpoint].append(process_time)

    # Keep only last 100 requests
    if len(request_times[endpoint]) > 100:
        request_times[endpoint] = request_times[endpoint][-100:]

    return response

@app.get("/metrics")
async def get_metrics():
    """Get performance metrics"""
    metrics = {}
    for endpoint, times in request_times.items():
        if times:
            metrics[endpoint] = {
                "avg_time": sum(times) / len(times),
                "min_time": min(times),
                "max_time": max(times),
                "request_count": len(times)
            }
    return metrics
```

## Security Considerations

### Input Validation

```python
from pydantic import validator
import re

class ChatRequest(BaseModel):
    message: str
    conversation_history: List[Message] = []

    @validator('message')
    def validate_message_content(cls, v):
        # Check for potential injection attacks
        dangerous_patterns = [
            r'<script.*?>',
            r'javascript:',
            r'data:text/html',
            r'vbscript:'
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError('Potentially dangerous content detected')

        return v
```

### Rate Limiting

```python
from fastapi import HTTPException
from collections import defaultdict
import time

# Simple in-memory rate limiting
request_counts = defaultdict(list)
RATE_LIMIT = 60  # requests per minute
RATE_WINDOW = 60  # seconds

def check_rate_limit(client_ip: str):
    now = time.time()

    # Clean old requests
    request_counts[client_ip] = [
        req_time for req_time in request_counts[client_ip]
        if now - req_time < RATE_WINDOW
    ]

    # Check rate limit
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )

    # Add current request
    request_counts[client_ip].append(now)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    check_rate_limit(client_ip)
    return await call_next(request)
```

### API Key Validation

```python
from fastapi import HTTPException, Header
from typing import Optional

async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key if required"""
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required"
        )

    # Add your API key validation logic here
    if x_api_key != "your-secret-api-key":
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

@app.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    api_key: str = Depends(verify_api_key)
):
    # Your chat logic here
    pass
```

### HTTPS and Security Headers

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# Trusted hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["your-domain.com", "www.your-domain.com"]
)

# HTTPS redirect (for production)
if not settings.debug:
    app.add_middleware(HTTPSRedirectMiddleware)

# Security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response
```

## Complete Example

Here's a complete `app.py` example:

```python
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional
import uvicorn
import logging
import time
import os

# Import Remo components
from src.orchestration import SupervisorOrchestrator
from src.memory import ConversationMemoryManager, ConversationContextManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Remo AI Assistant API",
    description="Multi-agent AI assistant with conversation memory",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Message(BaseModel):
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")

class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message", max_length=1000)
    conversation_history: List[Message] = Field(default=[], description="Previous conversation messages")

    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()

class ChatResponse(BaseModel):
    response: str = Field(..., description="Assistant's response")
    success: bool = Field(..., description="Request success status")
    error: Optional[str] = Field(None, description="Error message if any")

# Initialize Remo components
orchestrator = SupervisorOrchestrator(model_name="gpt-4o-mini")
memory_manager = ConversationMemoryManager()
context_manager = ConversationContextManager()

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )

    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Remo AI Assistant API",
        "version": "1.0.0"
    }

# Main chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # Process the request through Remo's multi-agent system
        response = await process_chat_request(request)

        return ChatResponse(
            response=response,
            success=True,
            error=None
        )
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_chat_request(request: ChatRequest) -> str:
    """Process chat request through Remo's multi-agent system"""
    try:
        # Convert conversation history to the format expected by Remo
        messages = []
        for msg in request.conversation_history:
            messages.append({"role": msg.role, "content": msg.content})

        # Add current message
        messages.append({"role": "user", "content": request.message})

        # Process through orchestrator (same logic as remo.py)
        response = orchestrator.process_request(request.message, messages)

        return response
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

This comprehensive FastAPI integration provides a robust, scalable, and secure API for the Remo AI Assistant system.

---

**For more information, see the main README and other developer guides! 🚀**
