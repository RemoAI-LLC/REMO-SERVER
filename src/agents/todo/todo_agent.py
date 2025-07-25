"""
Todo Agent
Specialized AI agent for managing todo lists, task organization, and project management.
Uses LangGraph's create_react_agent for reasoning and tool execution.
"""

from langgraph.prebuilt import create_react_agent
try:
    from langchain_aws import ChatBedrock
except ImportError:
    ChatBedrock = None
import boto3
import os
import json
from langchain.tools import tool
from .todo_tools import (
    add_todo, 
    list_todos, 
    mark_todo_complete, 
    update_todo, 
    delete_todo, 
    prioritize_todos
)
from typing import List, Dict
from langsmith import traceable

class TodoAgent:
    """
    Specialized agent for todo management with focused expertise.
    Handles creating, organizing, and managing todo items and tasks.
    """
    
    def __init__(self, user_id: str = None):
        """
        Initialize the Todo Agent with tools and persona.
        
        Args:
            user_id: User ID for user-specific functionality
        """
        self.name = "todo_agent"
        self.user_id = user_id
        # Bedrock LLM initialization
        model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")
        region = os.getenv("AWS_REGION", "us-east-1")
        access_key = os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        temperature = 0.3
        if ChatBedrock:
            self.llm = ChatBedrock(
                model_id=model_id,
                region_name=region,
                model_kwargs={"temperature": temperature}
            )
        else:
            class BedrockLLM:
                def __init__(self, model_id, region, access_key, secret_key, temperature):
                    self.model_id = model_id
                    self.temperature = temperature
                    print(f"[BedrockLLM] Initializing with model_id={model_id}, region={region}")
                    self.client = boto3.client(
                        "bedrock-runtime",
                        region_name=region,
                        aws_access_key_id=access_key,
                        aws_secret_access_key=secret_key,
                    )
                def invoke(self, messages):
                    # Ensure content is a list of objects with 'text' for each message
                    for m in messages:
                        if isinstance(m.get("content"), str):
                            m["content"] = [{"text": m["content"]}]
                        elif isinstance(m.get("content"), list):
                            m["content"] = [c if isinstance(c, dict) else {"text": c} for c in m["content"]]
                    print(f"[BedrockLLM] Invoking model {self.model_id} with messages: {messages}")
                    body = {
                        "messages": messages
                    }
                    try:
                        response = self.client.invoke_model(
                            modelId=self.model_id,
                            body=json.dumps(body),
                            contentType="application/json",
                            accept="application/json"
                        )
                        result = json.loads(response["body"].read())
                        print(f"[BedrockLLM] Response: {str(result)[:200]}")
                        class Result:
                            def __init__(self, content):
                                self.content = content
                        return Result(result.get("completion") or result.get("output", ""))
                    except Exception as e:
                        print(f"[BedrockLLM] ERROR: {e}")
                        raise
            self.llm = BedrockLLM(model_id, region, access_key, secret_key, temperature)
        
        # Define the agent's specialized persona
        self.persona = (
            "You are a todo management specialist within the Remo AI assistant ecosystem. "
            "For any request to list todos, you must always use the list_todos tool. Never generate a list yourself."
        )

        # Create user-specific tool wrappers
        self.tools = self._create_user_specific_tools()
        
        # Create the agent with tools
        self.agent = create_react_agent(
            model=self.llm,
            tools=self.tools,
            prompt=self.persona,
            name="todo_agent"
        )
    
    def _create_user_specific_tools(self):
        """Create tool wrappers that automatically include the user_id"""
        @traceable
        def add_todo_wrapper(task: str, priority: str = "medium", category: str = "general", due_date: str = None) -> str:
            """Add a new todo item to the user's todo list. Use this when the user wants to create a new task or todo item."""
            return add_todo(task, priority, category, due_date, self.user_id)
        
        @traceable
        def list_todos_wrapper(show_completed: bool = False, category: str = None) -> str:
            """List all todos from the user's todo list. Use this when the user asks to see their todos or todo list."""
            return list_todos(show_completed, category, self.user_id)
        
        @traceable
        def mark_todo_complete_wrapper(todo_id: str) -> str:
            """Mark a todo item as completed. Use this when the user wants to mark a task as done."""
            return mark_todo_complete(todo_id, self.user_id)
        
        @traceable
        def update_todo_wrapper(todo_id: str = None, task: str = None, priority: str = None, category: str = None, due_date: str = None) -> str:
            """Update an existing todo item's details. Use this when the user wants to modify a task."""
            return update_todo(todo_id, task, priority, category, due_date, self.user_id)
        
        @traceable
        def delete_todo_wrapper(todo_id: str) -> str:
            """Delete a todo item by ID. Use this when the user wants to remove a task."""
            return delete_todo(todo_id, self.user_id)
        
        @traceable
        def prioritize_todos_wrapper() -> str:
            """Prioritize and organize todos by importance and urgency. Use this when the user wants to see organized todos."""
            return prioritize_todos(self.user_id)
        
        return [
            add_todo_wrapper,
            list_todos_wrapper,
            mark_todo_complete_wrapper,
            update_todo_wrapper,
            delete_todo_wrapper,
            prioritize_todos_wrapper
        ]
    
    def set_user_id(self, user_id: str):
        """Set the user ID for user-specific functionality"""
        self.user_id = user_id
        # Recreate tools with new user_id
        self.tools = self._create_user_specific_tools()
        # Recreate agent with new tools
        self.agent = create_react_agent(
            model=self.llm,
            tools=self.tools,
            prompt=self.persona,
            name="todo_agent"
        )
    
    def get_agent(self):
        """Get the compiled agent for use in orchestration"""
        return self.agent
    
    def get_name(self) -> str:
        """Get the agent's name for routing"""
        return "todo_agent"
    
    def get_description(self) -> str:
        """Get a description of what this agent does"""
        return "Handles todo lists, task organization, and project management" 
    
    def process(self, user_message: str, conversation_history: List[Dict] = None, todo_details: dict = None) -> str:
        """
        Process a user message and return a response.
        
        Args:
            user_message: The user's message
            conversation_history: Previous conversation messages for context
            todo_details: Optional details extracted from the message
            
        Returns:
            The agent's response as a string
        """
        try:
            print(f"[TodoAgent] process called with user_message: {user_message}")
            # If the message is an add todo intent, call add_todo directly and return a final message
            add_keywords = ["add todo", "add to do", "add task", "create todo", "new todo", "add", "create"]
            if any(kw in user_message.lower() for kw in add_keywords):
                # Naive extraction: use the whole message as the task
                task = user_message
                result = self.tools[0](task=task)  # add_todo_wrapper is the first tool
                print(f"[TodoAgent] add_todo tool result: {result}")
                # Always return a final, explicit confirmation
                return f"✅ Todo added! {result}\nIf you want to add another, just tell me the task. To see your todos, say 'list my todos'."
            # Otherwise, use the normal agent invoke flow
            messages = []
            if conversation_history:
                for msg in conversation_history:
                    if isinstance(msg.get("content"), str):
                        msg["content"] = [{"text": msg["content"]}]
                    elif isinstance(msg.get("content"), list):
                        msg["content"] = [c if isinstance(c, dict) else {"text": c} for c in msg["content"]]
                    messages.append(msg)
            messages.append({"role": "user", "content": [{"text": user_message}]})
            response = self.agent.invoke({"messages": messages})
            print(f"[TodoAgent] agent.invoke response: {response}")
            if "messages" in response and response["messages"]:
                print(f"[TodoAgent] Returning response: {response['messages'][-1].content}")
                return response["messages"][-1].content
            else:
                print("[TodoAgent] No messages in response, returning fallback.")
                return "I've processed your todo request. How else can I help you?"
        except Exception as e:
            print(f"[TodoAgent] Exception in process: {e}")
            return f"I encountered an error while processing your todo request: {str(e)}. Please try again."

    def list_todos(self, show_completed: bool = False, category: str = None) -> str:
        """Directly list todos for the current user."""
        print(f"[TodoAgent] list_todos called for user_id={self.user_id}, show_completed={show_completed}, category={category}")
        result = list_todos(show_completed, category, self.user_id)
        print(f"[TodoAgent] list_todos result: {result}")
        return result 