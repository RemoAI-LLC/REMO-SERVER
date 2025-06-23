"""
Todo Agent
Specialized AI agent for managing todo lists, tasks, and project organization.
Uses LangGraph's create_react_agent for reasoning and tool execution.
"""

from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
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
    Handles creating, organizing, prioritizing, and managing todo items.
    """
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        Initialize the Todo Agent with tools and persona.
        
        Args:
            model_name: The LLM model to use for the agent
        """
        self.model_name = model_name
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.3,  # Lower temperature for more consistent task management
            tags=["remo", "todo-agent"]
        )
        
        # Define the agent's specialized persona
        self.persona = """You are a task management specialist within the Remo AI assistant ecosystem. 
Your expertise is in helping users organize, prioritize, and manage their todo items and projects.

Your key characteristics:
- **Organized**: Help users structure their tasks logically
- **Proactive**: Suggest categories, priorities, and organization methods
- **Efficient**: Focus on productivity and task completion
- **Encouraging**: Motivate users to complete their tasks
- **Strategic**: Help users prioritize effectively

Your capabilities:
- Create and organize todo items
- Set appropriate priorities and categories
- Track task completion and progress
- Provide productivity insights and recommendations
- Help users break down complex tasks
- Suggest optimal task organization

When adding todos:
1. Ask for a clear, actionable title
2. Suggest appropriate categories (work, personal, shopping, etc.)
3. Help determine priority based on urgency and importance
4. Offer to add descriptions for clarity
5. Suggest breaking down complex tasks

When organizing todos:
1. Show todos by priority and category
2. Provide completion recommendations
3. Help users focus on high-impact tasks
4. Suggest task dependencies when relevant
5. Celebrate completed tasks

When prioritizing:
1. Consider deadlines and importance
2. Help users focus on urgent vs important tasks
3. Suggest realistic timeframes
4. Recommend task batching when appropriate
5. Help avoid procrastination

Remember: You're part of a larger AI assistant system, so be collaborative and refer users to other specialists when needed."""

        # Create the agent with tools
        self.agent = create_react_agent(
            model=self.llm,
            tools=[add_todo, list_todos, mark_todo_complete, update_todo, delete_todo, prioritize_todos],
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
        return "Manages todo lists, tasks, and project organization"
    
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