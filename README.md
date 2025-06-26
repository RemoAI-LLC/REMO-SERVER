# Remo - Your Personal AI Assistant

"Remo: A personal AI Assistant that can be hired by every human on the planet. Personal assistants are not just for the rich anymore."

Now powered by multi-agent orchestration with specialized agents for reminders and todo management.
Enhanced with conversation memory for seamless multi-turn interactions.
**NEW**: User-specific data isolation with DynamoDB integration for secure, personalized experiences.

## 🚀 Quick Start

### Backend (API) Only

```bash
cd REMO-SERVER
source venv/bin/activate
python app.py
# Server runs on http://localhost:8000
```

### Frontend + Backend

```bash
# Backend
cd REMO-SERVER
source venv/bin/activate
python app.py

# Frontend (in new terminal)
cd REMO-APP
npm run dev:web
# Frontend runs on http://localhost:5173
```

## 🌟 Features

### 🤖 Multi-Agent Orchestration

- **Reminder Agent**: Manages reminders, alerts, and scheduled tasks
- **Todo Agent**: Handles todo lists, task organization, and project management
- **Supervisor Orchestrator**: Routes requests to appropriate specialists

### 🧠 Advanced Memory System

- **Conversation Memory**: Remembers context across interactions
- **Context Management**: Tracks conversation topics and user intent
- **Memory Persistence**: Saves conversations for future reference
- **User-Specific Data**: Isolated conversation history per user
- **Multi-Turn Support**: Handles incomplete requests and follow-up responses
- **Intent Detection**: Automatically detects reminder and todo intents
- **Time Recognition**: Recognizes time expressions like "6am", "2pm", "tomorrow"
- **Memory Types**: Supports buffer (short-term) and summary (long-term) memory
- **Adaptive Memory**: Can switch between memory types based on conversation length
- **Conversation Continuity**: Maintains context across multiple interactions
- **Clarification Detection**: Recognizes when users are correcting routing mistakes

### 🎯 Intelligent Routing

- **Intent Detection**: Automatically detects reminder and todo requests
- **Context-Aware Routing**: Routes based on conversation history
- **Fallback Handling**: Graceful degradation if agents fail
- **Direct Listing**: Fast, accurate listing of todos and reminders

### 💾 Data Persistence & Security

- **DynamoDB Integration**: Scalable, serverless database storage
- **User Data Isolation**: Complete separation of user data using Privy user IDs
- **Automatic Cleanup**: TTL-based data expiration for old conversations
- **Secure Storage**: Encrypted data storage with proper access controls

### 🌐 API Integration

- **FastAPI Backend**: RESTful API with automatic documentation
- **CORS Support**: Ready for frontend integration
- **Environment Variables**: Secure credential management
- **User Authentication**: Privy integration for secure user management

## 📋 Prerequisites

- Python 3.11+
- OpenAI API Key
- Node.js 18+ (for frontend)
- AWS DynamoDB (for data persistence)
- Privy (for user authentication)

## 🛠️ Installation

### Backend Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd REMO-SERVER

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Frontend Setup

```bash
cd REMO-APP
npm install
```

### Database Setup

```bash
# Set up DynamoDB tables
cd REMO-SERVER
python scripts/setup_dynamodb.py
```

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# AWS DynamoDB (for data persistence)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1

# Optional (for LangSmith tracing)
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=your_project_name
LANGCHAIN_TRACING_V2=true
```

### Frontend Configuration

```bash
# In REMO-APP/.env
VITE_API_URL=http://localhost:8000  # For development
VITE_API_URL=https://your-backend-url.com  # For production
```

## 🚀 Deployment

### Backend Deployment (Render)

1. Connect your GitHub repository to Render
2. Select the `REMO-SERVER` directory
3. Set environment variables in Render dashboard
4. Deploy!

### Frontend Deployment (Vercel)

1. Connect your GitHub repository to Vercel
2. Select the `REMO-APP` directory
3. Set build command: `npm run build:web`
4. Set environment variables
5. Deploy!

## 📚 API Documentation

### Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-backend-url.com`

### Endpoints

#### Health Check

```bash
GET /health
```

#### Chat Endpoint

```bash
POST /chat
Content-Type: application/json

{
  "message": "Set a reminder for tomorrow 9am",
  "user_id": "user_123",
  "conversation_history": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help you?"}
  ]
}
```

### API Examples

#### Basic Chat

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "who are you?", "user_id": "user_123", "conversation_history": []}'
```

#### Set Reminder

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "set a reminder for painting tomorrow at 9am", "user_id": "user_123", "conversation_history": []}'
```

