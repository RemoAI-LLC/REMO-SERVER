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

## 🗄️ DynamoDB Table: `remo-users`

The `remo-users` table is the foundation of Remo's user management system, storing user profile information and authentication details with complete data isolation.

### 📊 **Table Structure**

```python
# remo-users Table Schema
{
    'privy_id': 'HASH',        # Partition Key (String) - Unique user identifier
    'email': 'String',         # User's email address
    'wallet': 'String',        # Wallet address (optional)
    'first_name': 'String',    # User's first name
    'last_name': 'String',     # User's last name
    'phone_number': 'String',  # Phone number (optional)
    'created_at': 'String',    # ISO datetime when user was created
    'updated_at': 'String'     # ISO datetime when user was last updated
}
```

### 🔧 **Table Creation Process**

#### Step 1: Automatic Table Creation
```python
# In DynamoDBService.__init__()
def _ensure_users_table(self):
    table_name = 'remo-users'
    
    try:
        # Check if table exists
        self.users_table = self.dynamodb.Table(table_name)
        self.users_table.load()
        print(f"✅ Users table '{table_name}' exists")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            # Create table if it doesn't exist
            print(f"📝 Creating users table '{table_name}'...")
            self._create_users_table(table_name)
```

#### Step 2: Table Configuration
```python
def _create_users_table(self, table_name: str):
    table = self.dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'privy_id',
                'KeyType': 'HASH'  # Partition key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'privy_id',
                'AttributeType': 'S'  # String type
            }
        ],
        BillingMode='PAY_PER_REQUEST'  # Cost-effective for variable workloads
    )
    
    # Wait for table to be created
    table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
    self.users_table = table
    print(f"✅ Users table '{table_name}' created successfully")
```

### 📝 **Step-by-Step Usage Process**

#### Step 1: User Registration
```python
# When a user signs up with Privy
user_data = {
    'privy_id': 'did:privy:1234567890abcdef',
    'email': 'john.doe@example.com',
    'wallet': '0x1234567890abcdef1234567890abcdef12345678',
    'first_name': 'John',
    'last_name': 'Doe',
    'phone_number': '+1234567890'
}

# Save user details to DynamoDB
success = db.save_user_details(user_data)
if success:
    print("✅ User registered successfully")
else:
    print("❌ Failed to register user")
```

#### Step 2: User Authentication
```python
# When user logs in, retrieve their details
user_details = db.get_user_details('did:privy:1234567890abcdef')

if user_details:
    print(f"Welcome back, {user_details['first_name']}!")
    # User is authenticated and can access their data
else:
    print("User not found - redirect to registration")
```

#### Step 3: User Data Retrieval
```python
# Get complete user profile
user_profile = db.get_user_details(privy_id)

# Access specific user information
user_email = user_profile['email']
user_name = f"{user_profile['first_name']} {user_profile['last_name']}"
user_wallet = user_profile['wallet']
```

#### Step 4: User Data Updates
```python
# Update user information
updated_user_data = {
    'privy_id': 'did:privy:1234567890abcdef',
    'email': 'john.doe@newemail.com',  # Updated email
    'first_name': 'John',
    'last_name': 'Smith',  # Updated last name
    'phone_number': '+1987654321'  # Updated phone
}

success = db.save_user_details(updated_user_data)
if success:
    print("✅ User profile updated successfully")
```

### 🔍 **CRUD Operations**

#### Create (Save User Details)
```python
def save_user_details(self, user_data: Dict) -> bool:
    """Save user details to DynamoDB."""
    try:
        item = {
            'privy_id': user_data['privy_id'],
            'email': user_data.get('email', ''),
            'wallet': user_data.get('wallet', ''),
            'first_name': user_data.get('first_name', ''),
            'last_name': user_data.get('last_name', ''),
            'phone_number': user_data.get('phone_number', ''),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        self.users_table.put_item(Item=item)
        return True
        
    except Exception as e:
        print(f"Error saving user details: {e}")
        return False
```

#### Read (Get User Details)
```python
def get_user_details(self, privy_id: str) -> Optional[Dict]:
    """Get user details by Privy ID."""
    try:
        response = self.users_table.get_item(
            Key={'privy_id': privy_id}
        )
        
        return response.get('Item')
        
    except Exception as e:
        print(f"Error getting user details: {e}")
        return None
```

