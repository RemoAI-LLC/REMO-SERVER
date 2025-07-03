"""
Reminder Agent
Specialized AI agent for managing reminders, alerts, and scheduled tasks.
Uses LangGraph's create_react_agent for reasoning and tool execution.
"""

from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from .reminder_tools import (
    set_reminder, 
    list_reminders, 
    update_reminder, 
    delete_reminder, 
    mark_reminder_complete
)
from typing import List, Dict

class ReminderAgent:
    """
    Specialized agent for reminder management with focused expertise.
    Handles creating, listing, updating, and managing reminders.
    """
    
    def __init__(self, model_name: str = "gpt-4o-mini", user_id: str = None):
        """
        Initialize the Reminder Agent with tools and persona.
        
        Args:
            model_name: The LLM model to use for the agent
            user_id: User ID for user-specific functionality
        """
        self.name = "reminder_agent"  # Add name attribute for supervisor
        self.model_name = model_name
        self.user_id = user_id
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.3,  # Lower temperature for more consistent reminder management
            tags=["remo", "reminder-agent"]
        )
        
        # Define the agent's specialized persona
        self.persona = """You are a reminder management specialist within the Remo AI assistant ecosystem. 
Your expertise is in helping users set, manage, and track reminders for important tasks and events.

Your key characteristics:
- **Precise**: Always confirm details like time, date, and description
- **Organized**: Keep reminders well-structured and easy to understand
- **Proactive**: Suggest helpful reminder details when users are vague
- **Friendly**: Maintain a warm, helpful tone while being professional
- **Thorough**: Ask clarifying questions when needed

Your capabilities:
- Set reminders with specific times and dates
- List and organize existing reminders
- Update reminder details
- Mark reminders as completed
- Delete unnecessary reminders
- Suggest optimal reminder times

When setting reminders:
1. Always confirm the exact time and date
2. Ask for a description if not provided
3. Suggest appropriate timing if user is vague
4. Provide clear confirmation of what was set

When listing reminders:
1. Show active reminders by default
2. Include relevant details (time, description)
3. Organize by urgency/chronological order
4. Offer to show completed reminders if requested

Remember: You're part of a larger AI assistant system, so be collaborative and refer users to other specialists when needed."""

        # Create user-specific tool wrappers
        self.tools = self._create_user_specific_tools()
        
        # Create the agent with tools
        self.agent = create_react_agent(
            model=self.llm,
            tools=self.tools,
            prompt=self.persona,
            name="reminder_agent"
        )
    
    def _create_user_specific_tools(self):
        """Create tool wrappers that automatically include the user_id"""
        
        @tool
        def set_reminder_wrapper(title: str, datetime_str: str, description: str = "") -> str:
            """Set a new reminder with title, datetime, and optional description."""
            return set_reminder(title, datetime_str, description, self.user_id)
        
        @tool
        def list_reminders_wrapper(show_completed: bool = False) -> str:
            """List all reminders, optionally including completed ones."""
            return list_reminders(show_completed, self.user_id)
        
        @tool
        def update_reminder_wrapper(reminder_id: str, title: str = None, datetime_str: str = None, description: str = None) -> str:
            """Update an existing reminder's details."""
            return update_reminder(reminder_id, title, datetime_str, description, self.user_id)
        
        @tool
        def delete_reminder_wrapper(reminder_id: str) -> str:
            """Delete a reminder by ID."""
            return delete_reminder(reminder_id, self.user_id)
        
        @tool
        def mark_reminder_complete_wrapper(reminder_id: str) -> str:
            """Mark a reminder as completed."""
            return mark_reminder_complete(reminder_id, self.user_id)
        
        return [
            set_reminder_wrapper,
            list_reminders_wrapper,
            update_reminder_wrapper,
            delete_reminder_wrapper,
            mark_reminder_complete_wrapper
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
            name="reminder_agent"
        )
    
    def get_agent(self):
        """Get the compiled agent for use in orchestration"""
        return self.agent
    
    def get_name(self) -> str:
        """Get the agent's name for routing"""
        return "reminder_agent"
    
    def get_description(self) -> str:
        """Get a description of what this agent does"""
        return "Manages reminders, alerts, and scheduled tasks" 
    
    def process(self, user_message: str, conversation_history: List[Dict] = None, reminder_details: dict = None) -> str:
        """
        Process a user message and return a response.
        
        Args:
            user_message: The user's message
            conversation_history: Previous conversation messages for context
            reminder_details: Optional details extracted from the message
            
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
                return "I've processed your reminder request. How else can I help you?"
                
        except Exception as e:
            return f"I encountered an error while processing your reminder request: {str(e)}. Please try again." 

    def list_reminders(self, show_completed: bool = False) -> str:
        """Directly list reminders for the current user."""
        return list_reminders(show_completed, self.user_id) 