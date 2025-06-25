# Enhanced DynamoDB Integration Guide for Remo AI Assistant

## Overview

This guide covers the enhanced DynamoDB integration for Remo AI Assistant, which provides proper NoSQL table structure for user-specific data storage, conversation memory, reminders, todos, and user details.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Table Structure](#table-structure)
3. [Data Models](#data-models)
4. [API Endpoints](#api-endpoints)
5. [Usage Examples](#usage-examples)
6. [Setup Instructions](#setup-instructions)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## Architecture Overview

The enhanced DynamoDB integration uses a multi-table approach instead of the previous single-table design:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ remo-reminders  │    │   remo-todos    │    │   remo-users    │    │remo-conversations│
│                 │    │                 │    │                 │    │                 │
│ • user_id (PK)  │    │ • user_id (PK)  │    │ • privy_id (PK) │    │ • user_id (PK)  │
│ • reminder_id   │    │ • todo_id (SK)  │    │ • email         │    │ • timestamp (SK)│
│   (SK)          │    │ • title         │    │ • wallet        │    │ • role           │
│ • title         │    │ • description   │    │ • first_name    │    │ • content       │
│ • description   │    │ • priority      │    │ • last_name     │    │ • ttl           │
│ • reminding_time│    │ • status        │    │ • phone_number  │    │                 │
│ • status        │    │ • created_at    │    │ • created_at    │    │                 │
│ • created_at    │    │ • updated_at    │    │ • updated_at    │    │                 │
│ • updated_at    │    │ • ttl           │    │                 │    │                 │
│ • ttl           │    │                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Features

- **User Data Isolation**: Each user's data is completely isolated using their Privy ID
- **Proper NoSQL Design**: Optimized table structure with Global Secondary Indexes (GSIs)
- **Automatic TTL**: Conversation messages are automatically cleaned up after 30 days
- **Status Tracking**: Reminders and todos have status tracking (pending, done, cancelled)
- **Priority Management**: Todos support priority levels (low, medium, high, urgent)
- **Scalable**: Designed to handle millions of users and data points

## Table Structure

### 1. remo-reminders Table

**Primary Key Structure:**
- Partition Key: `user_id` (String) - Privy user ID
- Sort Key: `reminder_id` (String) - Unique reminder identifier

**Attributes:**
- `title` (String) - Reminder title
- `description` (String) - Optional description
- `reminding_time` (String) - ISO datetime when reminder should trigger
- `status` (String) - Status: "pending", "done", "cancelled"
- `created_at` (String) - ISO datetime when created
- `updated_at` (String) - ISO datetime when last updated
- `ttl` (Number) - Time-to-live for automatic cleanup (1 year)

**Global Secondary Indexes:**
- `status-index`: Query reminders by status
  - Partition Key: `user_id`
  - Sort Key: `status`

### 2. remo-todos Table

**Primary Key Structure:**
- Partition Key: `user_id` (String) - Privy user ID
- Sort Key: `todo_id` (String) - Unique todo identifier

**Attributes:**
- `title` (String) - Todo title
- `description` (String) - Optional description
- `priority` (String) - Priority: "low", "medium", "high", "urgent"
- `status` (String) - Status: "pending", "done", "cancelled"
- `created_at` (String) - ISO datetime when created
- `updated_at` (String) - ISO datetime when last updated
- `ttl` (Number) - Time-to-live for automatic cleanup (1 year)

**Global Secondary Indexes:**
- `status-index`: Query todos by status
  - Partition Key: `user_id`
  - Sort Key: `status`
- `priority-index`: Query todos by priority
  - Partition Key: `user_id`
  - Sort Key: `priority`

### 3. remo-users Table

**Primary Key Structure:**
- Partition Key: `privy_id` (String) - Privy user ID

**Attributes:**
- `email` (String) - User's email address
- `wallet` (String) - Wallet address (if wallet login)
- `first_name` (String) - User's first name
- `last_name` (String) - User's last name
- `phone_number` (String) - User's phone number
- `created_at` (String) - ISO datetime when created
- `updated_at` (String) - ISO datetime when last updated

### 4. remo-conversations Table

**Primary Key Structure:**
- Partition Key: `user_id` (String) - Privy user ID
- Sort Key: `timestamp` (String) - ISO datetime of message

**Attributes:**
- `role` (String) - Message role: "user" or "assistant"
- `content` (String) - Message content
- `ttl` (Number) - Time-to-live for automatic cleanup (30 days)

## Data Models

### Reminder Model

```python
{
    "reminder_id": "rem_20241201_143022_abc123",
    "title": "Team Meeting",
    "description": "Weekly team sync",
    "reminding_time": "2024-12-02T10:00:00",
    "status": "pending",
    "created_at": "2024-12-01T14:30:22",
    "updated_at": "2024-12-01T14:30:22",
    "ttl": 1735689600
}
```

### Todo Model

```python
{
    "todo_id": "todo_20241201_143022_abc123",
    "title": "Review project proposal",
    "description": "Review the Q1 project proposal document",
    "priority": "high",
    "status": "pending",
    "created_at": "2024-12-01T14:30:22",
    "updated_at": "2024-12-01T14:30:22",
    "ttl": 1735689600
}
```

### User Model

```python
{
    "privy_id": "did:privy:abc123",
    "email": "user@example.com",
    "wallet": "0x1234567890abcdef",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890",
    "created_at": "2024-12-01T14:30:22",
    "updated_at": "2024-12-01T14:30:22"
}
```

### Conversation Message Model

```python
{
    "user_id": "did:privy:abc123",
    "timestamp": "2024-12-01T14:30:22",
    "role": "user",
    "content": "Hello Remo!",
    "ttl": 1735689600
}
```

## API Endpoints

### DynamoDB Service Methods

#### Reminders

```python
# Save a reminder
dynamodb_service.save_reminder(user_id, reminder_data)

# Get reminders (all or filtered by status)
dynamodb_service.get_reminders(user_id, status="pending")

# Update reminder status
dynamodb_service.update_reminder_status(user_id, reminder_id, "done")

# Delete a reminder
dynamodb_service.delete_reminder(user_id, reminder_id)
```

#### Todos

```python
# Save a todo
dynamodb_service.save_todo(user_id, todo_data)

# Get todos (all or filtered by status/priority)
dynamodb_service.get_todos(user_id, status="pending", priority="high")

# Update todo status
dynamodb_service.update_todo_status(user_id, todo_id, "done")

# Delete a todo
dynamodb_service.delete_todo(user_id, todo_id)
```

#### User Details

```python
# Save user details
dynamodb_service.save_user_details(user_data)

# Get user details
dynamodb_service.get_user_details(privy_id)
```

#### Conversation Memory

```python
# Save a conversation message
dynamodb_service.save_conversation_message(user_id, message_data)

# Get conversation history
dynamodb_service.get_conversation_history(user_id, limit=50)
```

### REST API Endpoints

#### Chat Endpoint

```http
POST /chat
Content-Type: application/json

{
    "message": "Set a reminder for tomorrow at 10am",
    "conversation_history": [...],
    "user_id": "did:privy:abc123"
}
```

#### User Data Endpoints

```http
GET /user/{user_id}/data
DELETE /user/{user_id}/data?data_type=reminders
GET /user/{user_id}/preferences
POST /user/{user_id}/preferences
```

## Usage Examples

### Setting a Reminder

```python
from src.utils.dynamodb_service import DynamoDBService

dynamodb_service = DynamoDBService()

# Create reminder data
reminder_data = {
    "reminder_id": f"rem_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id[-8:]}",
    "title": "Team Meeting",
    "description": "Weekly team sync meeting",
    "reminding_time": "2024-12-02T10:00:00",
    "status": "pending",
    "created_at": datetime.now().isoformat()
}

# Save reminder
success = dynamodb_service.save_reminder(user_id, reminder_data)
```

### Adding a Todo

```python
# Create todo data
todo_data = {
    "todo_id": f"todo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id[-8:]}",
    "title": "Review project proposal",
    "description": "Review the Q1 project proposal document",
    "priority": "high",
    "status": "pending",
    "created_at": datetime.now().isoformat()
}

# Save todo
success = dynamodb_service.save_todo(user_id, todo_data)
```

### Managing Conversation Memory

```python
from src.memory.conversation_memory import ConversationMemoryManager

# Initialize memory manager
memory_manager = ConversationMemoryManager(user_id=user_id)

# Add messages
memory_manager.add_message("user", "Hello Remo!")
memory_manager.add_message("assistant", "Hello! How can I help you today?")

# Get recent messages
recent_messages = memory_manager.get_recent_messages(5)
```

### Using Reminder Tools

```python
from src.agents.reminders.reminder_tools import set_reminder, list_reminders

# Set a reminder
result = set_reminder("Team Meeting", "tomorrow 10am", "Weekly sync", user_id)

# List reminders
reminders = list_reminders(show_completed=False, user_id=user_id)
```

### Using Todo Tools

```python
from src.agents.todo.todo_tools import add_todo, list_todos

# Add a todo
result = add_todo("Review proposal", "high", "work", user_id=user_id)

# List todos
todos = list_todos(show_completed=False, user_id=user_id)
```

## Setup Instructions

### 1. Environment Variables

Create a `.env` file in the `REMO-SERVER` directory:

```env
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=us-east-1
```

### 2. Install Dependencies

```bash
cd REMO-SERVER
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run Setup Script

```bash
python scripts/setup_dynamodb.py
```

This script will:
- Check environment variables
- Create all required DynamoDB tables
- Test user data isolation
- Verify conversation memory functionality
- Test reminder and todo operations
- Validate user details storage

### 4. Start the Server

```bash
python app.py
```

## Troubleshooting

### Common Issues

#### 1. AWS Credentials Not Found

**Error:** `AWS credentials not found`

**Solution:**
- Ensure AWS credentials are set in environment variables
- Check that `.env` file is in the correct location
- Verify AWS credentials have DynamoDB permissions

#### 2. Table Creation Failed

**Error:** `Error creating table`

**Solution:**
- Check AWS permissions (DynamoDB:CreateTable)
- Verify AWS region is correct
- Ensure table names don't conflict with existing tables

#### 3. User Data Not Saving

**Error:** `Failed to save data`

**Solution:**
- Verify user_id is not None
- Check DynamoDB service initialization
- Ensure proper data structure

#### 4. Conversation Memory Not Loading

**Error:** `Error loading conversation history`

**Solution:**
- Check DynamoDB connection
- Verify user_id format
- Ensure conversation table exists

### Debug Mode

Enable debug logging by setting the environment variable:

```env
DEBUG=true
```

### Monitoring

Monitor DynamoDB usage in AWS Console:
- Go to DynamoDB service
- Check table metrics
- Monitor read/write capacity
- Set up CloudWatch alarms

## Best Practices

### 1. Data Modeling

- Use consistent naming conventions for IDs
- Include timestamps for all records
- Use TTL for automatic cleanup
- Design for query patterns

### 2. Performance

- Use GSIs for common query patterns
- Limit query results with pagination
- Use batch operations when possible
- Monitor read/write capacity

### 3. Security

- Use IAM roles with minimal permissions
- Enable encryption at rest
- Use VPC endpoints for private access
- Regularly rotate access keys

### 4. Cost Optimization

- Use on-demand billing for development
- Set up provisioned capacity for production
- Monitor unused tables
- Use TTL for automatic cleanup

### 5. Error Handling

- Always check return values from DynamoDB operations
- Implement retry logic for transient failures
- Log errors with context
- Graceful degradation when DynamoDB is unavailable

## Migration from Old Structure

If migrating from the old single-table structure:

1. **Backup existing data**
2. **Run migration script** (if available)
3. **Update application code**
4. **Test thoroughly**
5. **Switch over gradually**

## Support

For issues or questions:

1. Check the troubleshooting section
2. Review AWS DynamoDB documentation
3. Check application logs
4. Contact the development team

## Conclusion

The enhanced DynamoDB integration provides a robust, scalable foundation for Remo AI Assistant's user-specific data storage. The multi-table approach ensures proper data isolation, efficient querying, and automatic cleanup while maintaining backward compatibility.

Key benefits:
- ✅ Proper NoSQL design
- ✅ User data isolation
- ✅ Automatic TTL cleanup
- ✅ Status and priority tracking
- ✅ Scalable architecture
- ✅ Comprehensive testing
- ✅ Easy maintenance 