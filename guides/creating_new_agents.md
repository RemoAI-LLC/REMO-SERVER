# 📧 Creating New Agents in Remo Multi-Agent System

This guide provides step-by-step instructions for adding new specialized agents to the Remo multi-agent orchestration system.

## 🎯 Overview

Remo uses a **supervisor pattern** where specialized agents handle specific domains while Remo coordinates between them. This guide shows you how to add new agents following the established architecture.

## 📁 Current Agent Structure

```
src/
├── agents/
│   ├── reminders/          # Reminder management
│   │   ├── __init__.py
│   │   ├── reminder_agent.py
│   │   └── reminder_tools.py
│   ├── todo/              # Todo management
│   │   ├── __init__.py
│   │   ├── todo_agent.py
│   │   └── todo_tools.py
│   └── __init__.py
├── orchestration/
│   └── supervisor.py      # Coordinates all agents
└── utils/
    └── state.py
```

## 🚀 Step-by-Step Guide

### Step 1: Create the Agent Directory Structure

Create a new folder for your agent in `src/agents/`:

```bash
mkdir -p src/agents/your_agent_name
```

**Example for Email Agent:**

```bash
mkdir -p src/agents/email
```

### Step 2: Create Required Files

Create these three files in your agent directory:

```
src/agents/your_agent_name/
├── __init__.py           # Package initialization
├── your_agent_name_agent.py    # Agent class and persona
└── your_agent_name_tools.py    # Agent tools and functions
```

**Example for Email Agent:**

```
src/agents/email/
├── __init__.py
├── email_agent.py
└── email_tools.py
```

### Step 3: Implement Agent Tools

Create `your_agent_name_tools.py` with functions your agent will use:

```python
"""
Your Agent Name Tools
Provides functions for [describe what your agent does].
Uses [describe storage/dependencies] for demonstration purposes.
"""

from typing import Dict, List, Optional
from datetime import datetime
import json
import os

# Storage file for your agent's data
YOUR_AGENT_STORAGE_FILE = "your_agent_data.json"

def _load_data() -> Dict[str, List[Dict]]:
    """Load data from storage file"""
    if os.path.exists(YOUR_AGENT_STORAGE_FILE):
        try:
            with open(YOUR_AGENT_STORAGE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"items": []}
    return {"items": []}

def _save_data(data: Dict[str, List[Dict]]):
    """Save data to storage file"""
    with open(YOUR_AGENT_STORAGE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def your_main_function(param1: str, param2: str = "") -> str:
    """
    Main function for your agent's primary capability.

    Args:
        param1: Description of first parameter
        param2: Description of second parameter (optional)

    Returns:
        Confirmation message with details
    """
    try:
        # Your implementation here
        result = f"✅ Successfully processed: {param1}"

        # Save to storage if needed
        data = _load_data()
        data["items"].append({
            "id": f"item_{len(data['items']) + 1}",
            "param1": param1,
            "param2": param2,
            "created": datetime.now().isoformat()
        })
        _save_data(data)

        return result

    except Exception as e:
        return f"❌ Failed to process: {str(e)}"

def list_items(filter_param: str = None) -> str:
    """
    List items managed by your agent.

    Args:
        filter_param: Optional filter parameter

    Returns:
        Formatted list of items
    """
    data = _load_data()
    items = data["items"]

    if not items:
        return "📝 No items found."

    # Apply filters if needed
    if filter_param:
        items = [item for item in items if filter_param.lower() in str(item).lower()]

    if not items:
        return "📝 No items match your criteria."

    result = "📋 Your Items:\n\n"
    for item in items:
        result += f"• {item.get('param1', 'Unknown')}\n"
        if item.get('param2'):
            result += f"  📝 {item['param2']}\n"
        result += f"  📅 Created: {datetime.fromisoformat(item['created']).strftime('%Y-%m-%d %H:%M')}\n\n"

    return result

# Add more functions as needed for your agent's capabilities
```

### Step 4: Create the Agent Class

Create `your_agent_name_agent.py` with the agent implementation:

