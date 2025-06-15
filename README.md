# Basic Chatbot with LangGraph

This project implements a basic chatbot using LangGraph, LangChain, and LangSmith for tracing and monitoring. The implementation follows the [LangGraph tutorial](https://langchain-ai.github.io/langgraph/tutorials/get-started/1-build-basic-chatbot/).

## Project Overview

The chatbot is built using three main components:

- **LangChain**: Provides the core LLM integration and chat model functionality
- **LangGraph**: Enables building stateful, multi-agent applications with a graph-based architecture
- **LangSmith**: Offers tracing, monitoring, and debugging capabilities for the LLM application

## Prerequisites

Before starting, ensure you have:

- Access to an LLM that supports tool-calling features (OpenAI, Anthropic, or Google Gemini)
- Python 3.8+ installed
- Required API keys for your chosen LLM provider

## Core Components Explained

### 1. LangChain

LangChain is a framework for developing applications powered by language models. In our chatbot:

```python
from langchain.chat_models import init_chat_model

# Initialize the chat model
llm = init_chat_model("openai:gpt-4")

# Example of using the model
response = llm.invoke([{"role": "user", "content": "Hello!"}])
```

Key features:

- Model abstraction and management
- Message formatting and handling
- Integration with various LLM providers

### 2. LangGraph

LangGraph is a library for building stateful, multi-agent applications. It uses a graph-based architecture where:

```python
from langgraph.graph import StateGraph, START

# Define the state structure
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Create the graph
graph_builder = StateGraph(State)

# Add a node (function that processes messages)
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

# Add the node to the graph
graph_builder.add_node("chatbot", chatbot)

# Connect the entry point to the chatbot node
graph_builder.add_edge(START, "chatbot")
```

Key concepts:

- **StateGraph**: A state machine that manages the flow of data
- **Nodes**: Functions that process data and return updates to the state
- **Edges**: Define how data flows between nodes
- **State**: The current state of the conversation, including message history

### 3. LangSmith

LangSmith provides tracing and monitoring capabilities:

```python
import os
from langsmith import Client

# Set up LangSmith
os.environ["LANGCHAIN_API_KEY"] = "your_api_key"
os.environ["LANGCHAIN_PROJECT"] = "your_project"

# Traces are automatically created when running the graph
graph.stream({"messages": [{"role": "user", "content": "Hello!"}]})
```

Features:

- Real-time tracing of LLM calls
- Performance monitoring
- Debugging tools
- Trace visualization

## Step-by-Step Implementation

### 1. Install Required Packages

```bash
pip install -U langgraph langsmith
pip install -U "langchain[openai]"  # or your chosen provider
```

### 2. Create StateGraph Structure

```python
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)
```

### 3. Initialize Chat Model

```python
import os
from langchain.chat_models import init_chat_model

# Set your API key
os.environ["OPENAI_API_KEY"] = "your-api-key"

# Initialize the model
llm = init_chat_model("openai:gpt-4")
```

### 4. Create Chatbot Node

```python
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

# Add node to graph
graph_builder.add_node("chatbot", chatbot)
```

### 5. Set Up Graph Structure

```python
# Add entry point
graph_builder.add_edge(START, "chatbot")

# Compile the graph
graph = graph_builder.compile()
```

### 6. Visualize the Graph (Optional)

```python
from IPython.display import Image, display

try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    # This requires some extra dependencies and is optional
    pass
```

### 7. Implement Chat Loop

```python
def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)

while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)
    except:
        # fallback if input() is not available
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break
```

## Project Structure

```
.
├── .env                    # Environment variables
├── requirements.txt        # Project dependencies
├── chatbot.py             # Main chatbot implementation
└── README.md              # This documentation
```

## Setup

1. Create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Unix/macOS
# OR
venv\Scripts\activate     # On Windows

# To deactivate the virtual environment when you're done
deactivate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your API keys:

```
OPENAI_API_KEY=your_openai_api_key_here
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=your_project_name
```

## Implementation Details

### 1. State Management

The chatbot uses a `StateGraph` to manage conversation state:

```python
# Define the state structure
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Example of state updates
initial_state = {
    "messages": [{"role": "user", "content": "Hello!"}]
}

# State is automatically updated with new messages
updated_state = graph.invoke(initial_state)
```

Key features:

- Automatic message history management
- State persistence between interactions
- Type-safe state updates

### 2. Graph Structure

The chatbot implements a simple graph with:

```python
# Create the graph
graph_builder = StateGraph(State)

# Define the chatbot node
def chatbot(state: State):
    # Process messages and return updates
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# Add the node and connect it
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")

# Compile the graph
graph = graph_builder.compile()
```

Components:

- **Entry Point**: Where the graph starts processing
- **Nodes**: Functions that process data
- **Edges**: Define the flow between nodes
- **State Updates**: How the graph modifies the state

### 3. LangSmith Integration

The implementation includes LangSmith tracing:

```python
# Traces are automatically created
for event in graph.stream({"messages": [{"role": "user", "content": "Hello!"}]}):
    # Each event is traced in LangSmith
    print(event)
```

Features:

- Automatic trace creation
- Performance metrics
- Debug information
- Trace visualization in the dashboard

## Running the Chatbot

1. Start the chatbot:

```bash
python chatbot.py
```

2. Interact with the chatbot:

```python
# Example interaction
User: Hello!
Assistant: Hi! How can I help you today?
User: What can you do?
Assistant: I can engage in conversation, answer questions, and help with various tasks.
```

3. View traces in LangSmith:

- Visit [LangSmith Dashboard](https://smith.langchain.com)
- Navigate to your project
- View traces for each conversation

## Key Features

### 1. Stateful Conversations

```python
# Messages are automatically appended to the state
state = {
    "messages": [
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi! How can I help?"}
    ]
}
```

### 2. Streaming Responses

```python
# Real-time response streaming
for event in graph.stream(state):
    print("Assistant:", event["messages"][-1].content)
```

### 3. Tracing and Monitoring

```python
# Each interaction is traced
with Client() as client:
    run = client.create_run(
        name="chatbot_interaction",
        inputs={"messages": state["messages"]}
    )
```

### 4. Error Handling

```python
try:
    response = graph.invoke(state)
except Exception as e:
    print(f"Error: {e}")
    # Handle error gracefully
```

## Dependencies

- langgraph: For building the state machine
- langchain: For LLM integration
- langsmith: For tracing and monitoring
- python-dotenv: For environment variable management

## Next Steps

Potential improvements:

1. Add memory capabilities
2. Implement tools and function calling
3. Add human-in-the-loop features
4. Enhance error handling and recovery
5. Add conversation persistence

## Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)
- [LangSmith Documentation](https://docs.smith.langchain.com/)
