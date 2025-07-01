# Email Assistant Implementation Guide

## Overview

This guide documents the implementation of the Email Assistant Agent following the [LangChain agents-from-scratch pattern](https://github.com/langchain-ai/agents-from-scratch). The email assistant provides comprehensive email management capabilities including composition, sending, searching, and organization.

## Architecture

The email assistant follows a modular architecture with the following components:

```
src/agents/email/
├── __init__.py              # Module initialization
├── email_agent.py           # Main email agent class
├── email_tools.py           # Email management tools
└── email_triage.py          # Email classification and triage
```

## Step 1: Building the Email Agent

### 1.1 Email Tools (`email_tools.py`)

The email tools provide the core functionality for email management:

#### Core Functions:
- `compose_email()` - Create email drafts
- `send_email()` - Send emails immediately or schedule
- `schedule_email()` - Schedule emails for later
- `search_emails()` - Search through emails
- `mark_email_read()` - Mark emails as read
- `archive_email()` - Archive emails
- `forward_email()` - Forward emails
- `reply_to_email()` - Reply to emails
- `get_email_summary()` - Get email statistics

#### Example Usage:
```python
from src.agents.email.email_tools import compose_email, search_emails

# Compose an email
result = compose_email(
    to_recipients=["john@example.com"],
    subject="Meeting Tomorrow",
    body="Hi John, let's meet tomorrow at 2pm.",
    user_id="user_123"
)

# Search emails
results = search_emails("meeting", user_id="user_123")
```

### 1.2 Email Agent (`email_agent.py`)

The main email agent class that orchestrates email operations:

#### Key Features:
- **Intent Analysis**: Detects email-related intents from user messages
- **Tool Integration**: Uses email tools for actual operations
- **Conversation Management**: Handles multi-turn email conversations
- **User Context**: Maintains user-specific email context

#### Core Methods:
```python
class EmailAgent:
    def __init__(self, user_id: str = None)
    def process(self, user_message: str, conversation_history: List[Dict] = None) -> str
    def _analyze_intent(self, message: str) -> str
    def _handle_compose_email(self, message: str) -> str
    def _handle_send_email(self, message: str) -> str
    def _handle_search_emails(self, message: str) -> str
    def get_agent(self)  # For LangGraph integration
    def get_description(self) -> str  # Agent description
```

#### Intent Detection:
The agent detects various email intents:
- `compose_email` - Writing new emails
- `send_email` - Sending emails
- `schedule_email` - Scheduling emails
- `search_emails` - Searching emails
- `email_summary` - Getting email statistics
- `manage_email` - Email management operations

### 1.3 Email Triage (`email_triage.py`)

Intelligent email classification and prioritization system:

#### Features:
- **Priority Analysis**: Classifies emails as urgent, high, medium, or low priority
- **Category Detection**: Identifies email categories (work, personal, finance, etc.)
- **Urgency Scoring**: Calculates urgency scores (0-10)
- **Action Suggestions**: Provides intelligent suggestions for email handling

#### Example:
```python
from src.agents.email.email_triage import EmailTriage

triage = EmailTriage(user_id="user_123")
email_data = {
    "subject": "Urgent: Meeting Tomorrow",
    "body": "Hi, we have an urgent meeting tomorrow at 2pm.",
    "from": "boss@company.com"
}

result = triage.triage_email(email_data)
# Returns: priority="urgent", category="work", urgency_score=10
```

## Step 2: Integration with Existing System

### 2.1 DynamoDB Integration

The email assistant integrates with the existing DynamoDB service:

#### Email Table Structure:
```json
{
  "TableName": "remo-emails",
  "KeySchema": [
    {"AttributeName": "user_id", "KeyType": "HASH"},
    {"AttributeName": "email_id", "KeyType": "RANGE"}
  ],
  "GlobalSecondaryIndexes": [
    {
      "IndexName": "status-index",
      "KeySchema": [
        {"AttributeName": "user_id", "KeyType": "HASH"},
        {"AttributeName": "status", "KeyType": "RANGE"}
      ]
    },
    {
      "IndexName": "priority-index", 
      "KeySchema": [
        {"AttributeName": "user_id", "KeyType": "HASH"},
        {"AttributeName": "priority", "KeyType": "RANGE"}
      ]
    }
  ]
}
```

#### CRUD Operations:
- `save_email_draft()` - Save email drafts
- `get_email_draft()` - Retrieve email drafts
- `get_emails()` - Query emails with filters
- `update_email_status()` - Update email status
- `delete_email()` - Delete emails
- `save_scheduled_email()` - Save scheduled emails

### 2.2 Memory Integration

The email assistant integrates with the conversation memory system:

#### Intent Detection:
```python
from src.memory.memory_utils import MemoryUtils

# Detect email intents
is_email_intent, details = MemoryUtils.detect_email_intent(message)
```

#### Context Management:
- Email-specific context keywords
- Conversation flow analysis
- Multi-turn email conversations

### 2.3 Orchestration Integration

The email agent integrates with the supervisor orchestrator:

```python
from src.orchestration.supervisor import SupervisorOrchestrator

# Email agent is automatically included in the supervisor
supervisor = SupervisorOrchestrator(model_name="gpt-4o-mini", user_id="user_123")
# Email agent available as: supervisor.email_agent
```

## Step 3: API Integration

### 3.1 Main App Integration

The email assistant is integrated into the main FastAPI application:

#### Intent Detection:
```python
# In app.py
is_email_intent, email_details = MemoryUtils.detect_email_intent(user_message)
```

#### Routing Logic:
```python
elif is_email_intent:
    should_route_to_specialized = True
    target_agent = "email_agent"
    context_manager.set_conversation_topic("email")
    context_manager.set_user_intent("email_management")
    context_manager.set_active_agent("email_agent")
```

#### Agent Processing:
```python
elif target_agent == "email_agent":
    agent_response = supervisor_orchestrator.email_agent.process(
        user_message, conversation_history_for_agent
    )
```

## Step 4: Testing

### 4.1 Test Script

A comprehensive test script validates all email assistant functionality:

```bash
python test_email_functionality.py
```

#### Test Coverage:
- Email intent detection
- Email agent processing
- Email triage functionality
- Email tools functionality
- DynamoDB integration
- Full integration testing

### 4.2 Test Results

The test script validates:
- ✅ Intent detection accuracy
- ✅ Agent response quality
- ✅ Triage classification
- ✅ Tool functionality
- ✅ Database operations
- ✅ Integration workflow

## Usage Examples

### 4.1 Basic Email Operations

```python
# Initialize email agent
email_agent = EmailAgent(user_id="user_123")

# Compose email
response = email_agent.process("compose an email to john@example.com")

# Search emails
response = email_agent.process("search for emails from boss")

# Get email summary
response = email_agent.process("email summary")
```

### 4.2 Advanced Email Management

```python
# Schedule email
response = email_agent.process("schedule an email for tomorrow")

# Manage emails
response = email_agent.process("archive email")
response = email_agent.process("mark email as read")
response = email_agent.process("forward email to colleague")
```

### 4.3 API Usage

```bash
# Chat with email assistant
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "compose an email to john@example.com",
    "user_id": "user_123"
  }'
```

## Configuration

### 4.1 Environment Variables

The email assistant uses the same environment configuration as the main system:

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# OpenAI Configuration
OPENAI_API_KEY=your_openai_key
```

### 4.2 DynamoDB Tables

The email assistant automatically creates the required DynamoDB table:

- **Table Name**: `remo-emails`
- **Partition Key**: `user_id` (String)
- **Sort Key**: `email_id` (String)
- **TTL**: 1 year for automatic cleanup
- **GSIs**: Status and priority indexes for efficient querying

## Performance Considerations

### 4.1 Database Optimization

- **GSIs**: Status and priority indexes for efficient filtering
- **TTL**: Automatic cleanup of old emails
- **Batch Operations**: Support for batch email operations
- **Pagination**: Efficient handling of large email lists

### 4.2 Memory Management

- **Context Awareness**: Maintains conversation context
- **Intent Caching**: Caches detected intents for performance
- **Tool Binding**: Efficient tool binding with user context

## Security

### 4.1 Data Isolation

- **User-Specific**: All email operations are user-specific
- **DynamoDB Partitioning**: Data isolated by user_id
- **Access Control**: User ID required for all operations

### 4.2 Privacy

- **Email Content**: Stored securely in DynamoDB
- **Metadata**: Minimal metadata collection
- **TTL**: Automatic data cleanup

## Future Enhancements

### 4.1 Gmail API Integration

Future versions will include:
- Direct Gmail API integration
- Real email sending capabilities
- Email synchronization
- Calendar integration

### 4.2 Advanced Features

- **Email Templates**: Pre-defined email templates
- **Smart Scheduling**: AI-powered email scheduling
- **Email Analytics**: Usage analytics and insights
- **Multi-account Support**: Multiple email account management

### 4.3 Machine Learning

- **Smart Triage**: ML-powered email classification
- **Priority Learning**: Learn from user email handling patterns
- **Response Suggestions**: AI-powered email response suggestions

## Troubleshooting

### 4.1 Common Issues

1. **DynamoDB Connection**: Ensure AWS credentials are configured
2. **Table Creation**: Tables are created automatically on first use
3. **User ID**: Always provide user_id for email operations
4. **Intent Detection**: Check message format for intent detection

### 4.2 Debug Mode

Enable debug logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Conclusion

The email assistant implementation successfully follows the LangChain agents-from-scratch pattern and integrates seamlessly with the existing Remo system. It provides comprehensive email management capabilities while maintaining the system's architecture and design principles.

The implementation is ready for production use and can be extended with additional features like Gmail API integration and advanced ML capabilities. 