#### Add Todo

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "add buy groceries to my todo list", "user_id": "user_123", "conversation_history": []}'
```

#### List Todos

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "show me all my todos", "user_id": "user_123", "conversation_history": []}'
```

#### List Reminders

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "show me all my reminders", "user_id": "user_123", "conversation_history": []}'
```

#### With Conversation History

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "yes, add description: paint the living room",
    "user_id": "user_123",
    "conversation_history": [
      {"role": "user", "content": "set a reminder for painting tomorrow at 9am"},
      {"role": "assistant", "content": "Could you please confirm if you would like to add a description?"}
    ]
  }'
```

### Interactive API Docs

Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

## 🏗️ Architecture

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
                              │
                              ▼
                       ┌─────────────────┐
                       │   DynamoDB      │
                       │   • User Data   │
                       │   • Memory      │
                       │   • Context     │
                       └─────────────────┘
```

## 🧠 How Agents Use Conversation Memory

The conversation memory system is the backbone of Remo's intelligent agent interactions. Here's how agents leverage memory to provide context-aware, personalized experiences:

### 1. **Memory Initialization & User Isolation**

Each user gets their own isolated memory managers that store conversation history separately:

```python
# User-specific memory managers
memory_manager = ConversationMemoryManager(memory_type="buffer", user_id=user_id)
context_manager = ConversationContextManager(user_id=user_id)
```

**Benefits**: Complete data isolation ensures privacy and personalized experiences.

### 2. **Memory Storage During Conversations**

Every interaction is automatically stored for future reference:

```python
# Store user messages and agent responses
memory_manager.add_message("user", user_message)
memory_manager.add_message("assistant", agent_response)

# Automatically saved to DynamoDB with user isolation
```

**Benefits**: Persistent memory across sessions and devices.

### 3. **Context-Aware Agent Routing**

Agents receive conversation history to understand context:

```python
# Get recent conversation history
recent_messages = memory_manager.get_recent_messages(5)
conversation_history_for_agent = []

# Pass context to agents for better responses
agent_response = todo_agent.process(user_message, conversation_history_for_agent)
```

**Benefits**: Agents can reference previous conversations and provide more relevant responses.

### 4. **Multi-Turn Conversation Support**

Agents handle incomplete requests by remembering context:

```python
# Example conversation flow:
# User: "Add a todo for groceries"
# Agent: "What priority would you like to set?"
# User: "High priority"
# Agent: "Added 'groceries' with high priority to your todo list"

# The agent remembers the original request and completes it
```

**Benefits**: Natural conversation flow without repeating information.

### 5. **Intent Detection with Memory Context**

Better intent recognition using conversation history:

```python
# Context-aware intent detection
if conversation_context.get('active_agent') == 'todo_agent':
    # More likely to be a todo intent if already in todo conversation
    return detect_todo_intent(message, context)
```

**Benefits**: More accurate routing and response generation.

### 6. **State Management Across Sessions**

Track conversation state and active agents:

```python
# Remember which agent is active
context_manager.set_active_agent("todo_agent")

# Track pending requests
context_manager.add_pending_request("add_todo", "todo_agent", ["priority"])
```

**Benefits**: Seamless continuation of conversations across sessions.

### 7. **Agent Response with Memory Context**

Agents provide personalized responses using memory:

```python
# Agent can reference previous conversations
def process(self, user_message: str, conversation_history: List[Dict] = None):
    if conversation_history:
        # "You mentioned groceries earlier, I'll add that to your todo list"
        # "Based on our previous conversation about your project..."
```

**Benefits**: More natural and contextual interactions.

### 8. **Memory Types for Different Use Cases**

```python
# Buffer Memory (Default) - For daily conversations
memory_manager = ConversationMemoryManager(memory_type="buffer")

# Summary Memory - For long conversations
memory_manager = ConversationMemoryManager(memory_type="summary", max_tokens=2000)
```

**Benefits**: Optimized memory usage based on conversation length.

### 9. **Persistent Memory Across Sessions**

```python
# Load previous conversation context
context_data = dynamodb_service.load_conversation_context(user_id)
if context_data:
    # Restore conversation state
    context_manager.current_state = context_data.get('current_state')
    context_manager.active_agent = context_data.get('active_agent')
