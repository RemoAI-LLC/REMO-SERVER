# 🏗️ Remo-Server Architecture Overview

## 🎯 Learning Outcomes

- Understand the high-level architecture and design of Remo-Server
- Identify all major components and their responsibilities
- See how agents, memory, orchestration, and user data isolation fit together
- Know where to find deeper technical details in other guides

---

## 1. System Design & Big Picture

Remo-Server is a multi-agent, context-aware AI backend built with FastAPI, LangChain, LangGraph, and DynamoDB. It powers the Remo AI Assistant, enabling:

- Multi-turn, context-aware conversations
- Specialized agents (reminders, todos, email, etc.)
- User-specific data isolation and persistence
- Extensible, modular architecture

### High-Level Flow

```
User (Privy ID) → Frontend (React) → FastAPI Backend → Orchestration & Memory → Specialized Agents → DynamoDB
```

---

## 2. Technology Stack

- **Python 3.11+**: Core language
- **FastAPI**: REST API backend ([FastAPI Integration Guide](./fastapi_integration_guide.md))
- **LangChain & LangGraph**: LLM orchestration, agent creation, memory ([Conversation Memory Guide](./conversation_memory_guide.md))
- **DynamoDB (boto3)**: User-specific data storage ([DynamoDB Integration Guide](./dynamodb_integration_guide.md))
- **React**: Frontend (see REMO-APP)
- **Privy**: User authentication (frontend)

---

## 3. Core Components

### A. API Layer

- **app.py**: FastAPI server, main entrypoint
- **Endpoints**: `/chat`, `/health`, user data endpoints ([API Integration Guide](./api_integration_guide.md))

### B. Orchestration & Routing

- **Supervisor Orchestrator**: Coordinates all agents ([Orchestration & Routing Guide](./orchestration_and_routing.md))
- **Intent Detection**: Advanced pattern matching ([Intent Detection & Routing Improvements](./intent_detection_and_routing_improvements.md))
- **Context Management**: Maintains conversation state ([Conversation Memory Guide](./conversation_memory_guide.md))

### C. Agents

- **Specialized Agents**: Reminders, Todos, Email, etc. ([Creating New Agents](./creating_new_agents.md))
- **Extensible**: Add new agents easily

### D. Memory System

- **ConversationMemoryManager**: Stores conversation history (buffer/summary)
- **ContextManager**: Tracks pending requests, context, and routing
- **User-specific**: Each user has isolated memory ([User-Specific Implementation Summary](./user_specific_implementation_summary.md))

### E. Data Layer

- **DynamoDB**: Stores all user data (reminders, todos, memory, preferences)
- **Service Layer**: `src/utils/dynamodb_service.py`

---

## 4. Data Flow Example

```
1. User sends message from frontend (with Privy user ID)
2. FastAPI backend receives `/chat` request
3. Conversation history and user ID are passed to orchestrator
4. Intent detection & context management decide routing
5. Specialized agent processes the request
6. Response is generated and memory is updated
7. Data is persisted in DynamoDB under the user's ID
8. Response is sent back to frontend
```

---

## 5. Extensibility & Best Practices

- **Add new agents**: Follow [Creating New Agents](./creating_new_agents.md)
- **Update memory logic**: See [Conversation Memory Guide](./conversation_memory_guide.md)
- **User data isolation**: See [DynamoDB Integration Guide](./dynamodb_integration_guide.md)
- **Debug & visualize**: Use [Visualization & Debugging](./visualization_and_debugging.md)

---

## 6. Next Steps

- [Building from Scratch](./building_from_scratch.md)
- [API Integration Guide](./api_integration_guide.md)
- [Conversation Memory Guide](./conversation_memory_guide.md)
- [DynamoDB Integration Guide](./dynamodb_integration_guide.md)
- [Orchestration & Routing Guide](./orchestration_and_routing.md)

---

**This guide is always the starting point. For details, follow the links to each specialized guide.**
