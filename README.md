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

## 🗄️ DynamoDB Table: `remo-reminders`

The `remo-reminders` table is the core storage system for Remo's reminder functionality, enabling users to set, track, and manage their reminders with complete data isolation and efficient querying.

### 📊 **Table Structure**

```python
# remo-reminders Table Schema
{
    'user_id': 'HASH',         # Partition Key (String) - User identifier
    'reminder_id': 'RANGE',    # Sort Key (String) - Unique reminder identifier
    'title': 'String',         # Reminder title/name
    'description': 'String',   # Optional reminder description
    'reminding_time': 'String', # ISO datetime when reminder should trigger
    'status': 'String',        # Status: 'pending', 'done', 'cancelled'
    'created_at': 'String',    # ISO datetime when reminder was created
    'updated_at': 'String',    # ISO datetime when reminder was last updated
    'ttl': 'Number'            # Unix timestamp + 1 year for automatic cleanup
}

# Global Secondary Index: status-index
{
    'user_id': 'HASH',         # Partition key
    'status': 'RANGE'          # Sort key for status-based queries
}
```

### 🔧 **Table Creation Process**

#### Step 1: Automatic Table Creation
```python
# In DynamoDBService.__init__()
def _ensure_reminders_table(self):
    table_name = 'remo-reminders'
    
    try:
        # Check if table exists
        self.reminders_table = self.dynamodb.Table(table_name)
        self.reminders_table.load()
        print(f"✅ Reminders table '{table_name}' exists")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            # Create table if it doesn't exist
            print(f"📝 Creating reminders table '{table_name}'...")
            self._create_reminders_table(table_name)
```

#### Step 2: Table Configuration with GSI
```python
def _create_reminders_table(self, table_name: str):
    table = self.dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'user_id',
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'reminder_id',
                'KeyType': 'RANGE'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'user_id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'reminder_id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'status',
                'AttributeType': 'S'
            }
        ],
        BillingMode='PAY_PER_REQUEST',
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'status-index',
                'KeySchema': [
                    {
                        'AttributeName': 'user_id',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': 'status',
                        'KeyType': 'RANGE'
                    }
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                }
            }
        ]
    )
    
    # Wait for table to be created
    table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
    self.reminders_table = table
    print(f"✅ Reminders table '{table_name}' created successfully")
```

### 📝 **Step-by-Step Usage Process**

#### Step 1: Setting a Reminder
```python
# When user sets a reminder through the agent
reminder_data = {
    'reminder_id': f"rem_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id[-8:]}",
    'title': 'Doctor Appointment',
    'description': 'Annual checkup with Dr. Smith',
    'reminding_time': '2025-06-26T14:00:00',
    'status': 'pending',
    'created_at': datetime.now().isoformat()
}

# Save reminder to DynamoDB
success = db.save_reminder('user_123', reminder_data)
if success:
    print("✅ Reminder set successfully")
else:
    print("❌ Failed to set reminder")
```

#### Step 2: Listing User Reminders
```python
# Get all reminders for a user
all_reminders = db.get_reminders('user_123')

# Get only pending reminders
pending_reminders = db.get_reminders('user_123', status='pending')

# Get only completed reminders
completed_reminders = db.get_reminders('user_123', status='done')

print(f"Found {len(all_reminders)} total reminders")
print(f"Found {len(pending_reminders)} pending reminders")
print(f"Found {len(completed_reminders)} completed reminders")
```

#### Step 3: Updating Reminder Status
```python
# Mark reminder as completed
success = db.update_reminder_status('user_123', 'rem_20250625_180000_user_123', 'done')

# Mark reminder as cancelled
success = db.update_reminder_status('user_123', 'rem_20250625_180000_user_123', 'cancelled')

if success:
    print("✅ Reminder status updated successfully")
else:
    print("❌ Failed to update reminder status")
```

