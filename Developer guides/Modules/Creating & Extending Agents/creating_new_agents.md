# 🛠️ Creating New Agents in Remo Multi-Agent System

## 🎯 Learning Outcomes

- Understand the architecture and role of specialized agents in Remo
- Learn the step-by-step process to add a new agent
- Integrate your agent with orchestration, memory, and user data isolation
- Follow best practices for agent design, testing, and troubleshooting
- Know where to find deeper technical details and related guides

---

## 1. Overview

Remo-Server uses a **supervisor pattern** where specialized agents handle specific domains (reminders, todos, email, etc.) and the orchestrator coordinates between them. This guide shows you how to add new agents following the established, modular architecture.

For a high-level system view, see the [Architecture Overview](./architecture_overview.md).

---

## 2. Project Structure

- `src/agents/`: Specialized agents (reminders, todos, email, etc.)
- `src/orchestration/`: Supervisor orchestrator
- `src/memory/`: Conversation memory and context management
- `src/utils/`: Shared utilities (DynamoDB, Google Calendar, etc.)
- `app.py`: Main entrypoint (API server)

---

## 3. Step-by-Step: Creating a New Agent

### 3.1 Create the Agent Directory Structure

```bash
mkdir -p src/agents/your_agent_name
```

### 3.2 Create Required Files

```
src/agents/your_agent_name/
├── __init__.py           # Package initialization
├── your_agent_name_agent.py    # Agent class and persona
└── your_agent_name_tools.py    # Agent tools and functions
```

### 3.3 Implement Agent Tools

Define your agent's core functions in `your_agent_name_tools.py`. See [reminder_tools.py](../src/agents/reminders/reminder_tools.py) or [email_tools.py](../src/agents/email/email_tools.py) for examples.

### 3.4 Create the Agent Class

Implement the agent logic and persona in `your_agent_name_agent.py`. See [reminder_agent.py](../src/agents/reminders/reminder_agent.py) or [email_agent.py](../src/agents/email/email_agent.py).

### 3.5 Update Package Initialization

Add your agent to `__init__.py` in your agent directory:

```python
from .your_agent_name_agent import YourAgentNameAgent
__all__ = ["YourAgentNameAgent"]
```

### 3.6 Register Agent in Main Agents Package

Update `src/agents/__init__.py`:

```python
from .reminders.reminder_agent import ReminderAgent
from .todo.todo_agent import TodoAgent
from .your_agent_name.your_agent_name_agent import YourAgentNameAgent
__all__ = ["ReminderAgent", "TodoAgent", "YourAgentNameAgent"]
```

### 3.7 Integrate with Orchestrator

Update `src/orchestration/supervisor.py` to import, initialize, and register your agent. See [orchestration_and_routing.md](./orchestration_and_routing.md) for details.

### 3.8 Update Routing Logic (Optional)

Add keywords for your agent in the routing logic (see `remo.py` or orchestration guide):

```python
specialized_keywords = [
    # ...existing keywords...
    # Your agent keywords
    "your_keyword1", "your_keyword2", "your_keyword3"
]
```

### 3.9 Test Your New Agent

- Run Remo: `python app.py`
- Check agent registration in the supervisor
- Test commands that should trigger your agent
- Verify agent responses and routing

---

## 4. Example: Email Agent Implementation

See [Email Assistant Guide](./email_assistant_guide.md) for a full walkthrough.

---

## 5. Best Practices

- **Single Responsibility**: Each agent should have one clear purpose
- **Consistent Interface**: Implement `get_agent()`, `get_name()`, `get_description()`
- **User Data Isolation**: Always require `user_id` for user-specific data (see [User-Specific Implementation Summary](./user_specific_implementation_summary.md))
- **Memory Integration**: Use the context and memory managers for multi-turn tasks ([Conversation Memory Guide](./conversation_memory_guide.md))
- **Testing**: Test tools and agent logic individually before integration
- **Documentation**: Document your agent's capabilities and usage

---

## 6. Troubleshooting

- **Agent not appearing**: Check imports in `src/agents/__init__.py` and supervisor registration
- **Agent not responding**: Check routing keywords and tool function signatures
- **Import errors**: Ensure all `__init__.py` files are present and import paths are correct
- **Data issues**: Verify `user_id` is passed everywhere for user-specific data

---

## 7. Next Steps & Related Guides

- [Email Assistant Guide](./email_assistant_guide.md)
- [Orchestration & Routing Guide](./orchestration_and_routing.md)
- [Conversation Memory Guide](./conversation_memory_guide.md)
- [API Integration Guide](./api_integration_guide.md)
- [User-Specific Implementation Summary](./user_specific_implementation_summary.md)
- [Visualization & Debugging](./visualization_and_debugging.md)

---

**For more details, see the code in `src/agents/`, `src/orchestration/`, and the related guides above. Happy agent building! 🚀**
