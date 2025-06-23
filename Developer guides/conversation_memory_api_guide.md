# Conversation Memory & API Guide

This guide explains how conversation memory works in the Remo AI Assistant backend, especially in the context of the FastAPI `/chat` endpoint. It covers how memory is stored, retrieved, and used, and what data is persisted for each conversation.

---

## 1. What is Conversation Memory?

Conversation memory is the mechanism that allows Remo to remember the context of a conversation across multiple turns. This enables:

- Multi-turn interactions (e.g., follow-up questions, clarifications)
- Context-aware responses
- Task completion over several messages (e.g., reminders, todos)

---

## 2. How Memory Works in the API

### a. API Request Structure

When you call the `/chat` endpoint, you send:

```json
{
  "message": "Set a reminder for tomorrow 9am",
  "conversation_history": [
    { "role": "user", "content": "Hello" },
    { "role": "assistant", "content": "Hi! How can I help you?" }
  ]
}
```

- `message`: The latest user message
- `conversation_history`: The full history of the conversation so far (user and assistant messages)

### b. What Gets Stored?

**Both user and Remo (assistant) replies are stored** in the conversation memory. This is essential for:

- Maintaining context
- Allowing the AI to reference previous exchanges
- Handling incomplete requests and follow-ups

**Example memory after a few turns:**

```json
[
  { "role": "user", "content": "Set a reminder for tomorrow 9am" },
  { "role": "assistant", "content": "What should I remind you about?" },
  { "role": "user", "content": "Dentist appointment" },
  {
    "role": "assistant",
    "content": "Reminder set for tomorrow 9am: Dentist appointment."
  }
]
```

### c. How Memory is Used in the API

1. **Request Handling**

   - The API receives the latest message and the conversation history.
   - The backend combines the provided history with the new message to form the current context.

2. **Memory Update**

   - After generating a response, the backend appends both the user message and the assistant's reply to the memory.
   - This updated memory can be returned to the frontend or stored for future requests.

3. **Contextual Reasoning**
   - The full conversation history is passed to the LLM and agent orchestrator.
   - This allows Remo to:
     - Detect intent (reminder, todo, etc.)
     - Track incomplete requests
     - Reference previous answers
     - Maintain a consistent persona

### d. Memory Types

- **Buffer Memory** (default): Stores the exact sequence of messages for the current session. Best for short- to medium-length conversations.
- **Summary Memory** (optional): Summarizes long conversations to save space and maintain context.
- **Auto-switching**: The system can switch to summary memory if the conversation gets too long.

---

## 3. Where is Memory Stored?

- **In-memory (default):** For each API session, memory is kept in RAM (not persisted between server restarts).
- **Frontend responsibility:** The frontend is responsible for sending the full conversation history with each `/chat` request. This is typical for stateless APIs.
- **(Optional) Persistent storage:** For advanced use, you can extend the backend to persist memory to a database or file.

---

## 4. Example: Multi-turn API Usage

### Step 1: User starts a conversation

```json
{
  "message": "Set a reminder for painting",
  "conversation_history": []
}
```

**Remo:** "What time should I set the reminder for painting?"

### Step 2: User follows up

```json
{
  "message": "Tomorrow at 9am",
  "conversation_history": [
    { "role": "user", "content": "Set a reminder for painting" },
    {
      "role": "assistant",
      "content": "What time should I set the reminder for painting?"
    }
  ]
}
```

**Remo:** "Reminder set for painting at tomorrow 9am. Would you like to add a description?"

### Step 3: User adds more info

```json
{
  "message": "Yes, add description: paint the living room",
  "conversation_history": [
    { "role": "user", "content": "Set a reminder for painting" },
    {
      "role": "assistant",
      "content": "What time should I set the reminder for painting?"
    },
    { "role": "user", "content": "Tomorrow at 9am" },
    {
      "role": "assistant",
      "content": "Reminder set for painting at tomorrow 9am. Would you like to add a description?"
    }
  ]
}
```

**Remo:** "Description added: paint the living room."

---

## 5. Best Practices

- **Always send the full conversation history** with each API call for best results.
- **Store both user and assistant messages** in your frontend state.
- **Truncate or summarize** long histories if needed (see summary memory).
- **For persistent memory**, consider extending the backend to use a database.

---

## 6. Advanced: Customizing Memory Behavior

- You can configure the memory type (buffer, summary, etc.) in the backend code.
- For persistent, user-specific memory, implement a user/session ID and store memory server-side.
- For stateless APIs, the frontend manages memory and sends it with each request.

---

## 7. Summary

- **Both user and Remo replies are stored** in the conversation memory.
- **Memory is used to provide context** for every API call.
- **Frontend is responsible** for sending the conversation history with each request.
- **Memory enables multi-turn, context-aware conversations** and advanced agent orchestration.

---

**For more details, see the main API integration guide and the memory source code in `src/memory/`.**