#### Step 4: Managing Reminders
```python
# Update reminder details
updated_reminder = {
    'reminder_id': 'rem_20250625_180000_user_123',
    'title': 'Updated Doctor Appointment',
    'description': 'Rescheduled checkup',
    'reminding_time': '2025-06-27T15:00:00',
    'status': 'pending',
    'created_at': '2025-06-25T18:00:00'
}

success = db.save_reminder('user_123', updated_reminder)

# Delete a reminder
success = db.delete_reminder('user_123', 'rem_20250625_180000_user_123')
```

### 🔍 **CRUD Operations**

#### Create (Save Reminder)
```python
def save_reminder(self, user_id: str, reminder_data: Dict) -> bool:
    """Save a reminder to DynamoDB."""
    try:
        item = {
            'user_id': user_id,
            'reminder_id': reminder_data['reminder_id'],
            'title': reminder_data['title'],
            'description': reminder_data.get('description', ''),
            'reminding_time': reminder_data['reminding_time'],
            'status': reminder_data.get('status', 'pending'),
            'created_at': reminder_data['created_at'],
            'updated_at': datetime.now().isoformat(),
            'ttl': int(datetime.now().timestamp()) + (365 * 24 * 60 * 60)  # 1 year TTL
        }
        
        self.reminders_table.put_item(Item=item)
        return True
        
    except Exception as e:
        print(f"Error saving reminder: {e}")
        return False
```

#### Read (Get Reminders)
```python
def get_reminders(self, user_id: str, status: str = None) -> List[Dict]:
    """Get reminders for a user, optionally filtered by status."""
    try:
        if status:
            # Use GSI to filter by status
            response = self.reminders_table.query(
                IndexName='status-index',
                KeyConditionExpression='user_id = :user_id AND #status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':user_id': user_id,
                    ':status': status
                }
            )
        else:
            # Get all reminders for user
            response = self.reminders_table.query(
                KeyConditionExpression='user_id = :user_id',
                ExpressionAttributeValues={':user_id': user_id}
            )
        
        return response.get('Items', [])
        
    except Exception as e:
        print(f"Error getting reminders: {e}")
        return []
```

#### Update (Update Reminder Status)
```python
def update_reminder_status(self, user_id: str, reminder_id: str, status: str) -> bool:
    """Update reminder status."""
    try:
        self.reminders_table.update_item(
            Key={
                'user_id': user_id,
                'reminder_id': reminder_id
            },
            UpdateExpression='SET #status = :status, updated_at = :updated_at',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': status,
                ':updated_at': datetime.now().isoformat()
            }
        )
        return True
        
    except Exception as e:
        print(f"Error updating reminder status: {e}")
        return False
```

#### Delete (Remove Reminder)
```python
def delete_reminder(self, user_id: str, reminder_id: str) -> bool:
    """Delete a reminder."""
    try:
        self.reminders_table.delete_item(
            Key={
                'user_id': user_id,
                'reminder_id': reminder_id
            }
        )
        return True
        
    except Exception as e:
        print(f"Error deleting reminder: {e}")
        return False
```

### 🎯 **Where the remo-reminders Table is Used**

#### 1. **Reminder Agent Operations**
```python
# In reminder_agent.py - Setting reminders
def set_reminder(title: str, datetime_str: str, description: str = "", user_id: str = None):
    reminder_data = {
        "reminder_id": f"rem_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id[-8:]}",
        "title": title,
        "description": description,
        "reminding_time": reminder_time.isoformat(),
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    
    if dynamodb_service.save_reminder(user_id, reminder_data):
        return f"✅ Reminder set: '{title}' for {reminder_time.strftime('%Y-%m-%d %H:%M')}"
    else:
        return "❌ Failed to save reminder to database"
```

