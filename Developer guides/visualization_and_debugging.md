# 🕵️ Visualization & Debugging Guide

## 🎯 Learning Outcomes

- Understand how to visualize agent orchestration and conversation flows in Remo-Server
- Learn about debugging tools, test scripts, and best practices
- See how to test, debug, and optimize agent flows and memory
- Find links to orchestration, memory, and agent guides

---

## 1. Overview

Remo-Server provides tools for visualizing the multi-agent system and debugging orchestration, memory, and agent flows. This guide covers:

- Visualizing the agent orchestration graph
- Debugging conversation memory and context
- Using test scripts for reminders, todos, and feedback

---

## 2. Visualization Tools

- **`visualize_graph.py`**: Generates a PNG of the agent orchestration graph
- **Interactive API Docs**: Use `/docs` endpoint for live API testing

### Example

```bash
python visualize_graph.py
# Output: remo_multi_agent_graph.png
```

---

## 3. Debugging & Testing

- **Test Scripts**: Run `test_*.py` scripts for reminders, todos, feedback, and data isolation
- **Debug Logging**: Add print/log statements in agents, memory, and orchestration code
- **API Testing**: Use `/health` and `/chat` endpoints for live checks

### Example

```bash
python test_reminder_detection.py
python test_todo_functionality.py
python test_data_isolation.py
```

---

## 4. Best Practices

- Test with multiple users and edge cases
- Use debug logging for intent detection and routing
- Visualize agent flows after adding new agents or orchestration logic
- Use API docs for rapid endpoint testing

---

## 5. Related Guides & Next Steps

- [Orchestration & Routing Guide](./orchestration_and_routing.md)
- [Conversation Memory Guide](./conversation_memory_guide.md)
- [Creating New Agents](./creating_new_agents.md)
- [API Integration Guide](./api_integration_guide.md)

---

**For more details, see the code in `visualize_graph.py`, test scripts, and the orchestration/memory guides.**
