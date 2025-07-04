# Conversation Memory API Guide

## 🎯 Learning Outcomes

- Understand how conversation memory is managed via the Remo API
- Learn the correct request/response patterns for multi-turn conversations
- See how to persist and send conversation history from the frontend
- Know best practices for memory usage and troubleshooting
- Find links to related guides and code references

---

## 1. Overview

Remo-Server's `/chat` endpoint is designed for multi-turn, context-aware conversations. Memory is managed by sending the full conversation history with each API call. This enables:

- Contextual responses
- Multi-turn task completion
- User-specific memory and data isolation

---

## 2. API Request/Response Pattern

### Request Example

```json
{
  "message": "Set a reminder for tomorrow 9am",
  "conversation_history": [
    { "role": "user", "content": "Hello" },
    { "role": "assistant", "content": "Hi! How can I help you?" }
  ],
  "user_id": "user-123"
}
```

- `message`: The latest user message
- `conversation_history`: Full history of the conversation so far (user and assistant messages)
- `user_id`: (Optional) For user-specific memory and data

### Response Example

```json
{
  "response": "Reminder set for tomorrow 9am. What should I remind you about?",
  "success": true,
  "timestamp": "2024-06-01T12:00:00Z",
  "error": null,
  "user_id": "user-123"
}
```

---

## 3. How Memory is Used

- **Frontend**: Responsible for storing and sending the full conversation history with each `/chat` request
- **Backend**: Updates memory after each turn, storing both user and assistant messages
- **User-specific**: Memory is isolated per user (see [DynamoDB Guide](./dynamodb_integration_guide.md))

---

## 4. Best Practices

- Always send the full conversation history for best results
- Store both user and assistant messages in your frontend state
- Truncate or summarize long histories if needed (see [Conversation Memory Guide](./conversation_memory_guide.md))
- Use `user_id` for all requests to enable user-specific memory and data
- For persistent memory, consider extending the backend to use a database (see [DynamoDB Guide](./dynamodb_integration_guide.md))

---

## 5. Debugging & Troubleshooting

- If context is lost, check that the full conversation history is being sent
- If memory grows too large, implement truncation or summarization in the frontend
- Use the `/health` endpoint to verify backend status
- See [API Integration Guide](./api_integration_guide.md) for more endpoint details

---

## 6. Related Guides & Next Steps

- [Conversation Memory Guide](./conversation_memory_guide.md)
- [API Integration Guide](./api_integration_guide.md)
- [Frontend Integration Guide](../../REMO-APP/)
- [DynamoDB Integration Guide](./dynamodb_integration_guide.md)

---

**For more details, see the memory and API source code in `src/memory/` and `app.py`.**
