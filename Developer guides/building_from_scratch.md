# 🚀 Building Remo from Scratch

## 🎯 Learning Outcomes

- Set up Remo-Server from a fresh environment
- Understand the project structure and key files
- Run the API server and visualize the agent system
- Know where to go next for deeper learning

---

## 1. Clone the Repository

```bash
git clone <your-repo-url>
cd REMO-SERVER
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

- Copy `.env.example` to `.env` and fill in your API keys:

```
cp env.example .env
# Edit .env and add your OpenAI, AWS, and Google credentials
```

## 5. Understand the Project Structure

- `src/agents/`: Specialized agents (reminders, todos, email, etc.)
- `src/orchestration/`: Supervisor orchestrator
- `src/memory/`: Conversation memory and context management
- `src/utils/`: Shared utilities (DynamoDB, Google Calendar, etc.)
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
- [API Integration Guide](./api_integration_guide.md)

---

**You are now ready to start building with Remo-Server!**