#### 2. **Reminder Tools Integration**
```python
# In reminder_tools.py - Listing reminders
def list_reminders(show_completed: bool = False, user_id: str = None):
    if show_completed:
        reminders = dynamodb_service.get_reminders(user_id)
    else:
        reminders = dynamodb_service.get_reminders(user_id, status="pending")
    
    # Format and return reminder list
    result = "📋 Your Reminders:\n\n"
    for reminder in reminders:
        status = "✅" if reminder.get("status") == "done" else "⏰"
        reminder_time = datetime.fromisoformat(reminder["reminding_time"])
        result += f"{status} {reminder['title']}\n"
        result += f"   📅 {reminder_time.strftime('%Y-%m-%d %H:%M')}\n"
        if reminder.get("description"):
            result += f"   📝 {reminder['description']}\n"
        result += f"   🆔 {reminder['reminder_id']}\n\n"
    
    return result
```

#### 3. **API Endpoints**
```python
# In app.py - Reminder management endpoints
@app.get("/user/{user_id}/reminders")
async def get_user_reminders(user_id: str, status: str = None):
    reminders = db.get_reminders(user_id, status=status)
    return {"reminders": reminders, "count": len(reminders)}

@app.post("/user/{user_id}/reminders")
async def create_reminder(user_id: str, reminder_data: dict):
    success = db.save_reminder(user_id, reminder_data)
    return {"success": success}

@app.put("/user/{user_id}/reminders/{reminder_id}/status")
async def update_reminder_status(user_id: str, reminder_id: str, status: str):
    success = db.update_reminder_status(user_id, reminder_id, status)
    return {"success": success}
```

#### 4. **Chat Integration**
```python
# In app.py - Chat endpoint with reminder intent detection
if is_reminder_intent:
    should_route_to_specialized = True
    target_agent = "reminder_agent"
    context_manager.set_conversation_topic("reminder")
    context_manager.set_user_intent("set_reminder")
    
    # Call reminder agent with user context
    agent_response = supervisor_orchestrator.reminder_agent.process(
        user_message, conversation_history_for_agent
    )
```

### 🔒 **Security Features**

#### 1. **User Data Isolation**
- Each user's reminders are completely separated by `user_id`
- No cross-user data access possible
- Partition key ensures data distribution

#### 2. **Status-Based Access Control**
```python
def verify_reminder_access(user_id: str, reminder_id: str) -> bool:
    """Verify that a user can only access their own reminders."""
    reminders = db.get_reminders(user_id)
    return any(reminder['reminder_id'] == reminder_id for reminder in reminders)
```

#### 3. **Data Validation**
```python
def validate_reminder_data(reminder_data: Dict) -> bool:
    """Validate reminder data before saving."""
    required_fields = ['reminder_id', 'title', 'reminding_time']
    
    for field in required_fields:
        if field not in reminder_data or not reminder_data[field]:
            return False
    
    # Validate datetime format
    try:
        datetime.fromisoformat(reminder_data['reminding_time'])
    except ValueError:
        return False
    
    # Validate status
    valid_statuses = ['pending', 'done', 'cancelled']
    if reminder_data.get('status') not in valid_statuses:
        return False
    
    return True
```

### 📊 **Performance Optimizations**

#### 1. **Partition Key Design**
- `user_id` as partition key ensures even distribution
- Efficient queries for user-specific reminders
- No hot partition issues

#### 2. **Global Secondary Index (GSI)**
- `status-index` enables efficient status-based filtering
- Fast queries for pending, completed, or cancelled reminders
- Maintains query performance as data grows

#### 3. **TTL (Time To Live)**
- Automatic cleanup after 1 year
- Reduces storage costs
- Maintains database performance

#### 4. **Pay-per-Request Billing**
- Cost-effective for variable workloads
- Scales automatically with usage
- No capacity planning required

### 🧪 **Testing the remo-reminders Table**

