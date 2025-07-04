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
        model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1")
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
                    self.client = boto3.client(
                        "bedrock-runtime",
                        region_name=region,
                        aws_access_key_id=access_key,
                        aws_secret_access_key=secret_key,
                    )
                def invoke(self, messages):
                    prompt = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in messages])
                    body = {
                        "prompt": prompt,
                        "max_tokens": 1024,
                        "temperature": self.temperature,
                    }
                    response = self.client.invoke_model(
                        modelId=self.model_id,
                        body=json.dumps(body),
                        contentType="application/json",
                        accept="application/json"
                    )
                    result = json.loads(response["body"].read())
                    class Result:
                        def __init__(self, content):
                            self.content = content
                    return Result(result.get("completion") or result.get("output", ""))
            self.llm = BedrockLLM(model_id, region, access_key, secret_key, temperature)
        
        # Define the agent's specialized persona
        self.persona = "You are a todo management specialist within the Remo AI assistant ecosystem."

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
        
        @tool
        def add_todo_wrapper(task: str, priority: str = "medium", category: str = "general", due_date: str = None) -> str:
            """Add a new todo item to the user's todo list. Use this when the user wants to create a new task or todo item."""
            return add_todo(task, priority, category, due_date, self.user_id)
        
        @tool
        def list_todos_wrapper(show_completed: bool = False, category: str = None) -> str:
            """List all todos from the user's todo list. Use this when the user asks to see their todos or todo list."""
            return list_todos(show_completed, category, self.user_id)
        
        @tool
        def mark_todo_complete_wrapper(todo_id: str) -> str:
            """Mark a todo item as completed. Use this when the user wants to mark a task as done."""
            return mark_todo_complete(todo_id, self.user_id)
        
        @tool
        def update_todo_wrapper(todo_id: str, task: str = None, priority: str = None, category: str = None, due_date: str = None) -> str:
            """Update an existing todo item's details. Use this when the user wants to modify a task."""
            return update_todo(todo_id, task, priority, category, due_date, self.user_id)
        
        @tool
        def delete_todo_wrapper(todo_id: str) -> str:
            """Delete a todo item by ID. Use this when the user wants to remove a task."""
            return delete_todo(todo_id, self.user_id)
        
        @tool
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
            # Create messages for the agent
            messages = []
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)
            
            # Add the current user input
            messages.append({"role": "user", "content": user_message})
            
            # Invoke the agent
            response = self.agent.invoke({"messages": messages})
            
            # Extract the response content
            if "messages" in response and response["messages"]:
                return response["messages"][-1].content
            else:
                return "I've processed your todo request. How else can I help you?"
                
        except Exception as e:
            return f"I encountered an error while processing your todo request: {str(e)}. Please try again." 

    def list_todos(self, show_completed: bool = False, category: str = None) -> str:
        """Directly list todos for the current user."""
        return list_todos(show_completed, category, self.user_id) 