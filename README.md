# Remo - Your Personal AI Assistant

"Remo: A personal AI Assistant that can be hired by every human on the planet. Personal assistants are not just for the rich anymore."

**Now powered by multi-agent orchestration with specialized agents for enhanced capabilities and conversation memory for seamless multi-turn interactions!**

## Why Remo?

In today's fast-paced world, people are overwhelmed with various tasks requiring different skills and information overload. And that's where Personal assistants can make our work easy!

But traditionally, personal assistants have been a luxury available only to the wealthy or executives. The average person cannot afford a full-time human personal assistant because they are costly. And that is why we have introduced Remo.

## Project Overview

Remo is built using advanced AI orchestration technologies:

- **LangChain**: Provides the core LLM integration and chat model functionality
- **LangGraph**: Enables building stateful, multi-agent applications with a graph-based architecture
- **LangSmith**: Offers tracing, monitoring, and debugging capabilities for the LLM application
- **LangGraph Supervisor**: Powers multi-agent orchestration and coordination
- **Conversation Memory**: Maintains context across multi-turn conversations

Remo is a human-like personal assistant designed to be accessible to everyone. It combines the power of LangChain, LangGraph, and LangSmith with specialized AI agents and conversation memory to create an intelligent, responsive, and capable AI assistant that can help with various tasks.

## 🚀 New: Multi-Agent Orchestration with Conversation Memory

Remo now features a sophisticated multi-agent system that coordinates specialized AI agents for different tasks, enhanced with conversation memory for seamless multi-turn interactions:

### **Available Specialists:**

1. **Reminder Agent** 📅

   - Manages reminders, alerts, and scheduled tasks
   - Sets precise time-based notifications
   - Organizes and tracks reminder history
   - Updates and manages existing reminders
   - **NEW**: Remembers context across conversation turns

2. **Todo Agent** ✅
   - Handles todo lists and task organization
   - Manages project priorities and categories
   - Tracks task completion and progress
   - Provides productivity insights and recommendations
   - **NEW**: Maintains conversation context for incomplete requests

### **Conversation Memory Features:**

- **🧠 Persistent Context**: Remembers conversation state across multiple turns
- **🎯 Intelligent Routing**: Routes messages based on context, not just keywords
- **🔄 Multi-turn Support**: Handles incomplete requests and follow-up responses
- **📝 Intent Detection**: Automatically detects reminder and todo intents
- **⏰ Time Recognition**: Recognizes time expressions like "6am", "2pm", "tomorrow"
- **💾 Conversation Persistence**: Saves and loads conversation history
- **📊 Memory Types**: Supports buffer (short-term) and summary (long-term) memory
- **🔍 Context-Aware Responses**: Uses conversation history for better responses
- **⏱️ Request Timeout Management**: Automatically cleans up expired requests
- **🎛️ Adaptive Memory**: Can switch between memory types based on conversation length

### **How It Works:**

- **Supervisor Pattern**: Remo acts as a supervisor that routes requests to specialized agents
- **Intelligent Routing**: Automatically detects task types and routes to appropriate specialists
- **Context Awareness**: Maintains conversation context for seamless multi-turn interactions
- **Seamless Integration**: Maintains Remo's personality while leveraging specialized expertise
- **Coordinated Responses**: Combines responses when multiple agents are involved

## Remo's Mission & Personality

Remo is designed to be a genuine, human-like personal assistant that understands and empathizes with people's daily needs and challenges. Key characteristics include:

1. Human-Like Interaction:

   - Natural and conversational communication
   - Empathy and understanding
   - Appropriate humor and personality
   - Warm, friendly tone while maintaining professionalism
   - Emotional intelligence in responses
   - **NEW**: Perfect memory of conversation context

2. Proactive Assistance:

   - Anticipates needs before they're expressed
   - Offers helpful suggestions proactively
   - Remembers user preferences and patterns
   - Follows up on previous conversations
   - Takes initiative in solving problems
   - **NEW**: Remembers incomplete requests and asks for missing information

3. Professional yet Approachable:

   - Balances professionalism with friendliness
   - Shows respect and consideration
   - Maintains appropriate boundaries
   - Demonstrates genuine interest in helping
   - Exhibits patience and understanding

4. Task Management & Organization:

   - Daily schedule and task management
   - Work organization and prioritization
   - Reminder and follow-up management
   - Activity coordination
   - Deadline tracking