#### Manual Testing
```python
# Test reminder creation
reminder_data = {
    'reminder_id': 'test_rem_001',
    'title': 'Test Reminder',
    'description': 'This is a test reminder',
    'reminding_time': '2025-06-26T10:00:00',
    'status': 'pending',
    'created_at': datetime.now().isoformat()
}

# Save reminder
success = db.save_reminder('test_user_123', reminder_data)
print(f"Reminder creation: {'✅ Success' if success else '❌ Failed'}")

# Retrieve reminders
reminders = db.get_reminders('test_user_123')
print(f"Reminder retrieval: {'✅ Success' if reminders else '❌ Failed'}")
print(f"Found {len(reminders)} reminders")

# Update status
success = db.update_reminder_status('test_user_123', 'test_rem_001', 'done')
print(f"Status update: {'✅ Success' if success else '❌ Failed'}")

# Test GSI query
pending_reminders = db.get_reminders('test_user_123', status='pending')
print(f"Pending reminders: {len(pending_reminders)}")
```

#### Automated Testing
```bash
# Run the setup script to test table functionality
python scripts/setup_dynamodb.py

# Run reminder-specific tests
python test_reminder_detection.py
```

### 🔄 **Real-World Usage Examples**

#### Example 1: Setting Multiple Reminders
```python
# User sets multiple reminders
reminders_to_set = [
    {
        'title': 'Morning Meeting',
        'reminding_time': '2025-06-26T09:00:00',
        'description': 'Weekly team standup'
    },
    {
        'title': 'Doctor Appointment',
        'reminding_time': '2025-06-26T14:00:00',
        'description': 'Annual checkup'
    },
    {
        'title': 'Grocery Shopping',
        'reminding_time': '2025-06-26T18:00:00',
        'description': 'Buy milk and bread'
    }
]

for reminder in reminders_to_set:
    reminder_data = {
        'reminder_id': f"rem_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id[-8:]}",
        'title': reminder['title'],
        'description': reminder['description'],
        'reminding_time': reminder['reminding_time'],
        'status': 'pending',
        'created_at': datetime.now().isoformat()
    }
    db.save_reminder('user_123', reminder_data)
```

#### Example 2: Reminder Management Workflow
```python
# 1. List all reminders
all_reminders = db.get_reminders('user_123')
print(f"Total reminders: {len(all_reminders)}")

# 2. List pending reminders
pending = db.get_reminders('user_123', status='pending')
print(f"Pending reminders: {len(pending)}")

# 3. Mark a reminder as done
if pending:
    reminder_to_complete = pending[0]
    db.update_reminder_status('user_123', reminder_to_complete['reminder_id'], 'done')
    print(f"Completed: {reminder_to_complete['title']}")

# 4. List completed reminders
completed = db.get_reminders('user_123', status='done')
print(f"Completed reminders: {len(completed)}")
```

The `remo-reminders` table provides a robust, scalable foundation for Remo's reminder functionality, ensuring user data isolation, efficient querying, and automatic maintenance while supporting all CRUD operations needed for comprehensive reminder management.

## 3. remo-todos Table

The `remo-todos` table stores user-specific todo items with priority levels and status tracking.

### Table Structure

```json
{
  "TableName": "remo-todos",
  "KeySchema": [
    {
      "AttributeName": "user_id",
      "KeyType": "HASH"
    },
    {
      "AttributeName": "todo_id", 
      "KeyType": "RANGE"
    }
  ],
  "AttributeDefinitions": [
    {
      "AttributeName": "user_id",
      "AttributeType": "S"
    },
    {
      "AttributeName": "todo_id",
      "AttributeType": "S"
    },
    {
      "AttributeName": "status",
      "AttributeType": "S"
    },
    {
      "AttributeName": "priority",
      "AttributeType": "S"
    }
  ],
  "GlobalSecondaryIndexes": [
    {
      "IndexName": "status-index",
      "KeySchema": [
        {
          "AttributeName": "user_id",
          "KeyType": "HASH"
        },
        {
          "AttributeName": "status",
          "KeyType": "RANGE"
        }
      ],
      "Projection": {
        "ProjectionType": "ALL"
      }
    },
    {
      "IndexName": "priority-index",
      "KeySchema": [
        {
          "AttributeName": "user_id",
          "KeyType": "HASH"
        },
        {
          "AttributeName": "priority",
          "KeyType": "RANGE"
        }
      ],
      "Projection": {
        "ProjectionType": "ALL"
      }
    }
  ],
  "BillingMode": "PAY_PER_REQUEST",
  "TimeToLiveSpecification": {
    "Enabled": true,
    "AttributeName": "ttl"
  }
}
```

