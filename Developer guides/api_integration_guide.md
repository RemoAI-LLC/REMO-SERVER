# Remo API Integration Guide

This guide provides comprehensive documentation for integrating with the Remo AI Assistant API.

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base URL](#base-url)
4. [Endpoints](#endpoints)
5. [Request/Response Format](#requestresponse-format)
6. [Examples by Language](#examples-by-language)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)
9. [Rate Limiting](#rate-limiting)
10. [WebSocket Support](#websocket-support)

## Overview

The Remo API provides access to a sophisticated AI assistant with multi-agent orchestration, conversation memory, and specialized capabilities for reminders and todo management.

### Key Features

- **Multi-Agent Orchestration**: Automatic routing to specialized agents
- **Conversation Memory**: Context-aware responses across multiple turns
- **Intent Detection**: Automatic detection of reminder and todo requests
- **Fallback Handling**: Graceful degradation if specialized agents fail
- **Real-time Processing**: Fast response times with streaming support

## Authentication

Currently, the API uses environment-based authentication. Ensure your backend has the required API keys:

```bash
OPENAI_API_KEY=your_openai_api_key
LANGCHAIN_API_KEY=your_langsmith_key  # Optional
LANGCHAIN_PROJECT=your_project_name   # Optional
```

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://remo-server.onrender.com`

## Endpoints

### Health Check

```http
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "service": "Remo AI Assistant API",
  "version": "1.0.0"
}
```

### Chat Endpoint

```http
POST /chat
Content-Type: application/json
```

**Request Body:**

```json
{
  "message": "string",
  "conversation_history": [
    {
      "role": "user|assistant",
      "content": "string"
    }
  ]
}
```

**Response:**

```json
{
  "response": "string",
  "success": true,
  "error": null
}
```

## Request/Response Format

### Request Fields

| Field                  | Type   | Required | Description                    |
| ---------------------- | ------ | -------- | ------------------------------ |
| `message`              | string | Yes      | The user's message             |
| `conversation_history` | array  | No       | Previous conversation messages |

### Conversation History Format

```json
[
  {
    "role": "user",
    "content": "Set a reminder for tomorrow 9am"
  },
  {
    "role": "assistant",
    "content": "What would you like me to remind you about?"
  }
]
```

### Response Fields

| Field      | Type    | Description                        |
| ---------- | ------- | ---------------------------------- |
| `response` | string  | The assistant's response           |
| `success`  | boolean | Whether the request was successful |
| `error`    | string  | Error message if success is false  |

## Examples by Language

### JavaScript/Node.js

#### Using Fetch

```javascript
const API_BASE_URL = "https://remo-server.onrender.com";

async function chatWithRemo(message, conversationHistory = []) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        conversation_history: conversationHistory,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error:", error);
    throw error;
  }
}

// Example usage
const conversation = [
  { role: "user", content: "Hello Remo!" },
  { role: "assistant", content: "Hi! How can I help you today?" },
];

chatWithRemo("Set a reminder for tomorrow 9am", conversation)
  .then((data) => console.log("Response:", data.response))
  .catch((error) => console.error("Error:", error));
```

#### Using Axios

```javascript
import axios from "axios";

const API_BASE_URL = "https://remo-server.onrender.com";

const remoAPI = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

async function chatWithRemo(message, conversationHistory = []) {
  try {
    const response = await remoAPI.post("/chat", {
      message,
      conversation_history: conversationHistory,
    });

    return response.data;
  } catch (error) {
    console.error("Error:", error.response?.data || error.message);
    throw error;
  }
}
```

### Python

#### Using requests

```python
import requests
import json

API_BASE_URL = 'https://remo-server.onrender.com'

def chat_with_remo(message, conversation_history=None):
    if conversation_history is None:
        conversation_history = []

    url = f"{API_BASE_URL}/chat"
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'message': message,
        'conversation_history': conversation_history
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        raise

# Example usage
conversation = [
    {'role': 'user', 'content': 'Hello Remo!'},
    {'role': 'assistant', 'content': 'Hi! How can I help you today?'}
]

try:
    result = chat_with_remo('Set a reminder for tomorrow 9am', conversation)
    print('Response:', result['response'])
except Exception as e:
    print('Error:', e)
```

#### Using aiohttp (Async)

```python
import aiohttp
import asyncio

API_BASE_URL = 'https://remo-server.onrender.com'

async def chat_with_remo_async(message, conversation_history=None):
    if conversation_history is None:
        conversation_history = []

    url = f"{API_BASE_URL}/chat"
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'message': message,
        'conversation_history': conversation_history
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"HTTP {response.status}: {await response.text()}")

# Example usage
async def main():
    conversation = [
        {'role': 'user', 'content': 'Hello Remo!'},
        {'role': 'assistant', 'content': 'Hi! How can I help you today?'}
    ]

    try:
        result = await chat_with_remo_async('Set a reminder for tomorrow 9am', conversation)
        print('Response:', result['response'])
    except Exception as e:
        print('Error:', e)

asyncio.run(main())
```

### cURL

#### Basic Chat

```bash
curl -X POST https://remo-server.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "who are you?",
    "conversation_history": []
  }'
```

#### Set Reminder

```bash
curl -X POST https://remo-server.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "set a reminder for painting tomorrow at 9am",
    "conversation_history": []
  }'
```

#### Add Todo

```bash
curl -X POST https://remo-server.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "add buy groceries to my todo list",
    "conversation_history": []
  }'
```

#### With Conversation History

```bash
curl -X POST https://remo-server.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "yes, add description: paint the living room",
    "conversation_history": [
      {"role": "user", "content": "set a reminder for painting tomorrow at 9am"},
      {"role": "assistant", "content": "Could you please confirm if you would like to add a description?"}
    ]
  }'
```

### React/TypeScript

```typescript
interface Message {
  role: "user" | "assistant";
  content: string;
}

interface ChatRequest {
  message: string;
  conversation_history: Message[];
}

interface ChatResponse {
  response: string;
  success: boolean;
  error: string | null;
}

const API_BASE_URL = "https://remo-server.onrender.com";

export const chatWithRemo = async (
  message: string,
  conversationHistory: Message[] = []
): Promise<ChatResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        conversation_history: conversationHistory,
      } as ChatRequest),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return (await response.json()) as ChatResponse;
  } catch (error) {
    console.error("Error:", error);
    throw error;
  }
};

// Example usage in React component
const [messages, setMessages] = useState<Message[]>([]);
const [isLoading, setIsLoading] = useState(false);

const handleSendMessage = async (userMessage: string) => {
  setIsLoading(true);

  try {
    const result = await chatWithRemo(userMessage, messages);

    const newMessages = [
      ...messages,
      { role: "user", content: userMessage },
      { role: "assistant", content: result.response },
    ];

    setMessages(newMessages);
  } catch (error) {
    console.error("Failed to send message:", error);
  } finally {
    setIsLoading(false);
  }
};
```

### PHP

```php
<?php

class RemoAPI {
    private $baseUrl = 'https://remo-server.onrender.com';

    public function chat($message, $conversationHistory = []) {
        $url = $this->baseUrl . '/chat';

        $data = [
            'message' => $message,
            'conversation_history' => $conversationHistory
        ];

        $options = [
            'http' => [
                'header' => "Content-type: application/json\r\n",
                'method' => 'POST',
                'content' => json_encode($data)
            ]
        ];

        $context = stream_context_create($options);
        $result = file_get_contents($url, false, $context);

        if ($result === FALSE) {
            throw new Exception('Failed to connect to Remo API');
        }

        return json_decode($result, true);
    }
}

// Example usage
$remo = new RemoAPI();

$conversation = [
    ['role' => 'user', 'content' => 'Hello Remo!'],
    ['role' => 'assistant', 'content' => 'Hi! How can I help you today?']
];

try {
    $response = $remo->chat('Set a reminder for tomorrow 9am', $conversation);
    echo 'Response: ' . $response['response'] . "\n";
} catch (Exception $e) {
    echo 'Error: ' . $e->getMessage() . "\n";
}

?>
```

## Error Handling

### Common HTTP Status Codes

| Status | Description           | Solution                                 |
| ------ | --------------------- | ---------------------------------------- |
| 200    | Success               | Request processed successfully           |
| 400    | Bad Request           | Check request format and required fields |
| 500    | Internal Server Error | Server error, try again later            |
| 503    | Service Unavailable   | Server temporarily unavailable           |

### Error Response Format

```json
{
  "detail": "Error processing message: OpenAI API key not found"
}
```

### Error Handling Examples

#### JavaScript

```javascript
async function chatWithRemo(message, conversationHistory = []) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        conversation_history: conversationHistory,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || `HTTP ${response.status}`);
    }

    return data;
  } catch (error) {
    console.error("API Error:", error.message);

    // Handle specific error types
    if (error.message.includes("OpenAI API key")) {
      throw new Error("Authentication failed. Please check your API keys.");
    }

    throw error;
  }
}
```

#### Python

```python
def chat_with_remo(message, conversation_history=None):
    if conversation_history is None:
        conversation_history = []

    url = f"{API_BASE_URL}/chat"
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'message': message,
        'conversation_history': conversation_history
    }

    try:
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            error_message = error_data.get('detail', f'HTTP {response.status_code}')
            raise Exception(error_message)

    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {e}")
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON response: {e}")
```

## Best Practices

### 1. Conversation Management

```javascript
// Store conversation history in your application
let conversationHistory = [];

async function sendMessage(message) {
  try {
    const response = await chatWithRemo(message, conversationHistory);

    // Update conversation history
    conversationHistory.push(
      { role: "user", content: message },
      { role: "assistant", content: response.response }
    );

    return response;
  } catch (error) {
    console.error("Failed to send message:", error);
    throw error;
  }
}
```

### 2. Rate Limiting

```javascript
class RateLimitedRemoAPI {
  constructor(maxRequestsPerMinute = 60) {
    this.maxRequests = maxRequestsPerMinute;
    this.requests = [];
  }

  async chat(message, conversationHistory = []) {
    // Clean old requests
    const now = Date.now();
    this.requests = this.requests.filter((time) => now - time < 60000);

    // Check rate limit
    if (this.requests.length >= this.maxRequests) {
      throw new Error(
        "Rate limit exceeded. Please wait before making more requests."
      );
    }

    // Add current request
    this.requests.push(now);

    // Make API call
    return await chatWithRemo(message, conversationHistory);
  }
}
```

### 3. Retry Logic

```javascript
async function chatWithRemoWithRetry(
  message,
  conversationHistory = [],
  maxRetries = 3
) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await chatWithRemo(message, conversationHistory);
    } catch (error) {
      if (attempt === maxRetries) {
        throw error;
      }

      // Wait before retrying (exponential backoff)
      const delay = Math.pow(2, attempt) * 1000;
      await new Promise((resolve) => setTimeout(resolve, delay));
    }
  }
}
```

### 4. Input Validation

```javascript
function validateMessage(message) {
  if (!message || typeof message !== "string") {
    throw new Error("Message must be a non-empty string");
  }

  if (message.length > 1000) {
    throw new Error("Message too long. Maximum 1000 characters allowed.");
  }

  return message.trim();
}

function validateConversationHistory(history) {
  if (!Array.isArray(history)) {
    throw new Error("Conversation history must be an array");
  }

  for (const msg of history) {
    if (!msg.role || !msg.content) {
      throw new Error("Each message must have role and content fields");
    }

    if (!["user", "assistant"].includes(msg.role)) {
      throw new Error('Message role must be "user" or "assistant"');
    }
  }

  return history;
}
```

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Default**: 60 requests per minute per IP
- **Burst**: Up to 10 requests per second
- **Headers**: Rate limit information included in response headers

```javascript
// Check rate limit headers
const response = await fetch(`${API_BASE_URL}/chat`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(data),
});

const remaining = response.headers.get("X-RateLimit-Remaining");
const resetTime = response.headers.get("X-RateLimit-Reset");

console.log(`Remaining requests: ${remaining}`);
console.log(`Reset time: ${new Date(resetTime * 1000)}`);
```

## WebSocket Support

For real-time chat functionality, WebSocket support is planned for future releases. This will enable:

- Real-time message streaming
- Typing indicators
- Connection status updates
- Bi-directional communication

## Interactive API Documentation

Visit `https://remo-server.onrender.com/docs` for interactive API documentation powered by Swagger UI. This provides:

- Live API testing
- Request/response examples
- Schema documentation
- Try-it-out functionality

## Support

For API-related questions and support:

1. Check this documentation
2. Visit the interactive API docs at `/docs`
3. Open an issue on GitHub
4. Review the main README for general information

---

**Happy integrating with Remo! 🤖✨**
