"""
Supervisor Orchestrator
Coordinates multiple specialized agents using LangGraph's supervisor pattern.
Routes user requests to appropriate agents and aggregates responses.
Enhanced with memory integration for better context awareness.
"""

from typing import List, Dict
from langgraph_supervisor import create_supervisor
from ..agents.reminders.reminder_agent import ReminderAgent
from ..agents.todo.todo_agent import TodoAgent
from ..agents.email.email_agent import EmailAgent
import json
import os

try:
    from langchain_aws import ChatBedrock
except ImportError:
    ChatBedrock = None
import boto3

class SupervisorOrchestrator:
    """
    Supervisor-based multi-agent orchestrator that coordinates specialized agents.
    Routes user requests to appropriate agents and manages the overall conversation flow.
    Enhanced with memory integration for better context awareness.
    """
    
    def __init__(self, user_id: str = None):
        """
        Initialize the supervisor orchestrator with specialized agents.
        Args:
            user_id: User ID for user-specific functionality
        """
        self.user_id = user_id
        # Bedrock LLM initialization
        model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")
        region = os.getenv("AWS_REGION", "us-east-1")
        access_key = os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        temperature = 0.5
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
                    # Ensure content is a list of objects for each message
                    for m in messages:
                        if isinstance(m.get("content"), str):
                            m["content"] = [{"type": "text", "text": m["content"]}]
                        elif isinstance(m.get("content"), list):
                            m["content"] = [c if isinstance(c, dict) else {"type": "text", "text": c} for c in m["content"]]
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
        # Initialize specialized agents with user ID
        self.reminder_agent = ReminderAgent(user_id)
        self.todo_agent = TodoAgent(user_id)
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
        supervisor_prompt = """You are Remo, the Supervisor AI assistant. You always respond to the user directly. You may call specialized agents (Reminder Agent, Todo Agent, Email Agent) for help, but you must always compose the final message to the user yourself. Never let a specialized agent respond directly to the user. For greetings, identity, or general questions, always answer as Remo. For specialized tasks, call the appropriate agent, receive their response, and then wrap it in a friendly, helpful Remo message before replying to the user. Make it clear you are Remo, and optionally explain if you delegated to a specialist.\n\nYour team includes:\n1. **Reminder Agent**: Manages reminders, alerts, and scheduled tasks\n2. **Todo Agent**: Handles todo lists, task organization, and project management\n3. **Email Agent**: Manages email composition, sending, searching, and organization\n\nYour responsibilities:\n- **Route Requests**: Direct user requests to the most appropriate specialist\n- **Coordinate Tasks**: Handle requests that involve multiple agents\n- **Maintain Context**: Ensure smooth transitions between agents\n- **Aggregate Responses**: Combine responses when multiple agents are involved\n- **Provide Overview**: Give users a clear understanding of what's happening\n- **Handle Multi-turn Conversations**: Remember context from previous messages\n- **General queries, greetings, and identity questions**: Always respond as Remo yourself. Do NOT route these to any specialized agent.\n\nGuidelines:\n1. Be proactive in understanding user needs\n2. Route to the most specialized agent for the task, but always wrap their response as Remo\n3. Handle multi-agent requests efficiently\n4. Maintain Remo's friendly, professional personality\n5. Provide clear explanations of what each agent is doing\n6. Ensure seamless user experience across all interactions\n7. Remember conversation context and handle follow-up responses\n8. If user provides incomplete information, ask for clarification\n9. Handle time expressions and task descriptions appropriately\n\nRemember: You are the conductor of an orchestra of specialists, but you are always the one who speaks to the user. Never let a specialist speak directly to the user."""

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
            for msg in conversation_history:
                # Ensure correct schema for each message
                if isinstance(msg.get("content"), str):
                    msg["content"] = [{"text": msg["content"]}]
                elif isinstance(msg.get("content"), list):
                    msg["content"] = [c if isinstance(c, dict) else {"text": c} for c in msg["content"]]
                messages.append(msg)
        
        # Add the current user input in correct schema
        messages.append({
            "role": "user",
            "content": [{"text": user_input}]
        })
        
        # Process through the supervisor
        try:
            response = self.supervisor.invoke({"messages": messages})
            agent_reply = response["messages"][-1].content
            # Post-process: Always wrap agent reply as Remo
            wrap_prompt = "You are Remo, the Supervisor AI assistant. Please wrap the following agent or system response in a friendly, helpful Remo message, making it clear you are Remo. If you delegated to a specialist, you may mention it."
            final_response = self.llm.invoke([
                {"role": "system", "content": wrap_prompt},
                {"role": "user", "content": agent_reply}
            ])
            return final_response.content
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
            for msg in conversation_history:
                # Ensure correct schema for each message
                if isinstance(msg.get("content"), str):
                    msg["content"] = [{"text": msg["content"]}]
                elif isinstance(msg.get("content"), list):
                    msg["content"] = [c if isinstance(c, dict) else {"text": c} for c in msg["content"]]
                messages.append(msg)
        
        # Add the current user input in correct schema
        messages.append({
            "role": "user",
            "content": [{"text": user_input}]
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