5. Problem Solving & Resourcefulness:
   - Creative problem-solving
   - Efficient solution finding
   - Adaptability to different situations
   - Continuous learning
   - Practical, actionable advice

## Enhanced Capabilities

Remo can assist with:

- Email and communication management
- Scheduling and calendar management
- Task and project organization
- Research and information gathering
- Job application assistance
- Food ordering and delivery coordination
- Workflow automation
- Personal and professional task management
- Reminder and follow-up management
- Basic decision support
- **NEW**: Specialized reminder management through Reminder Agent
- **NEW**: Advanced todo and task organization through Todo Agent
- **NEW**: Seamless multi-turn conversations with memory

## Prerequisites

Before starting, ensure you have:

- Access to an LLM that supports tool-calling features (OpenAI, Anthropic, or Google Gemini)
- Python 3.8+ installed
- Required API keys for your chosen LLM provider

## Core Components Explained

### 1. LangChain

LangChain is a framework for developing applications powered by language models. In Remo:

```python
from langchain.chat_models import init_chat_model

# Initialize the chat model
llm = init_chat_model("openai:gpt-4")

# Example of using the model
response = llm.invoke([{"role": "user", "content": "Hello!"}])
```

Key features:

- Model abstraction and management
- Message formatting and handling
- Integration with various LLM providers

### 2. LangGraph

LangGraph is a library for building stateful, multi-agent applications. It uses a graph-based architecture where:

```python
from langgraph.graph import StateGraph, START

# Define the state structure
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Create the graph
graph_builder = StateGraph(State)

# Add a node (function that processes messages)
def remo(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

# Add the node to the graph
graph_builder.add_node("remo", remo)

# Connect the entry point to the remo node
graph_builder.add_edge(START, "remo")
```

Key concepts:

- **StateGraph**: A state machine that manages the flow of data
- **Nodes**: Functions that process data and return updates to the state
- **Edges**: Define how data flows between nodes
- **State**: The current state of the conversation, including message history

### 3. LangSmith

LangSmith provides tracing and monitoring capabilities:

```python
import os
from langsmith import Client

# Set up LangSmith
os.environ["LANGCHAIN_API_KEY"] = "your_api_key"
os.environ["LANGCHAIN_PROJECT"] = "your_project"

# Traces are automatically created when running the graph
graph.stream({"messages": [{"role": "user", "content": "Hello!"}]})
```

Features:

- Real-time tracing of LLM calls
- Performance monitoring
- Debugging tools
- Trace visualization

### 4. Multi-Agent Orchestration

The new multi-agent system uses LangGraph Supervisor for coordination:

```python
from src.orchestration import SupervisorOrchestrator

# Initialize the orchestrator
orchestrator = SupervisorOrchestrator(model_name="gpt-4")

# Process requests through specialized agents
response = orchestrator.process_request("Set a reminder for tomorrow's meeting")
```

Key features:

- **Supervisor Pattern**: Centralized coordination of specialized agents
- **Intelligent Routing**: Automatic detection and routing of task types
- **Seamless Integration**: Maintains conversation flow across agents
- **Specialized Expertise**: Each agent has focused capabilities

### 5. Conversation Memory System

The conversation memory system maintains context across multi-turn conversations:

```python
from src.memory import ConversationMemoryManager, ConversationContextManager

# Initialize memory system
memory_manager = ConversationMemoryManager(memory_type="buffer")
context_manager = ConversationContextManager()

# Start conversation
memory_manager.start_conversation()
context_manager.start_conversation()

# Add messages to memory
memory_manager.add_message("user", "Set a reminder for tomorrow")
memory_manager.add_message("assistant", "What time would you like the reminder?")

# Check context for routing
target_agent = context_manager.should_route_to_agent("6am", ["reminder_agent"])
```

Key features:

- **Persistent Context**: Remembers conversation state across turns
- **Intent Detection**: Automatically detects reminder and todo intents
- **Context-Aware Routing**: Routes messages based on conversation context
- **Pending Request Management**: Tracks incomplete requests
- **Conversation Persistence**: Saves and loads conversation history

#### Memory Types

Remo supports different memory types for different use cases:

**Buffer Memory (Default - Short-term)**:

```python
# Perfect for multi-turn task completion
memory_manager = ConversationMemoryManager(memory_type="buffer")
```

- ✅ Preserves exact conversation history
- ✅ Fast access to recent messages
- ✅ Perfect for "set alarm" → "6am" scenarios
- ❌ Memory usage grows with conversation length

