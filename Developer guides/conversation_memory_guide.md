# 🧠 Conversation Memory System Guide

This guide explains the conversation memory system implemented in Remo and how to add memory capabilities to new agents.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Components](#components)
4. [How It Works](#how-it-works)
5. [Adding Memory to New Agents](#adding-memory-to-new-agents)
6. [Memory Types](#memory-types)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [Examples](#examples)

## 🎯 Overview

The conversation memory system solves the problem of context loss in multi-turn conversations. Before this implementation, when a user said "set an alarm for tomorrow" followed by "6am", Remo would lose context and not understand that "6am" was completing the alarm request.

### Problem Solved

**Before Memory System:**

```
User: "can you set an alarm for tomorrow?"
Remo: "Of course, I'd be happy to help you with that! Please let me know the exact time you would like to set your alarm for tomorrow."

User: "6am"
Remo: "Good morning! It seems you mentioned a time - 6am. How can I assist you with that?"
```

**After Memory System:**

```
User: "can you set an alarm for tomorrow?"
Remo: "Of course, I'd be happy to help you with that! Please let me know the exact time you would like to set your alarm for tomorrow."

User: "6am"
Remo: "Perfect! I'll set your alarm for tomorrow at 6am."
```

## 🏗️ Architecture

The memory system consists of three main components:

```
src/memory/
├── __init__.py                 # Package exports
├── conversation_memory.py      # LangChain memory integration
├── context_manager.py          # Conversation state management
└── memory_utils.py            # Utility functions
```

### System Integration

```
User Input → Memory Manager → Context Manager → Routing Logic → Agent Selection
     ↓              ↓              ↓              ↓              ↓
Conversation → Context Keywords → Pending Requests → Intent Detection → Response
```

## 🔧 Components

### 1. ConversationMemoryManager

**Purpose**: Manages conversation history using LangChain memory components.

**Key Features**:

- LangChain memory integration (Buffer/Summary)
- Conversation persistence
- Message history management
- Conversation export/import

**Usage**:

```python
from src.memory import ConversationMemoryManager

# Initialize memory manager
memory_manager = ConversationMemoryManager(memory_type="buffer")

# Start conversation
conversation_id = memory_manager.start_conversation()

# Add messages
memory_manager.add_message("user", "Set a reminder for tomorrow")
memory_manager.add_message("assistant", "What time would you like the reminder?")

# Get recent messages
recent_messages = memory_manager.get_recent_messages(5)
```

### 2. ConversationContextManager

**Purpose**: Manages conversation state, pending requests, and routing logic.

**Key Features**:

- Conversation state tracking
- Pending request management
- Context-aware routing
- Agent interaction history

**Usage**:

```python
from src.memory import ConversationContextManager

# Initialize context manager
context_manager = ConversationContextManager()

# Start conversation
context_manager.start_conversation()

# Add pending request
context_manager.add_pending_request(
    request_type="set_reminder",
    agent_name="reminder_agent",
    required_info=["time"],
    context={"description": "meeting"}
)

# Check routing
target_agent = context_manager.should_route_to_agent("6am", ["reminder_agent"])
```

### 3. MemoryUtils

**Purpose**: Utility functions for intent detection and conversation analysis.

**Key Features**:

- Intent detection (reminder, todo)
- Time/task extraction
- Context keyword generation
- Conversation flow analysis

**Usage**:

```python
from src.memory import MemoryUtils

# Detect intent
is_reminder, details = MemoryUtils.detect_reminder_intent("set alarm for tomorrow")

# Extract time
time = MemoryUtils.extract_time_from_message("6am")

# Generate context keywords
keywords = MemoryUtils.get_context_keywords_for_intent("reminder", details)
```

## 🔄 How It Works

### 1. Message Processing Flow

```
1. User sends message
   ↓
2. Message added to memory
   ↓
3. Intent detection (reminder/todo/general)
   ↓
4. Context analysis (pending requests, conversation topic)
   ↓
5. Routing decision (specialized agent vs basic Remo)
   ↓
6. Agent processing with conversation history
   ↓
7. Response generation and memory update
```

### 2. Context-Aware Routing

The system uses multiple strategies to determine routing:

**Explicit Keywords**: Direct mention of "reminder", "todo", etc.
**Intent Detection**: Analysis of message content for specific intents
**Context Keywords**: Keywords from previous conversation
**Pending Requests**: Uncompleted requests waiting for information

### 3. Multi-Turn Conversation Handling

```
Turn 1: User: "Set a reminder for tomorrow"
- Intent: reminder
- Missing: time
- Action: Route to reminder agent, add pending request
- Context keywords: ["reminder", "time", "when"]

Turn 2: User: "6am"
- Context check: Contains time information
- Pending request: reminder_agent waiting for time
- Action: Route to reminder agent with context
- Result: Complete reminder setup
```

## 🚀 Adding Memory to New Agents

### Step 1: Update Agent Tools

Add memory-aware functions to your agent's tools:

```python
# In your_agent_tools.py
from src.memory import MemoryUtils

def your_main_function(param1: str, param2: str = "", context: Dict = None) -> str:
    """
    Main function with memory context support.

    Args:
        param1: Primary parameter
        param2: Secondary parameter
        context: Conversation context from memory system
    """
    # Use context if provided
    if context and context.get("pending_request"):
        # Handle multi-turn conversation
        pass

    # Your implementation here
    return f"✅ Successfully processed: {param1}"
```

### Step 2: Update Agent Class

Modify your agent to handle memory context:

```python
# In your_agent_agent.py
from src.memory import MemoryUtils

class YourAgentAgent:
    def __init__(self, model_name: str = "gpt-4"):
        # ... existing initialization ...

        # Update persona to mention memory capabilities
        self.persona = """You are a [domain] specialist within the Remo AI assistant ecosystem.
Your expertise is in [describe capabilities].

IMPORTANT: You have access to conversation memory and can handle multi-turn conversations.
When a user provides incomplete information:
1. Ask for the missing details
2. Remember the context for follow-up responses
3. Complete the request when all information is provided

Your capabilities:
- [list capabilities]
- Handle multi-turn conversations
- Remember context from previous messages

When handling requests:
1. Check if this is a follow-up to a previous request
2. Use context to complete incomplete requests
3. Provide clear, helpful responses
4. Remember conversation state for future interactions"""
```

### Step 3: Update Main Routing Logic

Add your agent to the memory-aware routing in `remo.py`:

```python
# In remo.py, update the routing logic

# Add your agent's keywords
specialized_keywords.extend([
    "your_keyword1", "your_keyword2", "your_keyword3"
])

# Add intent detection for your agent
is_your_agent_intent, your_agent_details = MemoryUtils.detect_your_agent_intent(user_message)

if is_your_agent_intent:
    should_route_to_specialized = True
    target_agent = "your_agent_name"
    context_manager.set_conversation_topic("your_topic")
    context_manager.set_user_intent("your_action")

    # Add context keywords
    context_keywords = MemoryUtils.get_context_keywords_for_intent("your_agent", your_agent_details)
    context_manager.add_context_keywords(context_keywords)

    # Handle pending requests if needed
    if not your_agent_details.get("has_required_info"):
        context_manager.add_pending_request(
            request_type="your_action",
            agent_name="your_agent_name",
            required_info=["missing_info"],
            context=your_agent_details
        )
```

### Step 4: Add Intent Detection

Create intent detection for your agent in `MemoryUtils`:

```python
# In src/memory/memory_utils.py

# Add your agent's keywords
YOUR_AGENT_KEYWORDS = {
    "action": ["your_action", "create", "add", "make"],
    "object": ["your_object", "item", "thing"],
    "category": ["your_category1", "your_category2"]
}

@classmethod
def detect_your_agent_intent(cls, message: str) -> Tuple[bool, Dict]:
    """
    Detect if a message has your agent-related intent.

    Args:
        message: The user message

    Returns:
        Tuple of (is_your_agent_intent, intent_details)
    """
    message_lower = message.lower()

    # Check for your agent keywords
    has_keywords = any(
        keyword in message_lower
        for keywords in cls.YOUR_AGENT_KEYWORDS.values()
        for keyword in keywords
    )

    if not has_keywords:
        return False, {}

    # Extract details
    intent_details = {
        "action": "your_action",
        "has_required_info": cls.extract_your_info(message) is not None,
        "info": cls.extract_your_info(message),
        "confidence": 0.8
    }

    return True, intent_details

@classmethod
def extract_your_info(cls, message: str) -> Optional[str]:
    """Extract your agent's specific information from message."""
    # Implement extraction logic for your agent
    pass
```

## 📊 Memory Types

### 1. Buffer Memory (Default - Short-term)

**Use Case**: Short to medium conversations
**Pros**:

- Preserves exact conversation history
- Fast access to recent messages
- No information loss
- Perfect for multi-turn conversations

**Cons**:

- Memory usage grows with conversation length
- May hit token limits for long conversations
- Not suitable for very long sessions

**Configuration**:

```python
memory_manager = ConversationMemoryManager(memory_type="buffer")
```

**When to Use**:

- Daily conversations
- Task-oriented interactions
- Multi-turn request completion
- Real-time assistance

### 2. Summary Memory (Long-term)

**Use Case**: Long conversations and persistent context
**Pros**:

- Constant memory usage
- Good for long-term context
- Automatic summarization
- Handles very long conversations

**Cons**:

- May lose specific details
- Requires LLM for summarization
- Slightly slower
- Summaries may not capture all nuances

**Configuration**:

```python
memory_manager = ConversationMemoryManager(
    memory_type="summary",
    max_tokens=2000
)
```

**When to Use**:

- Extended conversations
- Persistent user sessions
- When you need to remember context across days
- Memory-constrained environments

### 3. Vector Memory (Semantic Search)

**Use Case**: Finding relevant information from conversation history
**Pros**:

- Semantic search across conversations
- Can find relevant context from past interactions
- Good for user preference learning
- Scales well with large conversation histories

**Cons**:

- Requires vector database setup
- More complex implementation
- May not preserve exact conversation flow

**Configuration** (Future enhancement):

```python
# This would be a future enhancement
memory_manager = ConversationMemoryManager(
    memory_type="vector",
    vector_store="chroma",  # or "pinecone", "weaviate"
    embedding_model="text-embedding-ada-002"
)
```

**When to Use**:

- Learning user preferences
- Finding similar past interactions
- Building user profiles
- Long-term relationship building

### 4. Entity Memory (Person/Entity Tracking)

**Use Case**: Remembering specific people, places, or entities
**Pros**:

- Tracks specific entities across conversations
- Good for personalization
- Maintains relationship context
- Useful for business applications

**Cons**:

- Limited to entity-based information
- Doesn't preserve full conversation context
- Requires entity extraction

**Configuration** (Future enhancement):

```python
# This would be a future enhancement
memory_manager = ConversationMemoryManager(
    memory_type="entity",
    entity_extraction_model="gpt-4"
)
```

**When to Use**:

- Customer service applications
- Personal assistant scenarios
- When you need to remember people/places
- Business relationship management

## 🔄 Memory Type Selection Strategy

### Current Implementation: Buffer Memory

We chose **Buffer Memory** for Remo because:

1. **Multi-turn Task Completion**: Perfect for scenarios like "set alarm" → "6am"
2. **Immediate Context**: Preserves exact conversation flow
3. **Fast Response**: No summarization overhead
4. **Task-Oriented**: Most personal assistant tasks are short to medium length

### Memory Type Decision Matrix

| Scenario                 | Recommended Memory | Reason                                      |
| ------------------------ | ------------------ | ------------------------------------------- |
| Daily personal assistant | Buffer             | Preserves exact context for task completion |
| Extended conversations   | Summary            | Handles long sessions without memory bloat  |
| User preference learning | Vector             | Finds relevant past interactions            |
| Business applications    | Entity             | Tracks people and relationships             |
| Hybrid approach          | Buffer + Summary   | Short-term precision + long-term context    |

### Switching Memory Types

You can easily switch memory types in our implementation:

```python
# For short conversations (default)
memory_manager = ConversationMemoryManager(memory_type="buffer")

# For long conversations
memory_manager = ConversationMemoryManager(memory_type="summary", max_tokens=2000)

# Auto-switch based on conversation length
if len(memory_manager.get_recent_messages()) > 50:
    # Switch to summary memory for long conversations
    memory_manager = ConversationMemoryManager(memory_type="summary")
```

### Memory Type Comparison

| Feature                       | Buffer     | Summary       | Vector      | Entity         |
| ----------------------------- | ---------- | ------------- | ----------- | -------------- |
| **Context Preservation**      | ✅ Exact   | ⚠️ Summarized | ✅ Semantic | ❌ Entity-only |
| **Memory Usage**              | ❌ Grows   | ✅ Constant   | ✅ Scalable | ✅ Minimal     |
| **Speed**                     | ✅ Fast    | ⚠️ Medium     | ⚠️ Medium   | ✅ Fast        |
| **Multi-turn Support**        | ✅ Perfect | ⚠️ Good       | ❌ Limited  | ❌ Limited     |
| **Long-term Memory**          | ❌ No      | ✅ Yes        | ✅ Yes      | ✅ Yes         |
| **Implementation Complexity** | ✅ Simple  | ✅ Simple     | ❌ Complex  | ⚠️ Medium      |

## 🚀 Future Memory Enhancements

### 1. Hybrid Memory System

Combine multiple memory types for optimal performance:

```python
class HybridMemoryManager:
    def __init__(self):
        self.buffer_memory = ConversationBufferMemory()  # Short-term
        self.summary_memory = ConversationSummaryMemory()  # Long-term
        self.vector_memory = VectorMemory()  # Semantic search

    def get_context(self, query: str):
        # Get recent context from buffer
        recent = self.buffer_memory.get_recent_messages(5)

        # Get relevant history from vector search
        relevant = self.vector_memory.search(query)

        # Get summary for long-term context
        summary = self.summary_memory.get_summary()

        return combine_context(recent, relevant, summary)
```

### 2. Adaptive Memory Selection

Automatically choose the best memory type based on conversation characteristics:

```python
def select_memory_type(conversation_length: int, task_type: str, user_preference: str):
    if conversation_length > 100:
        return "summary"
    elif task_type == "preference_learning":
        return "vector"
    elif task_type == "entity_tracking":
        return "entity"
    else:
        return "buffer"
```

### 3. Memory Persistence and Migration

Save and restore conversations with different memory types:

```python
# Save conversation with current memory type
memory_manager.save_conversation("conversation.json")

# Load with different memory type
new_memory = ConversationMemoryManager(memory_type="summary")
new_memory.load_conversation("conversation.json")
```

## 📈 Memory Performance Monitoring

### Memory Usage Tracking

```python
def monitor_memory_usage(memory_manager):
    """Monitor memory usage and suggest optimizations."""
    message_count = len(memory_manager.get_recent_messages())
    memory_size = estimate_memory_size(memory_manager)

    if message_count > 50:
        print("⚠️  Consider switching to summary memory")
    if memory_size > 10_000_000:  # 10MB
        print("⚠️  Memory usage is high, consider cleanup")

    return {
        "message_count": message_count,
        "memory_size": memory_size,
        "recommendations": get_memory_recommendations(message_count, memory_size)
    }
```

### Memory Optimization Strategies

1. **Regular Cleanup**: Remove expired requests and old messages
2. **Memory Type Switching**: Switch to summary memory for long conversations
3. **Context Compression**: Compress old messages while preserving key information
4. **Selective Retention**: Keep only relevant conversation parts

## 🎯 Best Practices for Memory Selection

### 1. Start with Buffer Memory

For most personal assistant applications, start with buffer memory:

```python
# Default configuration - works for most use cases
memory_manager = ConversationMemoryManager(memory_type="buffer")
```

### 2. Monitor and Adapt

Track memory usage and switch types as needed:

```python
# Monitor conversation length
if len(memory_manager.get_recent_messages()) > 50:
    # Switch to summary memory
    memory_manager = ConversationMemoryManager(memory_type="summary")
```

### 3. Consider Use Case

Choose memory type based on your specific use case:

- **Task Completion**: Buffer memory
- **Long Conversations**: Summary memory
- **User Learning**: Vector memory
- **Entity Tracking**: Entity memory

### 4. Test Performance

Benchmark different memory types with your specific workload:

```python
def benchmark_memory_types(test_conversations):
    results = {}

    for memory_type in ["buffer", "summary", "vector"]:
        start_time = time.time()
        memory_manager = ConversationMemoryManager(memory_type=memory_type)

        for conv in test_conversations:
            memory_manager.add_message("user", conv["user"])
            memory_manager.add_message("assistant", conv["assistant"])

        results[memory_type] = {
            "time": time.time() - start_time,
            "memory_usage": get_memory_usage(memory_manager),
            "context_quality": evaluate_context_quality(memory_manager)
        }

    return results
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Context Not Being Maintained

**Symptoms**: Agent doesn't remember previous conversation
**Causes**:

- Memory not being properly initialized
- Messages not being added to memory
- Context keywords not being set

**Solutions**:

```python
# Check memory initialization
if not memory_manager.conversation_id:
    memory_manager.start_conversation()

# Ensure messages are added
memory_manager.add_message("user", user_input)
memory_manager.add_message("assistant", response)

# Verify context keywords
print(f"Context keywords: {context_manager.context_keywords}")
```

#### 2. Routing to Wrong Agent

**Symptoms**: Messages routed to incorrect agent
**Causes**:

- Overlapping keywords
- Incorrect intent detection
- Missing context keywords

**Solutions**:

```python
# Debug routing logic
print(f"Intent detection: {MemoryUtils.detect_reminder_intent(user_input)}")
print(f"Context routing: {context_manager.should_route_to_agent(user_input, agents)}")
print(f"Context keywords: {context_manager.context_keywords}")
```

#### 3. Memory Leaks

**Symptoms**: High memory usage, slow performance
**Causes**:

- Not cleaning up expired requests
- Too many messages in buffer
- Not switching to summary memory

**Solutions**:

```python
# Regular cleanup
expired_count = context_manager.cleanup_expired_requests()

# Switch to summary memory for long conversations
if len(memory_manager.get_recent_messages()) > 50:
    memory_manager = ConversationMemoryManager(memory_type="summary")
```

#### 4. Pending Requests Not Resolved

**Symptoms**: System keeps asking for same information
**Causes**:

- Request not being resolved after completion
- Incorrect routing logic
- Expired requests not cleaned up

**Solutions**:

```python
# Check pending requests
pending = context_manager.get_pending_request()
if pending:
    print(f"Pending: {pending.request_type} for {pending.agent_name}")

# Resolve after completion
if context_manager.get_pending_request(target_agent):
    context_manager.resolve_pending_request(target_agent)
```

### Debug Commands

Add these debug functions to help troubleshoot:

```python
def debug_memory_state():
    """Print current memory state for debugging."""
    print("=== Memory Debug Info ===")
    print(f"Conversation ID: {memory_manager.conversation_id}")
    print(f"Message count: {len(memory_manager.get_recent_messages())}")
    print(f"Context state: {context_manager.current_state.value}")
    print(f"Active agent: {context_manager.active_agent}")
    print(f"Pending requests: {len(context_manager.pending_requests)}")
    print(f"Context keywords: {context_manager.context_keywords}")
    print("========================")

def debug_conversation_flow(user_input: str):
    """Debug the conversation flow for a specific input."""
    print(f"=== Flow Debug for: '{user_input}' ===")

    # Intent detection
    is_reminder, reminder_details = MemoryUtils.detect_reminder_intent(user_input)
    is_todo, todo_details = MemoryUtils.detect_todo_intent(user_input)

    print(f"Reminder intent: {is_reminder} - {reminder_details}")
    print(f"Todo intent: {is_todo} - {todo_details}")

    # Context routing
    available_agents = ["reminder_agent", "todo_agent"]
    context_agent = context_manager.should_route_to_agent(user_input, available_agents)
    print(f"Context routing: {context_agent}")

    # Time/task extraction
    time = MemoryUtils.extract_time_from_message(user_input)
    task = MemoryUtils.extract_task_from_message(user_input)
    print(f"Extracted time: {time}")
    print(f"Extracted task: {task}")
    print("========================")
```

## 📝 Examples

### Example 1: Complete Reminder Flow

```python
# User: "Set a reminder for tomorrow"
is_reminder, details = MemoryUtils.detect_reminder_intent("Set a reminder for tomorrow")
# Result: True, {"action": "set_reminder", "has_time": False, "has_description": False}

context_manager.add_pending_request(
    request_type="set_reminder",
    agent_name="reminder_agent",
    required_info=["time"],
    context={}
)

# User: "6am"
time = MemoryUtils.extract_time_from_message("6am")
# Result: "6am"

pending = context_manager.get_pending_request("reminder_agent")
# Result: PendingRequest for reminder_agent

# Route to reminder agent with context
response = reminder_agent.process_with_context("6am", pending.context)
# Result: "✅ Reminder set: 'Reminder' for tomorrow 06:00"
```

### Example 2: Todo with Priority

```python
# User: "Add a high priority todo"
is_todo, details = MemoryUtils.detect_todo_intent("Add a high priority todo")
# Result: True, {"action": "add_todo", "has_task": False, "has_priority": True, "priority": "high"}

context_manager.add_pending_request(
    request_type="add_todo",
    agent_name="todo_agent",
    required_info=["task"],
    context={"priority": "high"}
)

# User: "finish project report"
task = MemoryUtils.extract_task_from_message("finish project report")
# Result: "finish project report"

# Complete todo with context
response = todo_agent.process_with_context("finish project report", {"priority": "high"})
# Result: "✅ Todo added: 'finish project report' (Priority: High, Category: General)"
```

### Example 3: Memory Persistence

```python
# Save conversation
conversation_file = memory_manager.save_conversation()
context_file = context_manager.save_context("context.json")

# Later, load conversation
memory_manager.load_conversation(conversation_file)
context_manager.load_context(context_file)

# Continue conversation with full context
response = process_user_input("What was I asking about?")
# Result: "You were setting up a reminder for tomorrow at 6am"
```

## 🎯 Summary

The conversation memory system provides:

1. **Persistent Context**: Remembers conversation state across turns
2. **Intelligent Routing**: Routes messages based on context, not just keywords
3. **Multi-turn Support**: Handles incomplete requests and follow-up responses
4. **Flexible Architecture**: Easy to extend for new agents
5. **Robust Error Handling**: Graceful fallbacks when memory fails

This system transforms Remo from a single-turn assistant to a truly conversational AI that remembers context and provides seamless multi-turn interactions.

---

**Next Steps**:

- Test the memory system with various conversation patterns
- Add memory to your new agents following the guide
- Monitor memory usage and optimize as needed
- Consider adding more sophisticated intent detection for complex scenarios
