# Remo - Your Personal AI Assistant

"Remo: A personal AI Assistant that can be hired by every human on the planet. Personal assistants are not just for the rich anymore."

Now powered by multi-agent orchestration with specialized agents for reminders and todo management.
Enhanced with conversation memory for seamless multi-turn interactions.

## 🚀 Quick Start

### Option 1: CLI Mode

```bash
cd REMO-SERVER
source venv/bin/activate
python remo.py
```

### Option 2: API Mode (Recommended for Production)

```bash
cd REMO-SERVER
source venv/bin/activate
python app.py
# Server runs on http://localhost:8000
```

### Option 3: Frontend + Backend

```bash
# Backend
cd REMO-SERVER
source venv/bin/activate
python app.py

# Frontend (in new terminal)
cd REMO-APP
npm run dev:web
# Frontend runs on http://localhost:5173
```

## 🌟 Features

### 🤖 Multi-Agent Orchestration

- **Reminder Agent**: Manages reminders, alerts, and scheduled tasks
- **Todo Agent**: Handles todo lists, task organization, and project management
- **Supervisor Orchestrator**: Routes requests to appropriate specialists

### 🧠 Advanced Memory System

- **Conversation Memory**: Remembers context across interactions
- **Context Management**: Tracks conversation topics and user intent
- **Memory Persistence**: Saves conversations for future reference

### 🎯 Intelligent Routing

- **Intent Detection**: Automatically detects reminder and todo requests
- **Context-Aware Routing**: Routes based on conversation history
- **Fallback Handling**: Graceful degradation if agents fail

### 🌐 API Integration

- **FastAPI Backend**: RESTful API with automatic documentation
- **CORS Support**: Ready for frontend integration
- **Environment Variables**: Secure credential management

## 📋 Prerequisites

- Python 3.11+
- OpenAI API Key
- Node.js 18+ (for frontend)

## 🛠️ Installation

### Backend Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd REMO-SERVER

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Frontend Setup

```bash
cd REMO-APP
npm install
```

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional (for LangSmith tracing)
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=your_project_name
LANGCHAIN_TRACING_V2=true
```

### Frontend Configuration

```bash
# In REMO-APP/.env
VITE_API_URL=http://localhost:8000  # For development
VITE_API_URL=https://your-backend-url.com  # For production
```

## 🚀 Deployment

### Backend Deployment (Render)

1. Connect your GitHub repository to Render
2. Select the `REMO-SERVER` directory
3. Set environment variables in Render dashboard
4. Deploy!

### Frontend Deployment (Vercel)

1. Connect your GitHub repository to Vercel
2. Select the `REMO-APP` directory
3. Set build command: `npm run build:web`
4. Set environment variables
5. Deploy!

## 📚 API Documentation

### Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-backend-url.com`

### Endpoints

#### Health Check

```bash
GET /health
```

#### Chat Endpoint

```bash
POST /chat
Content-Type: application/json

{
  "message": "Set a reminder for tomorrow 9am",
  "conversation_history": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help you?"}
  ]
}
```

### API Examples

#### Basic Chat

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "who are you?", "conversation_history": []}'
```

#### Set Reminder

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "set a reminder for painting tomorrow at 9am", "conversation_history": []}'
```

#### Add Todo

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "add buy groceries to my todo list", "conversation_history": []}'
```

#### With Conversation History

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "yes, add description: paint the living room",
    "conversation_history": [
      {"role": "user", "content": "set a reminder for painting tomorrow at 9am"},
      {"role": "assistant", "content": "Could you please confirm if you would like to add a description?"}
    ]
  }'
```

### Interactive API Docs

Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   Remo Core     │
│   (React)       │◄──►│   Backend       │◄──►│   (LangGraph)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Agents        │
                       │   • Reminder    │
                       │   • Todo        │
                       └─────────────────┘
```

## 🔧 Development

### Running in Development

```bash
# Backend
cd REMO-SERVER
source venv/bin/activate
python app.py

# Frontend
cd REMO-APP
npm run dev:web
```

### Building for Production

```bash
# Backend
cd REMO-SERVER
pip install -r requirements.txt

# Frontend
cd REMO-APP
npm run build:web
```

## 📁 Project Structure

```
REMO-SERVER/
├── app.py                 # FastAPI server
├── remo.py               # CLI interface
├── requirements.txt      # Python dependencies
├── .env                 # Environment variables
├── src/
│   ├── agents/          # Specialized AI agents
│   │   ├── reminders/   # Reminder management
│   │   └── todo/        # Todo management
│   ├── memory/          # Conversation memory
│   ├── orchestration/   # Multi-agent coordination
│   └── utils/           # Utility functions
└── Developer guides/    # Detailed documentation

REMO-APP/
├── src/
│   ├── pages/           # React components
│   ├── components/      # Reusable components
│   └── routes/          # Application routing
├── package.json         # Node.js dependencies
└── Developer guides/    # Frontend documentation
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:

1. Check the Developer guides folder
2. Review the API documentation at `/docs`
3. Open an issue on GitHub

---

**Remo - Making personal AI assistance accessible to everyone! 🤖✨**
