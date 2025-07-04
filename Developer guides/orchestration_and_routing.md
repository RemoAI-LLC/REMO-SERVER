# 🤖 Agent Orchestration & Routing Guide

## 🎯 Learning Outcomes

- Understand how Remo-Server orchestrates multiple agents and routes user requests
- Learn the layers: intent detection, context management, and routing logic
- See how to extend, debug, or add new agents and routing rules
- Find links to related guides and code references

---

## 1. Overview

Remo-Server uses a multi-layered orchestration system to provide seamless, context-aware user experiences. The system combines:

- Intent detection (what does the user want?)
- Context management (what's the current state?)
- Routing logic (which agent should handle this?)

---

## 2. Architecture & Layers

- **Intent Detection**: `src/memory/memory_utils.py` (regex, patterns, keyword analysis)
- **Context Management**: `src/memory/context_manager.py` (tracks state, pending requests, active agent)
- **Routing Logic**: `app.py` (priority order, agent selection, direct routing for listings)
- **Supervisor Orchestrator**: `src/orchestration/supervisor.py` (coordinates all agents)

---

## 3. Routing Flow

```
User Message → Intent Detection → Context Manager → Routing Logic → Agent(s) → Response
```

- **Priority**: Intent detection > Context routing > General response
- **Direct Routing**: Listing requests ("show my todos") bypass LLM for speed/accuracy
- **Clarification Handling**: User clarifications override previous routing

---

## 4. Extending & Debugging Routing

- Add new intent patterns in `memory_utils.py`
- Update context logic in `context_manager.py`
- Register new agents in `supervisor.py` and `app.py`
- Test with various user messages and conversation flows

---

## 5. Best Practices

- Use specific, non-overlapping keywords for each agent
- Prioritize intent detection over context routing
- Test with natural language variations and edge cases
- Use direct routing for deterministic operations (listing, status checks)

---

## 6. Related Guides & Next Steps

- [Conversation Memory Guide](./conversation_memory_guide.md)
- [Creating New Agents](./creating_new_agents.md)
- [API Integration Guide](./api_integration_guide.md)
- [Intent Detection & Routing Improvements](./intent_detection_and_routing_improvements.md)

---

**For more details, see the code in `src/memory/`, `src/orchestration/`, and the API/agent guides.**
