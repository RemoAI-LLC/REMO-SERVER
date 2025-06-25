"""
Todo Agent
Specialized AI agent for managing todo lists, task organization, and project management.
Uses LangGraph's create_react_agent for reasoning and tool execution.
"""

from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from .todo_tools import (
    add_todo, 
    list_todos, 
    mark_todo_complete, 
    update_todo, 
    delete_todo, 
    prioritize_todos
)

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
        self.model_name = model_name
        self.user_id = user_id
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.3,  # Lower temperature for more consistent todo management
            tags=["remo", "todo-agent"]
        )
        
        # Define the agent's specialized persona
        self.persona = """You are a todo management specialist within the Remo AI assistant ecosystem. 
Your expertise is in helping users organize, prioritize, and manage their tasks and projects effectively.

Your key characteristics:
- **Organized**: Help users structure their tasks logically
- **Proactive**: Suggest task organization and prioritization
- **Encouraging**: Motivate users to complete their tasks
- **Practical**: Provide actionable advice for task management
- **Flexible**: Adapt to different work styles and preferences

Your capabilities:
- Create and organize todo items
- Set priorities and categories
- Track task completion
- Provide task recommendations
- Help with project organization
- Suggest productivity improvements

When adding todos:
1. Ask for clear task descriptions
2. Suggest appropriate priorities
3. Help categorize tasks effectively
4. Confirm all details before creating

When organizing todos:
1. Show tasks by priority and category
2. Suggest logical task sequences
3. Help break down complex projects
4. Provide completion recommendations

When managing tasks:
1. Track progress and completion
2. Update task details as needed
3. Help prioritize when overwhelmed
4. Celebrate completed tasks

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
            """Add a new todo item with task description, priority, category, and optional due date."""
            return add_todo(task, priority, category, due_date, self.user_id)
        
        @tool
        def list_todos_wrapper(show_completed: bool = False, category: str = None) -> str:
            """List all todos, optionally filtered by completion status and category."""
            return list_todos(show_completed, category, self.user_id)
        
        @tool
        def mark_todo_complete_wrapper(todo_id: str) -> str:
            """Mark a todo item as completed."""
            return mark_todo_complete(todo_id, self.user_id)
        
        @tool
        def update_todo_wrapper(todo_id: str, task: str = None, priority: str = None, category: str = None, due_date: str = None) -> str:
            """Update an existing todo item's details."""
            return update_todo(todo_id, task, priority, category, due_date, self.user_id)
        
        @tool
        def delete_todo_wrapper(todo_id: str) -> str:
            """Delete a todo item by ID."""
            return delete_todo(todo_id, self.user_id)
        
        @tool
        def prioritize_todos_wrapper() -> str:
            """Prioritize and organize todos by importance and urgency."""
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
    
    def process(self, user_message: str, todo_details: dict = None) -> str:
        """
        Process a user message and return a response.
        
        Args:
            user_message: The user's message
            todo_details: Optional details extracted from the message
            
        Returns:
            The agent's response as a string
        """
        try:
            # Create a simple message structure for the agent
            messages = [{"role": "user", "content": user_message}]
            
            # Invoke the agent
            response = self.agent.invoke({"messages": messages})
            
            # Extract the response content
            if "messages" in response and response["messages"]:
                return response["messages"][-1].content
            else:
                return "I've processed your todo request. How else can I help you?"
                
        except Exception as e:
            return f"I encountered an error while processing your todo request: {str(e)}. Please try again." 