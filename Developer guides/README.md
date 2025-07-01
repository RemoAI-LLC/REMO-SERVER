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

**UPDATED**: Comprehensive guide to the enhanced orchestration system with intent detection, context management, and intelligent routing.

### [Intent Detection & Routing Improvements](./intent_detection_and_routing_improvements.md)

**NEW**: Detailed documentation of the recent improvements to intent detection and routing that resolved todo/reminder confusion issues and listing functionality.

### [Conversation Memory System](./conversation_memory_guide.md)

**NEW**: Comprehensive guide to the conversation memory system, including how to add memory to new agents and troubleshoot memory issues.

### [DynamoDB Integration Guide](./dynamodb_integration_guide.md)

**NEW**: Complete guide to the DynamoDB integration for user-specific data storage, including table setup, CRUD operations, and data isolation.

### [Enhanced DynamoDB Guide](./enhanced_dynamodb_guide.md)

**NEW**: Advanced DynamoDB features including TTL, GSIs, and optimized table structures for better performance and data management.

### [User-Specific Implementation Summary](./user_specific_implementation_summary.md)

**NEW**: Summary of all user-specific functionality improvements including data isolation, DynamoDB integration, and listing fixes.

### [Email Assistant Guide](./email_assistant_guide.md)

**NEW**: Comprehensive guide to the email assistant implementation following the LangChain agents-from-scratch pattern, including email composition, triage, and management.

### [Email Evaluation Guide](./email_evaluation_guide.md)

**NEW**: Comprehensive evaluation system for the email assistant agent, including LLM-as-a-judge evaluation, test datasets, and performance analysis.

### [Voice Chat Guide](./voice_chat_guide.md)

Guide for implementing voice chat functionality and handling voice input/output.

### [FastAPI Integration Guide](./fastapi_integration_guide.md)

Guide for integrating with FastAPI and handling API requests/responses.

### [Deployment Guide](./deployment_guide.md)

Guide for deploying the Remo system to production environments.

### [Visualization & Debugging](./visualization_and_debugging.md)

How to use the graph visualization tool, LangSmith tracing, and best practices for debugging multi-agent workflows.

## 🎯 Quick Start

1. **Read the [Architecture Overview](./architecture_overview.md)** to understand the big picture
2. **Follow [Building from Scratch](./building_from_scratch.md)** to set up your environment
3. **Learn about recent improvements in [Intent Detection & Routing Improvements](./intent_detection_and_routing_improvements.md)**
4. **Understand user-specific features in [User-Specific Implementation Summary](./user_specific_implementation_summary.md)**
5. **Set up database in [DynamoDB Integration Guide](./dynamodb_integration_guide.md)**
6. **Add or modify agents using [Creating New Agents](./creating_new_agents.md)**
7. **Learn about orchestration in [Agent Orchestration & Routing](./orchestration_and_routing.md)**
8. **Understand memory in [Conversation Memory System](./conversation_memory_guide.md)**
9. **Visualize and debug with [Visualization & Debugging](./visualization_and_debugging.md)**

## 🚀 Example Use Cases

- **Email Agent**: Send, read, and organize emails ✅ **IMPLEMENTED**
- **Email Evaluation**: Comprehensive evaluation system with LLM-as-a-judge ✅ **IMPLEMENTED**
- **Reminder Agent**: Set reminders and manage alerts ✅ **IMPLEMENTED**
- **Todo Agent**: Manage tasks and project organization ✅ **IMPLEMENTED**
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
- **User-Specific Memory**: Isolated conversation history per user

## 🎯 Intent Detection & Routing Features

The enhanced intent detection and routing system provides:

- **Natural Language Support**: Handles variations like "to do's", "todos", "todo list"
- **Clarification Detection**: Recognizes when users are correcting routing mistakes
- **False Positive Prevention**: Prioritizes todo keywords over reminder keywords
- **Task Extraction**: Intelligently extracts tasks from natural language
- **Context-Aware Routing**: Maintains conversation context for continuity
- **Priority-Based Routing**: Intent Detection > Context Routing > General Response
- **Direct Agent Routing**: Faster response times by avoiding supervisor overhead
- **Accurate Listing**: Direct routing for listing requests to avoid LLM confusion

### Intent Detection Quick Reference

| Intent Type | Keywords | Patterns | Example |
|-------------|----------|----------|---------|
| **Todo** | "todo", "task", "to do", "to do's" | `add.*to.*to do` | "add groceries to my to do's" |
| **Reminder** | "remind", "reminder", "alarm" | `remind me to.*at` | "remind me to call mom at 6pm" |
| **Email** | "email", "mail", "compose", "send" | `compose.*email\|send.*email` | "compose an email to john@example.com" |
| **Listing** | "show", "list", "all", "display" | `show.*todos\|list.*todos` | "show me all my todos" |
| **Clarification** | "i asked", "i want", "add to do" | `i asked.*to do` | "i asked you to add the to do" |

### Quick Intent Testing

```python
from src.memory.memory_utils import MemoryUtils

# Test intent detection
is_todo, todo_details = MemoryUtils.detect_todo_intent("add groceries to my to do's")
is_reminder, reminder_details = MemoryUtils.detect_reminder_intent("remind me to call mom")
is_email, email_details = MemoryUtils.detect_email_intent("compose an email to john@example.com")
is_listing, listing_type = MemoryUtils.detect_listing_request("show me all my todos")

# Extract tasks
task = MemoryUtils.extract_task_from_message("add going to groceries to my to do's")
# Returns: "going to groceries"
```

## 💾 Database Features

The DynamoDB integration provides:

- **User Data Isolation**: Complete separation of user data using Privy user IDs
- **Scalable Storage**: Serverless database that scales automatically
- **Automatic Cleanup**: TTL-based expiration for old conversations
- **Efficient Querying**: GSIs for fast user-specific data retrieval
- **CRUD Operations**: Comprehensive create, read, update, delete operations
- **Data Types**: Support for todos, reminders, user details, and conversation memory

### Database Quick Reference

```python
from src.utils.dynamodb_service import DynamoDBService

# Initialize service
db = DynamoDBService()

# User-specific operations
todos = db.get_user_todos("user_123")
reminders = db.get_user_reminders("user_123")
conversations = db.get_user_conversations("user_123")

# Add items
db.add_todo("user_123", "Buy groceries", "Get milk and bread")
db.add_reminder("user_123", "Call mom", "2024-01-15T18:00:00")
```

## 🆕 Recent Improvements

### User-Specific Functionality
- **Data Isolation**: Each user's data is completely separated using Privy user IDs
- **Personalized Experience**: Reminders, todos, and conversation history are user-specific
- **Secure Storage**: All user data is stored securely in DynamoDB with proper access controls

### Enhanced Listing Functionality
- **Accurate Listing**: Todo and reminder listings now show only the requested items
- **Direct Routing**: Fast, deterministic listing bypasses LLM confusion
- **Improved Intent Detection**: Better recognition of listing requests

### Database Integration
- **DynamoDB Service**: Comprehensive CRUD operations for all data types
- **Automatic Cleanup**: TTL-based expiration for old conversations
- **Efficient Querying**: GSIs for fast user-specific data retrieval

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
