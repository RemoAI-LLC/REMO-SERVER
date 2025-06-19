# 🖼️ Visualization & Debugging

Remo provides tools for visualizing the multi-agent orchestration system and for debugging agent interactions.

## Visualizing the Agent Graph

- Run `python visualize_graph.py` to generate a PNG diagram of the orchestration structure.
- The script initializes the supervisor orchestrator and saves `remo_multi_agent_graph.png`.
- If run in a Jupyter notebook, the graph is displayed inline.

## Interpreting the Diagram

- The diagram shows the supervisor pattern: user input flows to Remo, then to the supervisor, then to specialized agents.
- Each agent is shown with its tools and responsibilities.
- Use the diagram to understand and debug routing and agent relationships.

## LangSmith Tracing

- All user interactions are traced in LangSmith for observability.
- Use LangSmith to monitor, debug, and optimize agent workflows.
- Check traces for errors, bottlenecks, or unexpected routing.

## Debugging Tips

- Add debug prints in agent and supervisor code to trace execution.
- Test tools and agents individually before integrating.
- Use the visualization to spot missing or misconfigured agents.
- Review LangSmith traces for detailed execution flow.

## Best Practices

- Visualize the system after adding or modifying agents.
- Use LangSmith for all major debugging and optimization efforts.
- Keep orchestration logic clear and well-documented.