```python
"""
Your Agent Name Agent
Specialized AI agent for [describe your agent's purpose].
Uses LangGraph's create_react_agent for reasoning and tool execution.
"""

from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from .your_agent_name_tools import (
    your_main_function,
    list_items
    # Import all your tools here
)

class YourAgentNameAgent:
    """
    Specialized agent for [your agent's purpose] with focused expertise.
    Handles [describe main capabilities].
    """

    def __init__(self, model_name: str = "gpt-4"):
        """
        Initialize the Your Agent Name Agent with tools and persona.

        Args:
            model_name: The LLM model to use for the agent
        """
        self.model_name = model_name
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.3,  # Adjust temperature based on your agent's needs
            tags=["remo", "your-agent-name-agent"]
        )

        # Define the agent's specialized persona
        self.persona = """You are a [your domain] specialist within the Remo AI assistant ecosystem.
Your expertise is in [describe what your agent specializes in].

Your key characteristics:
- **Characteristic 1**: Description
- **Characteristic 2**: Description
- **Characteristic 3**: Description

Your capabilities:
- Capability 1
- Capability 2
- Capability 3

When handling requests:
1. First step
2. Second step
3. Third step

Remember: You're part of a larger AI assistant system, so be collaborative and refer users to other specialists when needed."""

        # Create the agent with tools
        self.agent = create_react_agent(
            model=self.llm,
            tools=[your_main_function, list_items],  # Add all your tools here
            prompt=self.persona,
            name="your_agent_name_agent"
        )

    def get_agent(self):
        """Get the compiled agent for use in orchestration"""
        return self.agent

    def get_name(self) -> str:
        """Get the agent's name for routing"""
        return "your_agent_name_agent"

    def get_description(self) -> str:
        """Get a description of what this agent does"""
        return "Describes what your agent does"
```

### Step 5: Update Package Initialization

Create `__init__.py` in your agent directory:

```python
"""
Your Agent Name Package
Specialized agent for [describe your agent's purpose].
"""

from .your_agent_name_agent import YourAgentNameAgent

__all__ = ["YourAgentNameAgent"]
```

### Step 6: Register Agent in Main Agents Package

Update `src/agents/__init__.py`:

```python
"""
Agents Package
Contains specialized AI agents for different tasks.
Each agent has focused expertise and tools for their specific domain.
"""

from .reminders.reminder_agent import ReminderAgent
from .todo.todo_agent import TodoAgent
from .your_agent_name.your_agent_name_agent import YourAgentNameAgent  # Add this line

__all__ = ["ReminderAgent", "TodoAgent", "YourAgentNameAgent"]  # Add to list
```

### Step 7: Integrate with Orchestrator

Update `src/orchestration/supervisor.py`:

#### A. Import the new agent:

```python
from ..agents.your_agent_name.your_agent_name_agent import YourAgentNameAgent
```

#### B. Initialize in `SupervisorOrchestrator.__init__`:

```python
# Initialize specialized agents
self.reminder_agent = ReminderAgent(model_name)
self.todo_agent = TodoAgent(model_name)
self.your_agent_name_agent = YourAgentNameAgent(model_name)  # Add this line
```

#### C. Add to supervisor creation:

```python
supervisor = create_supervisor(
    agents=[
        self.reminder_agent.get_agent(),
        self.todo_agent.get_agent(),
        self.your_agent_name_agent.get_agent(),  # Add this line
    ],
    model=self.llm,
    prompt=supervisor_prompt
)
```

#### D. Update `get_agent_info`:

```python
return {
    "reminder_agent": self.reminder_agent.get_description(),
    "todo_agent": self.todo_agent.get_description(),
    "your_agent_name_agent": self.your_agent_name_agent.get_description(),  # Add this line
}
```

### Step 8: Update Routing Logic (Optional)

Update `remo.py` to include keywords for your new agent:

```python
specialized_keywords = [
    # Reminder-related keywords
    "reminder", "remind", "alert", "schedule", "appointment", "alarm", "wake up", "meeting",
    "set", "create", "add reminder", "set reminder", "set alarm", "set appointment",

    # Todo-related keywords
    "todo", "task", "project", "organize", "prioritize", "complete", "add to", "add todo",
    "to do", "to-do", "checklist", "list", "add task", "create task", "mark complete",
    "finish", "done", "complete task", "todo list", "task list",

    # Your agent keywords
    "your_keyword1", "your_keyword2", "your_keyword3"  # Add your agent's keywords
]
```

### Step 9: Test Your New Agent

1. **Run Remo:**

   ```bash
   python remo.py
   ```

2. **Check agent registration:**

   - You should see your new agent listed in the "Available Specialists" section

3. **Test functionality:**
   - Try commands that should trigger your agent
   - Check if routing works correctly
   - Verify agent responses