```

**Benefits**: Users can continue conversations even after logging out and back in.

### 10. **Real-World Memory Usage Examples**

#### Example 1: Todo Management with Context
```
User: "Add a todo for groceries"
Agent: "I'll add that to your todo list. What priority would you like to set?"
User: "High priority"
Agent: "Added 'groceries' with high priority to your todo list. Is there anything specific you need to buy?"
User: "Yes, milk and bread"
Agent: "Updated your grocery todo to include milk and bread. Is there anything else?"
```

#### Example 2: Reminder Setting with Follow-up
```
User: "Set a reminder for my doctor's appointment"
Agent: "I'll set a reminder for your doctor's appointment. When is it scheduled for?"
User: "Tomorrow at 2pm"
Agent: "Reminder set for your doctor's appointment tomorrow at 2pm. Would you like me to add any notes?"
User: "Yes, bring insurance card"
Agent: "Added note: bring insurance card. Your reminder is all set!"
```

#### Example 3: Cross-Session Continuity
```
Session 1:
User: "I need to organize my project tasks"
Agent: "I can help you organize your project tasks. What project are you working on?"
User: "Website redesign"
Agent: "Great! Let me help you organize your website redesign project."

Session 2 (later):
User: "What was I working on?"
Agent: "You were organizing tasks for your website redesign project. Would you like me to show you your current project todos?"
```

### 11. **Memory System Components**

#### Conversation Memory Manager
- **Purpose**: Stores and retrieves conversation messages
- **Features**: Buffer and summary memory types
- **Storage**: DynamoDB with user isolation
- **Usage**: All agent interactions

#### Context Manager
- **Purpose**: Tracks conversation state and routing
- **Features**: Active agent tracking, pending requests
- **Storage**: DynamoDB with user isolation
- **Usage**: Intelligent routing decisions

#### Memory Utils
- **Purpose**: Intent detection and context analysis
- **Features**: Natural language processing, keyword extraction
- **Usage**: Routing and response generation

### 12. **Memory Benefits for Agents**

1. **Context Continuity**: Agents remember what was discussed and build on previous conversations
2. **Personalized Responses**: Each user's conversation history is isolated and personalized
3. **Multi-Turn Support**: Agents handle incomplete requests and follow-up questions naturally
4. **Intent Accuracy**: Better intent detection using conversation context
5. **State Management**: Track which agent is active and what requests are pending
6. **Persistence**: Conversations continue across sessions and devices
7. **Efficiency**: No need to repeat information or re-explain context
8. **User Experience**: Natural, human-like conversation flow

### 13. **Memory Integration Points**

#### In Agent Processing
```python
def process(self, user_message: str, conversation_history: List[Dict] = None):
    # Use conversation history for context
    messages = []
    if conversation_history:
        messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_message})
    
    # Agent processes with full context
    result = self.agent.invoke({"messages": messages})
```

#### In Routing Logic
```python
# Use memory for intelligent routing
context_agent = context_manager.should_route_to_agent(user_message, available_agents)
if context_agent:
    # Route to agent based on conversation context
    return route_to_agent(context_agent, user_message, conversation_history)
```

#### In Intent Detection
```python
# Use context for better intent recognition
is_todo_intent = MemoryUtils.detect_todo_intent(message, conversation_context)
is_reminder_intent = MemoryUtils.detect_reminder_intent(message, conversation_context)
```

The conversation memory system makes Remo's agents much more intelligent and user-friendly by providing them with the context they need to have natural, continuous conversations with users. This creates a truly personalized AI assistant experience that remembers and builds upon previous interactions.

## 🔧 Development

### Running in Development

```bash
# Backend
cd REMO-SERVER
source venv/bin/activate
python app.py

# Frontend
cd REMO-APP
npm run dev:web
```

### Building for Production

```bash
# Backend
cd REMO-SERVER
pip install -r requirements.txt

# Frontend
cd REMO-APP
npm run build:web
```

## 📁 Project Structure

```
REMO-SERVER/
├── app.py                 # FastAPI server
├── requirements.txt      # Python dependencies
├── .env                 # Environment variables
├── src/
│   ├── agents/          # Specialized AI agents
│   │   ├── reminders/   # Reminder management
│   │   └── todo/        # Todo management
│   ├── memory/          # Conversation memory
│   ├── orchestration/   # Multi-agent coordination
│   └── utils/           # Utility functions & DynamoDB
└── Developer guides/    # Detailed documentation

REMO-APP/
├── src/
│   ├── pages/           # React components
│   ├── components/      # Reusable components
│   └── routes/          # Application routing
├── package.json         # Node.js dependencies
└── Developer guides/    # Frontend documentation
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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:

1. Check the Developer guides folder
2. Review the API documentation at `/docs`
3. Open an issue on GitHub

---

**Remo - Making personal AI assistance accessible to everyone! 🤖✨**