### Item Structure

```json
{
  "user_id": "did:privy:abc123...",
  "todo_id": "todo_20241201_001",
  "title": "Complete project documentation",
  "description": "Write comprehensive API documentation for the new features",
  "priority": "high",
  "status": "pending",
  "created_at": "2024-12-01T10:30:00Z",
  "updated_at": "2024-12-01T15:45:00Z",
  "ttl": 1735689600
}
```

### Field Descriptions

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `user_id` | String | Privy user ID (partition key) | `"did:privy:abc123..."` |
| `todo_id` | String | Unique todo identifier (sort key) | `"todo_20241201_001"` |
| `title` | String | Todo title/name | `"Complete project documentation"` |
| `description` | String | Detailed description | `"Write comprehensive API docs"` |
| `priority` | String | Priority level | `"low"`, `"medium"`, `"high"`, `"urgent"` |
| `status` | String | Current status | `"pending"`, `"done"`, `"cancelled"` |
| `created_at` | String | ISO datetime of creation | `"2024-12-01T10:30:00Z"` |
| `updated_at` | String | ISO datetime of last update | `"2024-12-01T15:45:00Z"` |
| `ttl` | Number | Unix timestamp for expiration | `1735689600` (1 year) |

### CRUD Operations

#### Create Todo

```python
from src.utils.dynamodb_service import DynamoDBService
from datetime import datetime
import uuid

db = DynamoDBService()

# Create a new todo
todo_data = {
    'todo_id': f"todo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}",
    'title': 'Complete project documentation',
    'description': 'Project documentation needs to be completed by Friday',
    'priority': 'high',
    'status': 'pending',
    'created_at': datetime.now().isoformat()
}

success = db.save_todo(user_id="did:privy:abc123...", todo_data=todo_data)
print(f"Todo created: {success}")
```

#### Read Todos

```python
# Get all todos for a user
todos = db.get_todos(user_id="did:privy:abc123...")

# Get todos by status
pending_todos = db.get_todos(user_id="did:privy:abc123...", status="pending")
done_todos = db.get_todos(user_id="did:privy:abc123...", status="done")

# Get todos by priority
high_priority_todos = db.get_todos(user_id="did:privy:abc123...", priority="high")
urgent_todos = db.get_todos(user_id="did:privy:abc123...", priority="urgent")

# Get pending high priority todos
pending_high_todos = db.get_todos(user_id="did:privy:abc123...", status="pending", priority="high")
```

#### Update Todo

```python
# Mark todo as done
success = db.update_todo_status(
    user_id="did:privy:abc123...",
    todo_id="todo_20241201_001",
    status="done"
)

# Update priority
success = db.update_todo_status(
    user_id="did:privy:abc123...", 
    todo_id="todo_20241201_001",
    status="urgent"
)
```

#### Delete Todo

```python
# Delete a todo
success = db.delete_todo(
    user_id="did:privy:abc123...",
    todo_id="todo_20241201_001"
)
```

### Usage Examples

#### 1. Creating a Todo with AI Assistant

```python
# User says: "Add a todo to complete the project documentation by Friday"
# AI processes and creates:
todo_data = {
    'todo_id': 'todo_20241201_143022_a1b2c3d4',
    'title': 'Complete project documentation',
    'description': 'Project documentation needs to be completed by Friday',
    'priority': 'medium',
    'status': 'pending',
    'created_at': '2024-12-01T14:30:22Z'
}

db.save_todo(user_id="did:privy:abc123...", todo_data=todo_data)
```

#### 2. Listing User's Todos

```python
# Get all todos
all_todos = db.get_todos(user_id="did:privy:abc123...")

# Format for display
for todo in all_todos:
    print(f"📝 {todo['title']}")
    print(f"   Priority: {todo['priority'].upper()}")
    print(f"   Status: {todo['status']}")
    print(f"   Created: {todo['created_at']}")
    print("---")
```

