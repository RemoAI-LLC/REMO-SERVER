"""
Reminder Agent
Specialized AI agent for managing reminders, alerts, and scheduled tasks.
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
    
    def __init__(self, user_id: str = None):
        """
        Initialize the Reminder Agent with tools and persona.
        
        Args:
            user_id: User ID for user-specific functionality
        """
        self.name = "reminder_agent"
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
                for msg in conversation_history:
                    if isinstance(msg.get("content"), str):
                        msg["content"] = [{"text": msg["content"]}]
                    elif isinstance(msg.get("content"), list):
                        msg["content"] = [c if isinstance(c, dict) else {"text": c} for c in msg["content"]]
                    messages.append(msg)
            
            # Add the current user input in correct schema
            messages.append({"role": "user", "content": [{"text": user_message}]})
            
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