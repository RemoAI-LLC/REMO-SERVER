# 🏗️ Remo Architecture Overview

Remo is a multi-agent orchestration system designed for extensibility, clarity, and developer productivity. It leverages modern AI frameworks to coordinate specialized agents for personal assistance tasks.

## System Components

- **Agents**: Specialized, focused on a single domain (e.g., reminders, todos). Each agent has its own tools and persona.
- **Supervisor Orchestrator**: Routes user requests to the right agent(s) and aggregates responses. Implements the supervisor pattern using LangGraph.
- **Remo Entrypoint**: The main CLI and user interface, handling input/output and coordinating with the supervisor.
- **Visualization**: Tools to visualize the orchestration graph and agent relationships.
- **State Management**: Shared state for message passing and context across agents.

## Technology Stack

- **LangChain**: For LLM integration and tool execution.
- **LangGraph**: For multi-agent orchestration and graph-based workflows.
- **LangSmith**: For tracing, debugging, and monitoring agent interactions.

## How It Works

1. **User Input**: User interacts with Remo via CLI or other interface.
2. **Supervisor Orchestrator**: Receives input, determines which agent(s) should handle the request.
3. **Agents**: Each agent processes its part of the request using its tools and persona.
4. **Aggregation**: Supervisor combines responses and returns a coordinated answer to the user.

## System Diagram

```mermaid
graph TD
    User["User Input"] --> Remo["Remo Entrypoint"]
    Remo --> Supervisor["Supervisor Orchestrator"]
    Supervisor --> ReminderAgent["Reminder Agent"]
    Supervisor --> TodoAgent["Todo Agent"]
    ReminderAgent -- tools --> ReminderTools["Reminder Tools"]
    TodoAgent -- tools --> TodoTools["Todo Tools"]
    Supervisor -->|future| OtherAgents["Other Specialized Agents"]
    Supervisor -->|aggregates| Remo
```

## Extensibility

- Add new agents by following the agent template and registering them with the supervisor.
- Extend orchestration logic for more complex workflows.
- Visualize and debug using provided tools.

---

See the other guides for details on building, extending, and debugging the system.