#### 3. Filtering by Priority and Status

```python
# Get urgent pending todos
urgent_pending = db.get_todos(
    user_id="did:privy:abc123...", 
    status="pending", 
    priority="urgent"
)

# Get all high priority todos
high_priority = db.get_todos(
    user_id="did:privy:abc123...", 
    priority="high"
)
```

#### 4. Marking Todos as Complete

```python
# User says: "Mark the documentation todo as done"
# AI finds and updates:
success = db.update_todo_status(
    user_id="did:privy:abc123...",
    todo_id="todo_20241201_143022_a1b2c3d4",
    status="done"
)
```

### Global Secondary Indexes

#### 1. Status Index (`status-index`)
- **Partition Key**: `user_id`
- **Sort Key**: `status`
- **Use Case**: Query todos by status (pending, done, cancelled)

```python
# Query pending todos
response = db.todos_table.query(
    IndexName='status-index',
    KeyConditionExpression='user_id = :user_id AND #status = :status',
    ExpressionAttributeNames={'#status': 'status'},
    ExpressionAttributeValues={
        ':user_id': 'did:privy:abc123...',
        ':status': 'pending'
    }
)
```

#### 2. Priority Index (`priority-index`)
- **Partition Key**: `user_id`
- **Sort Key**: `priority`
- **Use Case**: Query todos by priority (low, medium, high, urgent)

```python
# Query high priority todos
response = db.todos_table.query(
    IndexName='priority-index',
    KeyConditionExpression='user_id = :user_id AND #priority = :priority',
    ExpressionAttributeNames={'#priority': 'priority'},
    ExpressionAttributeValues={
        ':user_id': 'did:privy:abc123...',
        ':priority': 'high'
    }
)
```

### Best Practices

#### 1. Todo ID Generation
```python
import uuid
from datetime import datetime

def generate_todo_id():
    """Generate a unique todo ID with timestamp."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = uuid.uuid4().hex[:8]
    return f"todo_{timestamp}_{unique_id}"

# Example: todo_20241201_143022_a1b2c3d4
```

#### 2. Priority Levels
```python
PRIORITY_LEVELS = {
    'low': 1,
    'medium': 2, 
    'high': 3,
    'urgent': 4
}

def get_priority_level(priority):
    """Get numeric priority level for sorting."""
    return PRIORITY_LEVELS.get(priority.lower(), 2)
```

#### 3. Status Management
```python
VALID_STATUSES = ['pending', 'done', 'cancelled']

def is_valid_status(status):
    """Validate todo status."""
    return status.lower() in VALID_STATUSES
```

#### 4. Error Handling
```python
def safe_todo_operation(operation_func, *args, **kwargs):
    """Safely execute todo operations with error handling."""
    try:
        result = operation_func(*args, **kwargs)
        return result
    except Exception as e:
        print(f"Todo operation failed: {e}")
        return None

# Usage
success = safe_todo_operation(db.save_todo, user_id, todo_data)
```

### Performance Considerations

#### 1. Query Optimization
- Use GSIs for filtering by status or priority
- Avoid scanning the entire table
- Use consistent read operations when needed

#### 2. Batch Operations
```python
def batch_update_todos(user_id, todo_updates):
    """Batch update multiple todos."""
    with db.todos_table.batch_writer() as batch:
        for todo_id, updates in todo_updates.items():
            batch.update_item(
                Key={'user_id': user_id, 'todo_id': todo_id},
                UpdateExpression='SET ' + ', '.join([f'#{k} = :{k}' for k in updates.keys()]),
                ExpressionAttributeNames={f'#{k}': k for k in updates.keys()},
                ExpressionAttributeValues={f':{k}': v for k, v in updates.items()}
            )
```

