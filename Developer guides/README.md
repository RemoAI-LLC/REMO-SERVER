# 📚 Remo Development Guides

This folder contains comprehensive guides for developing and extending the Remo multi-agent system.

## 📖 Available Guides

### [Architecture Overview](./architecture_overview.md)

A high-level explanation of Remo's architecture, including agent structure, orchestration, and how the system fits together.

### [Building from Scratch](./building_from_scratch.md)

Step-by-step instructions for setting up the project, installing dependencies, and understanding the codebase layout.

### [Creating New Agents](./creating_new_agents.md)

A complete step-by-step guide for adding new specialized agents to the Remo multi-agent orchestration system.

### [Agent Orchestration & Routing](./orchestration_and_routing.md)

Details on how the supervisor orchestrator works, how requests are routed, and how to extend orchestration logic.

### [Conversation Memory System](./conversation_memory_guide.md)

**NEW**: Comprehensive guide to the conversation memory system, including how to add memory to new agents and troubleshoot memory issues.

### [Visualization & Debugging](./visualization_and_debugging.md)

How to use the graph visualization tool, LangSmith tracing, and best practices for debugging multi-agent workflows.

## 🎯 Quick Start

1. **Read the [Architecture Overview](./architecture_overview.md)** to understand the big picture
2. **Follow [Building from Scratch](./building_from_scratch.md)** to set up your environment
3. **Add or modify agents using [Creating New Agents](./creating_new_agents.md)**
4. **Learn about orchestration in [Agent Orchestration & Routing](./orchestration_and_routing.md)**
5. **Understand memory in [Conversation Memory System](./conversation_memory_guide.md)**
6. **Visualize and debug with [Visualization & Debugging](./visualization_and_debugging.md)**

## 🚀 Example Use Cases

- **Email Agent**: Send, read, and organize emails
- **Calendar Agent**: Schedule meetings and manage events
- **Research Agent**: Search and summarize information
- **Shopping Agent**: Create lists and find products
- **Health Agent**: Track fitness and wellness goals

## 🧠 Memory System Features

The conversation memory system provides:

- **Persistent Context**: Remembers conversation state across turns
- **Intelligent Routing**: Routes messages based on context, not just keywords
- **Multi-turn Support**: Handles incomplete requests and follow-up responses
- **Intent Detection**: Automatically detects reminder and todo intents
- **Time Recognition**: Recognizes time expressions like "6am", "2pm", "tomorrow"
- **Conversation Persistence**: Saves and loads conversation history
- **Memory Types**: Supports buffer (short-term) and summary (long-term) memory
- **Adaptive Memory**: Can switch between memory types based on conversation length

### Memory Type Quick Reference

| Memory Type          | Use Case                                  | Pros                                               | Cons                              |
| -------------------- | ----------------------------------------- | -------------------------------------------------- | --------------------------------- |
| **Buffer** (Default) | Daily conversations, task completion      | Exact context, fast, perfect for multi-turn        | Memory grows with conversation    |
| **Summary**          | Extended conversations, long sessions     | Constant memory usage, handles long conversations  | May lose details, slower          |
| **Vector** (Future)  | User preference learning, semantic search | Semantic search, scales well                       | Complex setup, requires vector DB |
| **Entity** (Future)  | Person/entity tracking, business apps     | Tracks specific entities, good for personalization | Limited context, entity-only      |

### Quick Memory Configuration

```python
# Default - perfect for most use cases
memory_manager = ConversationMemoryManager(memory_type="buffer")

# For long conversations
memory_manager = ConversationMemoryManager(memory_type="summary", max_tokens=2000)

# Auto-switch for long conversations
if len(memory_manager.get_recent_messages()) > 50:
    memory_manager = ConversationMemoryManager(memory_type="summary")
```

## 📝 Contributing

When adding new guides:

1. Follow the established format and structure
2. Include code examples and best practices
3. Add troubleshooting sections
4. Update this README with new guide information

---

**Need help?** Check the main [README.md](../README.md) for general project information.