## 📋 Example: Email Agent Implementation

Here's a complete example for an Email Agent:

### `src/agents/email/email_tools.py`:

```python
"""
Email Tools
Provides functions for sending, reading, and managing emails.
"""

def send_email(to: str, subject: str, body: str) -> str:
    """Send an email"""
    return f"✅ Email sent to {to} with subject '{subject}'"

def list_emails(folder: str = "inbox") -> str:
    """List emails in a folder"""
    return f"📧 Listing emails in {folder} folder"

def read_email(email_id: str) -> str:
    """Read a specific email"""
    return f"📖 Reading email with ID {email_id}"
```

### `src/agents/email/email_agent.py`:

```python
"""
Email Agent
Specialized AI agent for managing emails.
"""

from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from .email_tools import send_email, list_emails, read_email

class EmailAgent:
    def __init__(self, model_name: str = "gpt-4"):
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.3,
            tags=["remo", "email-agent"]
        )

        self.persona = """You are an email management specialist within the Remo AI assistant ecosystem.
Your expertise is in helping users send, read, and organize their emails efficiently.

Your key characteristics:
- **Efficient**: Help users manage emails quickly and effectively
- **Organized**: Keep email management structured and clear
- **Secure**: Always prioritize email security and privacy
- **Helpful**: Provide clear guidance on email best practices

Your capabilities:
- Send emails with proper formatting
- List and organize emails by folder
- Read and summarize email content
- Manage email priorities and categories

When handling email requests:
1. Confirm email details (recipient, subject, content)
2. Ensure proper formatting and security
3. Provide clear confirmation of actions taken
4. Offer follow-up suggestions when appropriate

Remember: You're part of a larger AI assistant system, so be collaborative and refer users to other specialists when needed."""

        self.agent = create_react_agent(
            model=self.llm,
            tools=[send_email, list_emails, read_email],
            prompt=self.persona,
            name="email_agent"
        )

    def get_agent(self):
        return self.agent

    def get_name(self) -> str:
        return "email_agent"

    def get_description(self) -> str:
        return "Manages email sending, reading, and organization"
```

## 🎯 Best Practices

### 1. **Agent Design**

- **Single Responsibility**: Each agent should have one clear purpose
- **Focused Expertise**: Specialize in a specific domain
- **Clear Persona**: Define a distinct personality and capabilities
- **Consistent Interface**: Follow the established pattern with `get_agent()`, `get_name()`, `get_description()`

### 2. **Tool Implementation**

- **Error Handling**: Always include try-catch blocks
- **Validation**: Validate inputs before processing
- **Persistence**: Use appropriate storage (JSON files for simple data, databases for complex)
- **Clear Responses**: Provide informative, user-friendly responses

### 3. **Integration**

- **Consistent Naming**: Use consistent naming conventions
- **Proper Imports**: Ensure all imports are correct
- **Testing**: Test thoroughly before deployment
- **Documentation**: Document your agent's capabilities

### 4. **Keywords for Routing**

- **Specific**: Use specific keywords that clearly indicate your agent's domain
- **Comprehensive**: Include variations and synonyms
- **Non-conflicting**: Avoid keywords that might conflict with other agents

## 🔧 Troubleshooting

### Common Issues:

1. **Agent not appearing in list:**

   - Check that agent is properly imported in `src/agents/__init__.py`
   - Verify agent is initialized in `SupervisorOrchestrator`

2. **Agent not responding to requests:**

   - Check keyword routing in `remo.py`
   - Verify agent tools are working correctly
   - Check for errors in agent initialization

3. **Import errors:**
   - Ensure all `__init__.py` files are properly configured
   - Check import paths are correct
   - Verify file names match import statements

### Debug Tips:

1. **Add debug prints** to see what's happening:

   ```python
   print(f"DEBUG: Agent {agent_name} initialized")
   ```

2. **Test tools individually** before integrating:

   ```python
   from src.agents.your_agent.your_agent_tools import your_function
   result = your_function("test")
   print(result)
   ```

3. **Check LangSmith traces** for detailed execution flow

## 📚 Additional Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangGraph Supervisor Guide](https://langchain-ai.github.io/langgraph/agents/multi-agent/)
- [LangChain Tools Documentation](https://langchain-ai.github.io/langgraph/agents/tools/)

---

**Happy agent building! 🚀**