**Summary Memory (Long-term)**:

```python
# For extended conversations
memory_manager = ConversationMemoryManager(memory_type="summary", max_tokens=2000)
```

- ✅ Constant memory usage
- ✅ Handles very long conversations
- ✅ Good for persistent user sessions
- ⚠️ May lose specific details in summarization

**Auto-switching Memory**:

```python
# Automatically switch to summary memory for long conversations
if len(memory_manager.get_recent_messages()) > 50:
    memory_manager = ConversationMemoryManager(memory_type="summary")
```

#### Memory Configuration

Configure memory based on your needs:

```python
# For daily personal assistant use (recommended)
memory_manager = ConversationMemoryManager(memory_type="buffer")

# For extended conversations
memory_manager = ConversationMemoryManager(
    memory_type="summary",
    max_tokens=2000
)

# Monitor memory usage
message_count = len(memory_manager.get_recent_messages())
if message_count > 50:
    print("Consider switching to summary memory")
```

## Project Structure

```
Lang-Agent/
├── .env                    # Environment variables
├── requirements.txt        # Project dependencies
├── remo.py                # Main Remo implementation with multi-agent integration
├── visualize_graph.py     # Graph visualization utilities
├── src/                   # Multi-agent system source code
│   ├── agents/           # Specialized AI agents
│   │   ├── reminders/    # Reminder management agent
│   │   │   ├── reminder_agent.py
│   │   │   └── reminder_tools.py
│   │   └── todo/         # Todo management agent
│   │       ├── todo_agent.py
│   │       └── todo_tools.py
│   ├── orchestration/    # Multi-agent coordination
│   │   └── supervisor.py # Supervisor orchestrator
│   ├── memory/          # Conversation memory system
│   │   ├── conversation_memory.py
│   │   ├── context_manager.py
│   │   └── memory_utils.py
│   └── utils/           # Shared utilities
│       └── state.py     # State management
├── conversations/        # Saved conversation files
├── reminders.json        # Reminder storage (auto-generated)
├── todos.json           # Todo storage (auto-generated)
└── README.md            # This documentation
```

## Setup

1. Create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Unix/macOS
# OR
venv\Scripts\activate     # On Windows

# To deactivate the virtual environment when you're done
deactivate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your API keys:

```
OPENAI_API_KEY=your_openai_api_key_here
```

4. Run Remo:

```bash
python remo.py
```

## Usage Examples

### Basic Interaction

```bash
$ python remo.py

=== Remo - Your Advanced AI Assistant ===
Initializing Remo with multi-agent orchestration and conversation memory...

🤖 Remo is ready to assist you!
🔄 Now powered by specialized agents for reminders and todo management
🧠 Enhanced with conversation memory for seamless multi-turn interactions
🆔 Conversation ID: conv_20240115_143022

📋 Available Specialists:
   • Reminder Agent: Manages reminders, alerts, and scheduled tasks
   • Todo Agent: Manages todo lists, tasks, and project organization

How can I help you today?

You: Set a reminder for my dentist appointment tomorrow at 2 PM
Remo: I'll help you set that reminder through our specialized reminder system.

✅ Reminder set: 'Dentist appointment' for 2024-01-16 14:00

You: Add "buy groceries" to my todo list
Remo: I'll add that to your todo list through our task management specialist.

✅ Todo added: 'buy groceries' (Priority: Medium, Category: General)
```

### Multi-Turn Conversation with Memory

```bash
You: Set a reminder for my team meeting tomorrow
Remo: I'll help you set that reminder. What time would you like the reminder for your team meeting tomorrow?

You: 10am
Remo: Perfect! I'll set your reminder for the team meeting tomorrow at 10am.

✅ Reminder set: 'Team meeting' for 2024-01-16 10:00

You: Also add "prepare presentation slides" to my high priority todos
Remo: I'll add that high priority task to your todo list.

✅ Todo added: 'prepare presentation slides' (Priority: High, Category: General)
```

### Context-Aware Interactions

```bash
You: Set an alarm for tomorrow
Remo: I'll help you set that alarm. What time would you like the alarm for tomorrow?

You: 6am
Remo: Perfect! I'll set your alarm for tomorrow at 6am.

✅ Reminder set: 'Alarm' for 2024-01-16 06:00

You: Actually make it 7am
Remo: I'll update your alarm to 7am tomorrow.

✅ Reminder updated: 'Alarm' for 2024-01-16 07:00
```

