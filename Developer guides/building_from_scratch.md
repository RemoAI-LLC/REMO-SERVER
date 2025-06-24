# 🚀 Building Remo from Scratch

Follow these steps to set up and run the Remo multi-agent system from a fresh environment.

## 1. Clone the Repository

```bash
git clone <your-repo-url>
cd Lang-Agent
```

## 2. Set Up a Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Set Up Environment Variables

- Create a `.env` file in the project root.
- Add your OpenAI API key:

```
OPENAI_API_KEY=sk-...
```

## 5. Understand the Project Structure

- `src/agents/`: Specialized agents (reminders, todos, etc.)
- `src/orchestration/`: Supervisor orchestrator
- `src/utils/`: Shared utilities
- `app.py`: Main entrypoint (API server)
- `visualize_graph.py`: Visualizes the agent orchestration graph
- `Developer guides/`: Developer documentation

## 6. Run the API Server

```bash
python app.py
```

- The server runs on http://localhost:8000
- Use the `/docs` endpoint for interactive API documentation.

## 7. Visualize the System

```bash
python visualize_graph.py
```

- Generates `remo_multi_agent_graph.png` showing the orchestration structure.

## 8. Next Steps

- [Create new agents](./creating_new_agents.md)
- [Understand the architecture](./architecture_overview.md)
- [Debug and visualize](./visualization_and_debugging.md)
