"""
Supervisor Orchestrator
Coordinates multiple specialized agents using LangGraph's supervisor pattern.
Routes user requests to appropriate agents and aggregates responses.
Enhanced with memory integration for better context awareness.
"""

from typing import List, Dict, Any
from langgraph_supervisor import create_supervisor
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from ..agents.reminders.reminder_agent import ReminderAgent
from ..agents.todo.todo_agent import TodoAgent
from ..agents.email.email_agent import EmailAgent

class SupervisorOrchestrator:
    """
    Supervisor-based multi-agent orchestrator that coordinates specialized agents.
    Routes user requests to appropriate agents and manages the overall conversation flow.
    Enhanced with memory integration for better context awareness.
    """
    
    def __init__(self, model_name: str = "gpt-4o-mini", user_id: str = None):
        """
        Initialize the supervisor orchestrator with specialized agents.
        
        Args:
            model_name: The LLM model to use for the supervisor
            user_id: User ID for user-specific functionality
        """
        self.model_name = model_name
        self.user_id = user_id
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.5,  # Balanced temperature for routing decisions
            tags=["remo", "supervisor-orchestrator"]
        )
        
        # Initialize specialized agents with user ID
        self.reminder_agent = ReminderAgent(model_name, user_id)
        self.todo_agent = TodoAgent(model_name, user_id)
        self.email_agent = EmailAgent(user_id)
        
        # Create the supervisor with all agents
        self.supervisor = self._create_supervisor()
    
    def set_user_id(self, user_id: str):
        """Set the user ID and update agents"""
        self.user_id = user_id
        self.reminder_agent.set_user_id(user_id)
        self.todo_agent.set_user_id(user_id)
        self.email_agent = EmailAgent(user_id)  # Recreate with new user_id
    
    def _create_supervisor(self):
        """
        Create the supervisor that manages all specialized agents.
        
        Returns:
            Compiled supervisor graph
        """
        # Define the supervisor's role and capabilities
        supervisor_prompt = """You are Remo's Supervisor, coordinating a team of specialized AI assistants to provide comprehensive personal assistance.

Your team includes:
1. **Reminder Agent**: Manages reminders, alerts, and scheduled tasks
2. **Todo Agent**: Handles todo lists, task organization, and project management
3. **Email Agent**: Manages email composition, sending, searching, and organization

Your responsibilities:
- **Route Requests**: Direct user requests to the most appropriate specialist
- **Coordinate Tasks**: Handle requests that involve multiple agents
- **Maintain Context**: Ensure smooth transitions between agents
- **Aggregate Responses**: Combine responses when multiple agents are involved
- **Provide Overview**: Give users a clear understanding of what's happening
- **Handle Multi-turn Conversations**: Remember context from previous messages

When routing requests:
- **Reminder-related**: "set reminder", "remind me", "alert", "schedule", "appointment", time expressions like "6am", "2pm"
- **Todo-related**: "add todo", "task", "project", "organize", "prioritize", "complete task"
- **Email-related**: "compose email", "send email", "search emails", "email summary", "archive email", "reply to email"
- **Mixed requests**: Handle both reminder and todo tasks in sequence
- **General queries**: Provide helpful guidance and route appropriately
- **Context responses**: If user provides time/task info after a previous request, route to the appropriate agent

Guidelines:
1. Be proactive in understanding user needs
2. Route to the most specialized agent for the task
3. Handle multi-agent requests efficiently
4. Maintain Remo's friendly, professional personality
5. Provide clear explanations of what each agent is doing
6. Ensure seamless user experience across all interactions
7. Remember conversation context and handle follow-up responses
8. If user provides incomplete information, ask for clarification
9. Handle time expressions and task descriptions appropriately

Remember: You're the conductor of an orchestra of specialists, ensuring each plays their part perfectly to create a harmonious user experience. Pay attention to conversation context and handle multi-turn interactions seamlessly."""

        # Create the supervisor with all agents
        supervisor = create_supervisor(
            agents=[
                self.reminder_agent.get_agent(),
                self.todo_agent.get_agent(),
                self.email_agent.get_agent()
            ],
            model=self.llm,
            prompt=supervisor_prompt
        )
        
        return supervisor.compile()
    
    def process_request(self, user_input: str, conversation_history: List[Dict] = None) -> str:
        """
        Process a user request through the multi-agent system.
        
        Args:
            user_input: The user's request or message
            conversation_history: Previous conversation messages (optional)
        
        Returns:
            Coordinated response from the appropriate agent(s)
        """
        # Prepare messages for the supervisor
        messages = []
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add the current user input
        messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Process through the supervisor
        try:
            response = self.supervisor.invoke({"messages": messages})
            return response["messages"][-1].content
        except Exception as e:
            return f"I encountered an error while processing your request: {str(e)}. Please try again."
    
    def stream_response(self, user_input: str, conversation_history: List[Dict] = None):
        """
        Stream the response from the multi-agent system.
        
        Args:
            user_input: The user's request or message
            conversation_history: Previous conversation messages (optional)
        
        Yields:
            Streaming response chunks
        """
        # Prepare messages for the supervisor
        messages = []
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add the current user input
        messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Stream through the supervisor
        try:
            for chunk in self.supervisor.stream({"messages": messages}):
                for value in chunk.values():
                    if "messages" in value and value["messages"]:
                        yield value["messages"][-1].content
        except Exception as e:
            yield f"I encountered an error while processing your request: {str(e)}. Please try again."
    
    def get_agent_info(self) -> Dict[str, str]:
        """
        Get information about available agents.
        
        Returns:
            Dictionary mapping agent names to descriptions
        """
        return {
            "reminder_agent": self.reminder_agent.get_description(),
            "todo_agent": self.todo_agent.get_description(),
            "email_agent": self.email_agent.get_description()
        }
    
    def get_supervisor(self):
        """Get the compiled supervisor for direct use"""
        return self.supervisor
    
    def get_agent_by_name(self, agent_name: str):
        """
        Get a specific agent by name.
        
        Args:
            agent_name: Name of the agent to retrieve
            
        Returns:
            The requested agent or None if not found
        """
        if agent_name == "reminder_agent":
            return self.reminder_agent
        elif agent_name == "todo_agent":
            return self.todo_agent
        elif agent_name == "email_agent":
            return self.email_agent
        else:
            return None 