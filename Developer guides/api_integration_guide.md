# Remo API Integration Guide

## 🎯 Learning Outcomes

- Understand how to interact with the Remo-Server API
- Learn about available endpoints, request/response formats, and authentication
- See how conversation memory and user-specific data are handled in the API
- Know where to find deeper technical details and code references

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base URL](#base-url)
4. [Endpoints](#endpoints)
5. [Request/Response Format](#requestresponse-format)
6. [Examples by Language](#examples-by-language)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)
9. [Rate Limiting](#rate-limiting)
10. [WebSocket Support](#websocket-support)

---

## Overview

The Remo API provides access to a sophisticated AI assistant with multi-agent orchestration, conversation memory, and specialized capabilities for reminders, todos, and email management.

### Key Features

- **Multi-Agent Orchestration**: Automatic routing to specialized agents
- **Conversation Memory**: Context-aware responses across multiple turns ([Conversation Memory Guide](./conversation_memory_guide.md))
- **Intent Detection**: Automatic detection of reminder, todo, and email requests
- **User-Specific Data**: All data is isolated per user ([User Data Isolation Guide](./user_specific_implementation_summary.md))
- **Real-time Processing**: Fast response times with streaming support (future)

---

## Authentication

- The API uses environment-based authentication. Ensure your backend has the required API keys in `.env`:
  - `OPENAI_API_KEY`, `LANGCHAIN_API_KEY`, etc.
- No user-level API keys are required for frontend integration; user identity is managed via Privy ID or similar.

---

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://remo-server.onrender.com`

---

## Endpoints

### Health Check

```http
GET /health
```

### Chat Endpoint

```http
POST /chat
Content-Type: application/json
```

**Request Body:**

```json
{
  "message": "string",
  "conversation_history": [{ "role": "user|assistant", "content": "string" }],
  "user_id": "string (optional)"
}
```

**Response:**

```json
{
  "response": "string",
  "success": true,
  "timestamp": "ISO8601 string",
  "error": null,
  "user_id": "string (optional)"
}
```

### User Data Endpoints

- `/user/{user_id}/data` (GET, DELETE)
- `/user/{user_id}/preferences` (GET, POST)
- `/auth/google/login`, `/auth/google/callback`, `/auth/status/{user_id}`
- `/calendar/create-event` (POST)
- `/feedback/submit`, `/feedback/summary/{user_id}`

See [API source code](../app.py) for full endpoint list and details.

---

## Request/Response Format

- Always send the full conversation history for best results ([Conversation Memory API Guide](./conversation_memory_api_guide.md)).
- User ID should be included for user-specific memory and data isolation.

---

## Examples by Language

(Examples are up to date with the current API. See guide for code snippets in JS, Python, cURL, etc.)

---

## Error Handling

- Standard HTTP status codes and error messages are returned.
- See [Best Practices](#best-practices) for error handling patterns.

---

## Best Practices

- Store and send both user and assistant messages in your frontend state.
- Truncate or summarize long histories if needed (see [Conversation Memory Guide](./conversation_memory_guide.md)).
- Use user_id for all requests to enable user-specific memory and data.

---

## Rate Limiting

- 60 requests per minute per IP (default)
- Rate limit headers are included in responses

---

## WebSocket Support

- Real-time streaming and bi-directional communication are planned for future releases.

---

## 📚 Additional Resources

- [Conversation Memory Guide](./conversation_memory_guide.md)
- [User Data Isolation Guide](./user_specific_implementation_summary.md)
- [FastAPI Integration Guide](./fastapi_integration_guide.md)
- [Remo-Server Source Code](../src/)

---

**For more details, see the main API integration guide and the memory source code in `src/memory/`.**