#### Update (Modify User Data)
```python
# Update specific fields
def update_user_field(self, privy_id: str, field: str, value: str) -> bool:
    """Update a specific user field."""
    try:
        self.users_table.update_item(
            Key={'privy_id': privy_id},
            UpdateExpression=f'SET {field} = :value, updated_at = :updated_at',
            ExpressionAttributeValues={
                ':value': value,
                ':updated_at': datetime.now().isoformat()
            }
        )
        return True
    except Exception as e:
        print(f"Error updating user field: {e}")
        return False

# Example usage
db.update_user_field('user_123', 'email', 'newemail@example.com')
db.update_user_field('user_123', 'phone_number', '+1987654321')
```

#### Delete (Remove User)
```python
def delete_user(self, privy_id: str) -> bool:
    """Delete user from the system."""
    try:
        self.users_table.delete_item(
            Key={'privy_id': privy_id}
        )
        return True
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False
```

### 🎯 **Where the remo-users Table is Used**

#### 1. **User Authentication Flow**
```python
# In PrivyAuthGate.tsx (Frontend)
const { user } = usePrivy()
const privy_id = user?.id

# Send to backend for authentication
const response = await fetch('/api/auth', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ privy_id, user_data })
})
```

#### 2. **API Endpoints**
```python
# In app.py - User data endpoints
@app.get("/user/{user_id}/profile")
async def get_user_profile(user_id: str):
    user_details = db.get_user_details(user_id)
    if user_details:
        return {"success": True, "user": user_details}
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.post("/user/profile")
async def update_user_profile(user_data: dict):
    success = db.save_user_details(user_data)
    return {"success": success}
```

#### 3. **User-Specific Data Operations**
```python
# When creating user-specific managers
def get_user_manager(user_id: str):
    # Verify user exists before creating managers
    user_details = db.get_user_details(user_id)
    if not user_details:
        raise ValueError(f"User {user_id} not found")
    
    # Create user-specific memory and context managers
    memory_manager = ConversationMemoryManager(user_id=user_id)
    context_manager = ConversationContextManager(user_id=user_id)
    return {'memory_manager': memory_manager, 'context_manager': context_manager}
```

#### 4. **Data Isolation Verification**
```python
# Ensure user data is properly isolated
def verify_user_access(user_id: str, requested_user_id: str) -> bool:
    """Verify that a user can only access their own data."""
    return user_id == requested_user_id

# Usage in API endpoints
@app.get("/user/{user_id}/todos")
async def get_user_todos(user_id: str, current_user: str):
    if not verify_user_access(current_user, user_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    todos = db.get_todos(user_id)
    return {"todos": todos}
```

### 🔒 **Security Features**

#### 1. **User Data Isolation**
- Each user's data is completely separated by `privy_id`
- No cross-user data access possible
- Partition key ensures data distribution

#### 2. **Authentication Integration**
- Integrates with Privy for secure authentication
- Stores only necessary user information
- No sensitive data like passwords stored

#### 3. **Data Validation**
```python
def validate_user_data(user_data: Dict) -> bool:
    """Validate user data before saving."""
    required_fields = ['privy_id', 'email']
    
    for field in required_fields:
        if field not in user_data or not user_data[field]:
            return False
    
    # Validate email format
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, user_data['email']):
        return False
    
    return True
```

### 📊 **Performance Optimizations**

#### 1. **Partition Key Design**
- `privy_id` as partition key ensures even distribution
- No hot partition issues
- Efficient queries by user ID

#### 2. **Pay-per-Request Billing**
- Cost-effective for variable workloads
- No capacity planning required
- Scales automatically with usage

#### 3. **Minimal Data Storage**
- Only essential user information stored
- No redundant data
- Efficient storage usage

### 🧪 **Testing the remo-users Table**

#### Manual Testing
```python
# Test user creation
user_data = {
    'privy_id': 'test_user_123',
    'email': 'test@example.com',
    'first_name': 'Test',
    'last_name': 'User'
}

# Save user
success = db.save_user_details(user_data)
print(f"User creation: {'✅ Success' if success else '❌ Failed'}")

# Retrieve user
user = db.get_user_details('test_user_123')
print(f"User retrieval: {'✅ Success' if user else '❌ Failed'}")
print(f"User data: {user}")
```

#### Automated Testing
```bash
# Run the setup script to test table functionality
python scripts/setup_dynamodb.py
```

The `remo-users` table serves as the foundation for Remo's user management system, providing secure, isolated storage for user profiles while enabling seamless integration with Privy authentication and user-specific data operations throughout the application.

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
