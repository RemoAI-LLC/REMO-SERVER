# 🤖 Agent Orchestration & Routing

Remo uses a supervisor-based orchestration pattern to coordinate specialized agents. This guide explains how routing works and how to extend it.

## Supervisor Orchestrator

- Located in `src/orchestration/supervisor.py`.
- Initializes all specialized agents (reminders, todos, etc.).
- Uses LangGraph's `create_supervisor` to build a routing and aggregation graph.
- Handles user input, determines which agent(s) should respond, and aggregates their outputs.

## Routing Logic

- The supervisor uses keywords and context to decide which agent to invoke.
- Example: "remind me" → ReminderAgent, "add todo" → TodoAgent.
- Mixed requests are handled by invoking multiple agents in sequence.

## Extending Orchestration

- Add new agents to the supervisor by importing and initializing them.
- Update the agent list in the supervisor's `create_supervisor` call.
- Add new routing logic for additional domains or more complex workflows.

## Code Example

```python
from ..agents.email.email_agent import EmailAgent
...
self.email_agent = EmailAgent(model_name)
supervisor = create_supervisor(
    agents=[
        self.reminder_agent.get_agent(),
        self.todo_agent.get_agent(),
        self.email_agent.get_agent(),
    ],
    model=self.llm,
    prompt=supervisor_prompt
)
```

## Best Practices

- Keep agent responsibilities focused and non-overlapping.
- Use clear, specific keywords for routing.
- Test orchestration with mixed and edge-case requests.
- Use LangSmith for tracing and debugging orchestration flows.