#### 3. Pagination
```python
def get_todos_paginated(user_id, limit=10, last_key=None):
    """Get todos with pagination."""
    params = {
        'KeyConditionExpression': 'user_id = :user_id',
        'ExpressionAttributeValues': {':user_id': user_id},
        'Limit': limit
    }
    
    if last_key:
        params['ExclusiveStartKey'] = last_key
    
    response = db.todos_table.query(**params)
    return response.get('Items', []), response.get('LastEvaluatedKey')
```

### Security Considerations

#### 1. User Isolation
- All queries are scoped by `user_id`
- No cross-user data access possible
- Partition key ensures data isolation

#### 2. Input Validation
```python
def validate_todo_data(todo_data):
    """Validate todo data before saving."""
    required_fields = ['todo_id', 'title', 'created_at']
    for field in required_fields:
        if field not in todo_data:
            raise ValueError(f"Missing required field: {field}")
    
    if todo_data.get('priority') not in ['low', 'medium', 'high', 'urgent']:
        todo_data['priority'] = 'medium'
    
    if todo_data.get('status') not in ['pending', 'done', 'cancelled']:
        todo_data['status'] = 'pending'
    
    return todo_data
```

#### 3. TTL Management
- Automatic cleanup after 1 year
- Reduces storage costs
- Maintains data freshness

### Testing

#### 1. Unit Tests
```python
def test_todo_crud_operations():
    """Test todo CRUD operations."""
    db = DynamoDBService()
    user_id = "test_user_123"
    
    # Create
    todo_data = {
        'todo_id': 'test_todo_001',
        'title': 'Test todo',
        'description': 'Test description',
        'priority': 'high',
        'status': 'pending',
        'created_at': datetime.now().isoformat()
    }
    
    assert db.save_todo(user_id, todo_data) == True
    
    # Read
    todos = db.get_todos(user_id)
    assert len(todos) == 1
    assert todos[0]['title'] == 'Test todo'
    
    # Update
    assert db.update_todo_status(user_id, 'test_todo_001', 'done') == True
    
    # Delete
    assert db.delete_todo(user_id, 'test_todo_001') == True
```

#### 2. Integration Tests
```python
def test_todo_filtering():
    """Test todo filtering by status and priority."""
    db = DynamoDBService()
    user_id = "test_user_456"
    
    # Create test todos
    todos = [
        {'todo_id': 'todo1', 'title': 'High Priority', 'priority': 'high', 'status': 'pending'},
        {'todo_id': 'todo2', 'title': 'Low Priority', 'priority': 'low', 'status': 'done'},
        {'todo_id': 'todo3', 'title': 'Urgent Todo', 'priority': 'urgent', 'status': 'pending'}
    ]
    
    for todo in todos:
        todo['created_at'] = datetime.now().isoformat()
        db.save_todo(user_id, todo)
    
    # Test filtering
    pending_todos = db.get_todos(user_id, status='pending')
    assert len(pending_todos) == 2
    
    high_priority_todos = db.get_todos(user_id, priority='high')
    assert len(high_priority_todos) == 1
```

### Monitoring and Debugging

#### 1. CloudWatch Metrics
- Monitor read/write capacity
- Track throttling events
- Monitor GSI performance

#### 2. Logging
```python
import logging

logger = logging.getLogger(__name__)

def save_todo_with_logging(user_id, todo_data):
    """Save todo with detailed logging."""
    logger.info(f"Saving todo for user {user_id}: {todo_data['title']}")
    
    try:
        success = db.save_todo(user_id, todo_data)
        if success:
            logger.info(f"Todo saved successfully: {todo_data['todo_id']}")
        else:
            logger.error(f"Failed to save todo: {todo_data['todo_id']}")
        return success
    except Exception as e:
        logger.error(f"Exception saving todo: {e}")
        return False
```

#### 3. Performance Monitoring
```python
import time

def timed_todo_operation(operation_func, *args, **kwargs):
    """Time todo operations for performance monitoring."""
    start_time = time.time()
    result = operation_func(*args, **kwargs)
    end_time = time.time()
    
    print(f"Operation {operation_func.__name__} took {end_time - start_time:.3f} seconds")
    return result
```

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
