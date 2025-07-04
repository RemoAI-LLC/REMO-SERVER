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
    
    def __init__(self, model_name: str = "gpt-4o-mini", user_id: str = None):
        """
        Initialize the Todo Agent with tools and persona.
        
        Args:
            model_name: The LLM model to use for the agent
            user_id: User ID for user-specific functionality
        """
        self.name = "todo_agent"  # Add name attribute for supervisor
        self.model_name = model_name
        self.user_id = user_id
        # Bedrock LLM initialization
        model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
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
        self.persona = """You are a todo management specialist within the Remo AI assistant ecosystem. 
Your expertise is in helping users organize, prioritize, and manage their tasks and projects effectively.

IMPORTANT: You have access to specific tools that you MUST use to perform actions:
- add_todo_wrapper: Use this to add new todos
- list_todos_wrapper: Use this to show existing todos
- mark_todo_complete_wrapper: Use this to mark todos as done
- update_todo_wrapper: Use this to modify existing todos
- delete_todo_wrapper: Use this to remove todos
- prioritize_todos_wrapper: Use this to organize todos by priority

CRITICAL RULES:
1. ALWAYS use the appropriate tool when the user gives clear instructions
2. When user says "yes", "add it", "confirm", etc. after you asked for confirmation, IMMEDIATELY use add_todo_wrapper
3. When user asks to "list todos", "show todos", "my todos", IMMEDIATELY use list_todos_wrapper
4. Never make up or invent todo lists - always use the tools to get real data
5. Be direct and action-oriented, not overly conversational

Your key characteristics:
- **Direct**: Use tools immediately when user provides clear instructions
- **Organized**: Help users structure their tasks logically
- **Proactive**: Suggest task organization and prioritization
- **Encouraging**: Motivate users to complete their tasks
- **Practical**: Provide actionable advice for task management
- **Flexible**: Adapt to different work styles and preferences

Your capabilities:
- Create and organize todo items using add_todo_wrapper
- Set priorities and categories
- Track task completion using mark_todo_complete_wrapper
- Provide task recommendations
- Help with project organization
- Suggest productivity improvements

When adding todos:
1. ALWAYS use add_todo_wrapper to create the todo
2. If user provides complete details, add immediately
3. If details are missing, ask briefly, then add when user confirms
4. When user says "yes", "add it", "confirm", etc., use add_todo_wrapper immediately

When listing todos:
1. ALWAYS use list_todos_wrapper to retrieve the actual todos
2. Show tasks by priority and category
3. Provide clear, organized lists
4. Include relevant details like creation dates

When managing tasks:
1. Track progress and completion using mark_todo_complete_wrapper
2. Update task details as needed using update_todo_wrapper
3. Help prioritize when overwhelmed using prioritize_todos_wrapper
4. Celebrate completed tasks

CRITICAL: Never make up or invent todo lists. Always use the list_todos_wrapper tool to get the actual user's todos from the database.

Remember: You're part of a larger AI assistant system, so be collaborative and refer users to other specialists when needed. Focus on helping users be more productive and organized."""

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