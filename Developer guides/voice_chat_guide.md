# 🎤 Voice Chat Integration Guide

## 🎯 Learning Outcomes

- Understand how voice input and speech recognition are integrated in Remo-Server and REMO-APP
- Learn about the Web Speech API, backend handling, and multi-turn memory
- See how to implement, debug, or extend voice features
- Find links to frontend, API, and memory guides

---

## 1. Overview

Remo supports voice input via the Web Speech API in the frontend (REMO-APP) and multi-turn memory/context in the backend (REMO-SERVER). This enables:

- Voice-to-text chat with Remo
- Multi-turn, context-aware conversations
- Seamless integration with reminders, todos, and email agents

---

## 2. Frontend Voice Input

- Uses the [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
- Handles microphone permissions, transcript, and error states
- Sends recognized text to the backend `/chat` endpoint

### Example (REMO-APP/src/pages/Home.tsx):

```tsx
recognitionRef.current = new SpeechRecognition();
recognitionRef.current.onresult = (event) => {
  setTranscript(event.results[0][0].transcript);
  setInputText(event.results[0][0].transcript);
};
```

---

## 3. Backend Handling

- Receives voice input as normal chat messages
- Uses conversation memory for multi-turn context
- Handles reminders, todos, and email via intent detection

---

## 4. Debugging & Best Practices

- Test on HTTPS or localhost (Web Speech API requires secure context)
- Handle microphone permissions and browser compatibility
- Use debug logging for transcript and API calls
- Test multi-turn flows (e.g., "Set a reminder for tomorrow" → "6am")

---

## 5. Related Guides & Next Steps

- [Frontend Integration Guide](../../REMO-APP/)
- [API Integration Guide](./api_integration_guide.md)
- [Conversation Memory Guide](./conversation_memory_guide.md)
- [Orchestration & Routing Guide](./orchestration_and_routing.md)

---

**For more details, see the code in `REMO-APP/src/pages/Home.tsx`, backend `/chat` endpoint, and the memory/orchestration guides.**