## Agent Capabilities

### Reminder Agent

**Tools Available:**

- `set_reminder(title, datetime_str, description)`: Create new reminders
- `list_reminders(show_completed)`: View all reminders
- `update_reminder(reminder_id, title, datetime_str, description)`: Modify existing reminders
- `delete_reminder(reminder_id)`: Remove reminders
- `mark_reminder_complete(reminder_id)`: Mark reminders as completed

**Example Commands:**

- "Set a reminder for my doctor's appointment next Friday at 3 PM"
- "Show me all my active reminders"
- "Update my meeting reminder to 2 PM instead of 1 PM"
- "Mark my dentist reminder as completed"

**Memory Features:**

- Remembers incomplete reminder requests
- Recognizes time expressions in follow-up messages
- Maintains context across conversation turns
- Handles multi-turn reminder setup

### Todo Agent

**Tools Available:**

- `add_todo(title, description, priority, category)`: Create new todo items
- `list_todos(category, show_completed, priority)`: View todos with filtering
- `mark_todo_complete(todo_id)`: Mark todos as completed
- `update_todo(todo_id, title, description, priority, category)`: Modify todos
- `delete_todo(todo_id)`: Remove todos
- `prioritize_todos()`: Get priority overview and recommendations

**Example Commands:**

- "Add 'finish project report' to my high priority work todos"
- "Show me all my personal todos"
- "Mark the grocery shopping todo as complete"
- "Give me a priority overview of my tasks"

**Memory Features:**

- Remembers incomplete todo requests
- Recognizes task descriptions in follow-up messages
- Maintains priority and category context
- Handles multi-turn todo creation

## Architecture Details

### Multi-Agent Flow with Memory

1. **User Input** → `remo.py`
2. **Memory Processing** → Add message to conversation memory
3. **Intent Detection** → Analyze message for reminder/todo intent
4. **Context Analysis** → Check for pending requests and conversation context
5. **Agent Routing** → Route to appropriate specialized agent(s) with context
6. **Specialized Processing** → Agent handles the request with focused expertise
7. **Memory Update** → Update conversation memory with response
8. **Response Aggregation** → Supervisor combines responses if multiple agents involved
9. **User Output** → Returns coordinated response maintaining Remo's personality

### Memory System Components

- **ConversationMemoryManager**: Manages conversation history using LangChain memory
- **ConversationContextManager**: Tracks conversation state and pending requests
- **MemoryUtils**: Provides intent detection and conversation analysis utilities

### State Management

- **Persistent Storage**: Reminders and todos are stored in JSON files
- **Conversation History**: Maintained across agent interactions with memory system
- **Context Preservation**: User preferences, pending requests, and conversation topics are remembered
- **Conversation Persistence**: Conversations can be saved and loaded

### Error Handling

- **Graceful Fallbacks**: If specialized agents fail, falls back to basic Remo
- **Memory Error Recovery**: Continues operation even if memory components fail
- **User Feedback**: Clear error messages and recovery suggestions
- **Context Recovery**: Maintains conversation context even after errors

## Development

### Adding New Agents

To add a new specialized agent:

1. Create a new agent directory in `src/agents/`
2. Implement agent class with `get_agent()`, `get_name()`, and `get_description()` methods
3. Add agent tools in a separate `*_tools.py` file
4. Update `SupervisorOrchestrator` to include the new agent
5. Update routing logic in `remo.py`
6. **NEW**: Add memory integration following the [Conversation Memory Guide](./Developer%20guides/conversation_memory_guide.md)

### Adding Memory to Agents

To add conversation memory to a new agent:

1. Follow the [Conversation Memory Guide](./Developer%20guides/conversation_memory_guide.md)
2. Add intent detection in `MemoryUtils`
3. Update routing logic to include memory-aware routing
4. Add context keywords and pending request handling
5. Test multi-turn conversations

### Customizing Agent Behavior

Each agent can be customized by:

- Modifying the persona in the agent class
- Adding new tools to the agent's toolset
- Adjusting temperature and other LLM parameters
- Customizing the supervisor's routing logic
- **NEW**: Configuring memory behavior and context keywords

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- Open an issue on GitHub
- Check the documentation
- Review the LangGraph and LangChain documentation
- **NEW**: Consult the [Conversation Memory Guide](./Developer%20guides/conversation_memory_guide.md) for memory-related questions

---

**Remo: Making personal assistance accessible to everyone, one conversation at a time.** 🤖✨🧠
