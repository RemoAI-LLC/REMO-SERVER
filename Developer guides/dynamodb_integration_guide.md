# DynamoDB Integration Guide for Remo

This guide provides comprehensive documentation for the DynamoDB integration that enables user-specific functionality in Remo.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Setup and Configuration](#setup-and-configuration)
4. [Database Schema](#database-schema)
5. [API Integration](#api-integration)
6. [User-Specific Features](#user-specific-features)
7. [Development Workflow](#development-workflow)
8. [Testing](#testing)
9. [Deployment](#deployment)
10. [Troubleshooting](#troubleshooting)

## Overview

Remo now supports user-specific functionality using DynamoDB as the backend storage solution. Each user's data is isolated and stored separately, ensuring privacy and personalization.

### Key Features

- **User Isolation**: Each user's data is completely separate
- **Conversation Memory**: Persistent conversation history per user
- **Context Management**: User-specific conversation context and state
- **Reminder Management**: Personal reminders for each user
- **Todo Management**: Individual todo lists and task organization
- **Preferences**: User-specific settings and preferences
- **Data Persistence**: All data persists across sessions

## Architecture

### Data Flow

```
User (Privy ID) → Frontend → Backend API → DynamoDB Service → DynamoDB Table
```

### Components

1. **DynamoDB Service** (`src/utils/dynamodb_service.py`)
   - Handles all DynamoDB operations
   - Provides CRUD operations for different data types
   - Manages table creation and schema

2. **Memory Managers** (Updated)
   - `ConversationMemoryManager`: User-specific conversation memory
   - `ConversationContextManager`: User-specific context management

3. **Agent Tools** (Updated)
   - `Reminder Tools`: User-specific reminder storage
   - `Todo Tools`: User-specific todo storage

4. **API Endpoints** (Updated)
   - All endpoints now accept `user_id` parameter
   - User-specific data retrieval and storage

## Setup and Configuration

### 1. AWS Credentials

Add the following environment variables to your `.env` file:

```bash
# DynamoDB Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=us-east-1
DYNAMODB_TABLE_NAME=remo-user-data
```

### 2. AWS IAM Permissions

Ensure your AWS user/role has the following DynamoDB permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:CreateTable",
                "dynamodb:DescribeTable",
                "dynamodb:PutItem",
                "dynamodb:GetItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:Query",
                "dynamodb:Scan"
            ],
            "Resource": "arn:aws:dynamodb:*:*:table/remo-user-data"
        }
    ]
}
```

### 3. Dependencies

Install the required Python packages:

```bash
pip install boto3>=1.34.0
```

## Database Schema

### Table Structure

**Table Name**: `remo-user-data`

| Attribute | Type | Description |
|-----------|------|-------------|
| `user_id` | String | Partition key (Privy user ID) |
| `data_type` | String | Sort key (type of data) |
| `data` | Map | The actual data content |
| `timestamp` | String | ISO timestamp of last update |
| `ttl` | Number | Time-to-live for automatic cleanup |

### Data Types

The `data_type` field can have the following values:

1. **`conversation_memory`**: User's conversation history
2. **`conversation_context`**: User's conversation context and state
3. **`user_preferences`**: User's settings and preferences
4. **`reminder_data`**: User's reminders and alerts
5. **`todo_data`**: User's todo items and tasks

### Example Data Structure

```json
{
  "user_id": "did:privy:abc123...",
  "data_type": "conversation_memory",
  "data": {
    "conversation_id": "conv_20241201_143022",
    "conversation_start_time": "2024-12-01T14:30:22",
    "last_activity": "2024-12-01T15:45:33",
    "memory_type": "buffer",
    "messages": [
      {
        "role": "user",
        "content": "Set a reminder for tomorrow 9am",
        "timestamp": "2024-12-01T14:30:22"
      },
      {
        "role": "assistant",
        "content": "I'll set a reminder for tomorrow at 9am. What would you like me to remind you about?",
        "timestamp": "2024-12-01T14:30:25"
      }
    ]
  },
  "timestamp": "2024-12-01T15:45:33",
  "ttl": 1735681533
}
```

## API Integration

### Updated Endpoints

All existing endpoints now support user-specific functionality:

#### Chat Endpoint

```http
POST /chat
Content-Type: application/json

{
  "message": "Set a reminder for tomorrow 9am",
  "conversation_history": [...],
  "user_id": "did:privy:abc123..."
}
```

#### New User Management Endpoints

```http
# Get user data summary
GET /user/{user_id}/data

# Delete user data
DELETE /user/{user_id}/data?data_type=conversation_memory

# Get user preferences
GET /user/{user_id}/preferences

# Save user preferences
POST /user/{user_id}/preferences
Content-Type: application/json

{
  "theme": "dark",
  "language": "en",
  "notifications": true
}
```

### Frontend Integration

The frontend now automatically includes the user ID in all API calls:

```typescript
// Get user ID from Privy
const { user } = usePrivy();
const userId = user?.id;

// Include in API calls
const response = await fetch(`${API_BASE_URL}/chat`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    message: inputText,
    conversation_history: messages,
    user_id: userId
  }),
});
```

## User-Specific Features

### 1. Conversation Memory

Each user has their own conversation history that persists across sessions:

```python
# User-specific memory manager
memory_manager = ConversationMemoryManager(user_id=user_id)
memory_manager.add_message("user", "Hello Remo!")
memory_manager.add_message("assistant", "Hi! How can I help you today?")
```

### 2. Context Management

User-specific conversation context and state:

```python
# User-specific context manager
context_manager = ConversationContextManager(user_id=user_id)
context_manager.set_conversation_topic("reminder")
context_manager.add_pending_request("set_reminder", "reminder_agent", ["time"])
```

### 3. Reminder Management

Personal reminders for each user:

```python
# User-specific reminder tools
set_reminder("Meeting", "2024-12-02T09:00:00", "Team standup", user_id=user_id)
list_reminders(user_id=user_id)
```

### 4. Todo Management

Individual todo lists and task organization:

```python
# User-specific todo tools
add_todo("Complete project", "Finish the documentation", "high", "work", user_id=user_id)
list_todos(user_id=user_id)
```

## Development Workflow

### 1. Local Development

1. Set up AWS credentials in your `.env` file
2. Run the server locally
3. DynamoDB table will be created automatically on first use
4. Test with different user IDs to verify isolation

### 2. Testing User Isolation

```python
# Test with different users
user1_id = "did:privy:user1"
user2_id = "did:privy:user2"

# Set reminders for different users
set_reminder("User 1 reminder", "2024-12-02T10:00:00", user_id=user1_id)
set_reminder("User 2 reminder", "2024-12-02T11:00:00", user_id=user2_id)

# Verify isolation
user1_reminders = list_reminders(user_id=user1_id)
user2_reminders = list_reminders(user_id=user2_id)
# Should show different reminders for each user
```

### 3. Data Migration

If you have existing data, you can migrate it to the new user-specific format:

```python
# Example migration script
def migrate_existing_data():
    # Load existing global data
    old_reminders = load_old_reminders()
    
    # Migrate to user-specific format
    for user_id in get_all_users():
        user_reminders = filter_reminders_for_user(old_reminders, user_id)
        save_reminders_for_user(user_id, user_reminders)
```

## Testing

### Unit Tests

```python
import pytest
from src.utils.dynamodb_service import DynamoDBService

def test_user_isolation():
    service = DynamoDBService()
    
    # Test data isolation
    user1_data = {"reminders": [{"title": "User 1 reminder"}]}
    user2_data = {"reminders": [{"title": "User 2 reminder"}]}
    
    service.save_reminder_data("user1", user1_data)
    service.save_reminder_data("user2", user2_data)
    
    # Verify isolation
    loaded_user1 = service.load_reminder_data("user1")
    loaded_user2 = service.load_reminder_data("user2")
    
    assert loaded_user1["reminders"][0]["title"] == "User 1 reminder"
    assert loaded_user2["reminders"][0]["title"] == "User 2 reminder"
```

### Integration Tests

```python
def test_chat_with_user_id():
    response = client.post("/chat", json={
        "message": "Set a reminder for tomorrow 9am",
        "user_id": "test_user_123"
    })
    
    assert response.status_code == 200
    assert "reminder" in response.json()["response"].lower()
```

## Deployment

### 1. Environment Variables

Ensure all DynamoDB environment variables are set in your deployment environment:

```bash
AWS_ACCESS_KEY_ID=your_production_aws_key
AWS_SECRET_ACCESS_KEY=your_production_aws_secret
AWS_REGION=us-east-1
DYNAMODB_TABLE_NAME=remo-user-data-prod
```

### 2. AWS Configuration

1. Create a production DynamoDB table
2. Set up appropriate IAM roles and permissions
3. Configure auto-scaling if needed
4. Set up CloudWatch monitoring

### 3. Data Backup

Implement regular backups of your DynamoDB table:

```bash
# Example backup script
aws dynamodb create-backup \
    --table-name remo-user-data \
    --backup-name remo-backup-$(date +%Y%m%d)
```

## Troubleshooting

### Common Issues

#### 1. AWS Credentials Not Found

**Error**: `NoCredentialsError: Unable to locate credentials`

**Solution**: Ensure AWS credentials are properly configured in your environment variables.

#### 2. DynamoDB Table Not Found

**Error**: `ResourceNotFoundException: Requested resource not found`

**Solution**: The table will be created automatically on first use. Check your AWS region and table name configuration.

#### 3. Permission Denied

**Error**: `AccessDenied: User is not authorized to perform: dynamodb:PutItem`

**Solution**: Verify your IAM permissions include the necessary DynamoDB actions.

#### 4. User ID Not Provided

**Error**: Data not being saved or loaded

**Solution**: Ensure the frontend is passing the user ID in all API calls.

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# In your DynamoDB service
logger = logging.getLogger(__name__)
logger.debug(f"Saving data for user {user_id}")
```

### Health Check

Use the health check endpoint to verify DynamoDB connectivity:

```http
GET /health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-12-01T15:45:33",
  "dynamodb_available": true
}
```

## Best Practices

### 1. Data Management

- Use TTL (Time-to-Live) for automatic data cleanup
- Implement data retention policies
- Regular backup and monitoring
- Handle data migration carefully

### 2. Performance

- Use appropriate DynamoDB capacity settings
- Monitor read/write capacity units
- Implement caching where appropriate
- Use batch operations for bulk data

### 3. Security

- Use IAM roles with minimal required permissions
- Encrypt data at rest and in transit
- Implement proper access controls
- Regular security audits

### 4. Monitoring

- Set up CloudWatch alarms for DynamoDB metrics
- Monitor API response times
- Track user data usage patterns
- Implement error tracking and alerting

## Conclusion

The DynamoDB integration provides Remo with robust user-specific functionality while maintaining scalability and performance. Each user's data is completely isolated, ensuring privacy and enabling personalized experiences.

For additional support or questions, refer to the main documentation or contact the development team.

---

**Happy coding with user-specific Remo! 🚀✨** 