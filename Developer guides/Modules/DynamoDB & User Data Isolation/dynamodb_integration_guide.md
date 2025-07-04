# DynamoDB Integration Guide for Remo

## 🎯 Learning Outcomes

- Understand how Remo-Server uses DynamoDB for user-specific data isolation
- Learn the data flow, schema, and integration patterns
- See how conversation memory, reminders, todos, and preferences are stored per user
- Know how to set up, test, and troubleshoot DynamoDB integration
- Find links to related guides and code references

---

## 1. Overview

Remo-Server uses DynamoDB to provide robust, user-specific data storage. Each user's data (memory, reminders, todos, preferences) is isolated and persisted, enabling personalized and secure experiences.

---

## 2. Architecture & Data Flow

```
User (Privy ID) → Frontend → FastAPI Backend → DynamoDB Service → DynamoDB Table
```

- **`src/utils/dynamodb_service.py`**: All DynamoDB operations (CRUD, schema, user isolation)
- **`src/memory/`**: Memory managers use DynamoDB for persistence
- **API endpoints**: Accept `user_id` for all user-specific operations

---

## 3. Table Schema & Data Types

- **Table Name**: `remo-user-data`
- **Partition Key**: `user_id` (Privy ID)
- **Sort Key**: `data_type` (e.g., `conversation_memory`, `reminder_data`)
- **Data**: JSON map of the actual content
- **Timestamp**: Last update time
- **TTL**: (Optional) For automatic cleanup

### Data Types

- `conversation_memory`: User's conversation history
- `reminder_data`: User's reminders
- `todo_data`: User's todos
- `user_preferences`: User's settings
- `conversation_context`: Conversation state/context

---

## 4. Integration Patterns

### Backend Example

```python
from src.utils.dynamodb_service import DynamoDBService
service = DynamoDBService()
service.save_reminder_data(user_id, reminder_data)
reminders = service.load_reminder_data(user_id)
```

### API Example

```http
POST /chat
{
  "message": "Set a reminder for tomorrow 9am",
  "user_id": "did:privy:abc123..."
}
```

---

## 5. Best Practices

- Always use `user_id` for all data operations
- Test with multiple users to verify isolation
- Use TTL for automatic cleanup if needed
- Monitor and backup your DynamoDB tables
- Handle permissions and AWS credentials securely

---

## 6. Troubleshooting & Debugging

- If data is not isolated, check that `user_id` is passed everywhere
- Use the `/health` endpoint to verify DynamoDB connectivity
- Enable debug logging in `dynamodb_service.py` for more info
- See [User-Specific Implementation Summary](./user_specific_implementation_summary.md) for more details

---

## 7. Related Guides & Next Steps

- [Conversation Memory Guide](./conversation_memory_guide.md)
- [API Integration Guide](./api_integration_guide.md)
- [User-Specific Implementation Summary](./user_specific_implementation_summary.md)
- [Enhanced DynamoDB Guide](./enhanced_dynamodb_guide.md)

---

**For more details, see the DynamoDB service code in `src/utils/dynamodb_service.py` and the memory/user guides.**
