# 🧠 Conversation Memory System Guide

## 🎯 Learning Outcomes

- Understand how Remo-Server manages conversation memory and context
- Learn about buffer, summary, and future memory types
- See how memory integrates with agents, orchestration, and user data
- Know how to extend or customize the memory system
- Find code references and links to related guides

---

## 1. Overview

Remo-Server uses a modular conversation memory system to enable multi-turn, context-aware AI interactions. Memory is essential for:

- Multi-turn task completion (e.g., "set a reminder for tomorrow" → "6am")
- Contextual reasoning and follow-ups
- User-specific, persistent experiences

---

## 2. Architecture & Components

- **`src/memory/conversation_memory.py`**: Main memory manager (buffer, summary, future types)
- **`src/memory/context_manager.py`**: Tracks conversation state, pending requests, and routing context
- **`src/memory/memory_utils.py`**: Intent detection, context keyword extraction, and analysis

### System Flow

```
User Message → Memory Manager → Context Manager → Orchestration → Agent(s) → Memory Update
```

---

## 3. Memory Types

### A. Buffer Memory (Default)

- Stores the exact sequence of recent messages
- Best for short- to medium-length conversations
- Fast, preserves full context

### B. Summary Memory (Optional)

- Summarizes long conversations to save space
- Used when buffer memory exceeds token limits
- Can be enabled/configured in `ConversationMemoryManager`

### C. Future Types (Vector, Entity, Hybrid)

- Planned for advanced use cases (semantic search, entity tracking, etc.)

---

## 4. How Memory Works

- **Frontend**: Sends the full conversation history with each `/chat` request ([API Guide](./api_integration_guide.md))
- **Backend**: Updates memory after each turn, storing both user and assistant messages
- **User-specific**: Memory is isolated per user (see [DynamoDB Guide](./dynamodb_integration_guide.md))
- **Context Manager**: Tracks pending requests, conversation topics, and agent routing

---

## 5. Code Examples

### Initialize and Use Memory

```python
from src.memory import ConversationMemoryManager

memory = ConversationMemoryManager(memory_type="buffer", user_id=user_id)
memory.add_message("user", "Set a reminder for tomorrow")
memory.add_message("assistant", "What time?")
recent = memory.get_recent_messages(5)
```

### Context Management

```python
from src.memory import ConversationContextManager

context = ConversationContextManager(user_id=user_id)
context.add_pending_request("set_reminder", "reminder_agent", ["time"])
```

---

## 6. Best Practices

- Always send the full conversation history for best results
- Use buffer memory for most assistant tasks
- Switch to summary memory for long conversations
- Use user_id for all memory operations
- Monitor memory usage and optimize as needed

---

## 7. Extending the Memory System

- Add new memory types in `conversation_memory.py`
- Extend intent/context logic in `memory_utils.py`
- Integrate with new agents via the context manager

---

## 8. Related Guides & Next Steps

- [Conversation Memory API Guide](./conversation_memory_api_guide.md)
- [API Integration Guide](./api_integration_guide.md)
- [DynamoDB Integration Guide](./dynamodb_integration_guide.md)
- [Creating New Agents](./creating_new_agents.md)
- [Orchestration & Routing Guide](./orchestration_and_routing.md)

---

**For more details, see the memory source code in `src/memory/` and the API/agent guides.**
