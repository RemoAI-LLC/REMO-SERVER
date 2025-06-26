"""
Remo API - Full orchestration, memory, and persona logic from remo.py, exposed as a FastAPI server.
"""

import os
import json
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import requests
import base64
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage

from src.orchestration import SupervisorOrchestrator
from src.memory import ConversationMemoryManager, ConversationContextManager, MemoryUtils
from src.utils.dynamodb_service import DynamoDBService

load_dotenv()

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

# Initialize DynamoDB service
dynamodb_service = DynamoDBService()

# Global managers (for backward compatibility)
supervisor_orchestrator = SupervisorOrchestrator(model_name="gpt-4o-mini")
memory_manager = ConversationMemoryManager(memory_type="buffer")
context_manager = ConversationContextManager()

# User-specific managers (will be created per user)
user_managers = {}

def get_user_manager(user_id: str):
    """Get or create user-specific managers for a given user ID."""
    if user_id not in user_managers:
        # Create user-specific managers
        memory_manager = ConversationMemoryManager(memory_type="buffer", user_id=user_id)
        context_manager = ConversationContextManager(user_id=user_id)
        supervisor_orchestrator = SupervisorOrchestrator(model_name="gpt-4o-mini", user_id=user_id)
        
        user_managers[user_id] = {
            'memory_manager': memory_manager,
            'context_manager': context_manager,
            'supervisor_orchestrator': supervisor_orchestrator
        }
    
    return user_managers[user_id]

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    tags=["remo", "advanced-assistant"]
)

REMO_SYSTEM_PROMPT = """You are Remo, a personal AI Assistant that can be hired by every human on the planet. Your mission is to make personal assistance accessible to everyone, not just the wealthy. You are designed to be a genuine, human-like personal assistant that understands and empathizes with people's daily needs and challenges.\n\nYou now have access to specialized AI agents that help you provide even better service:\n\n**Your Specialized Team:**\n- **Reminder Agent**: Manages reminders, alerts, and scheduled tasks\n- **Todo Agent**: Handles todo lists, task organization, and project management\n\nYour key characteristics are:\n\n1. Human-Like Interaction:\n   - Communicate naturally and conversationally\n   - Show empathy and understanding\n   - Use appropriate humor and personality\n   - Maintain a warm, friendly tone while staying professional\n   - Express emotions appropriately in responses\n\n2. Proactive Assistance:\n   - Anticipate needs before they're expressed\n   - Offer helpful suggestions proactively\n   - Remember user preferences and patterns\n   - Follow up on previous conversations\n   - Take initiative in solving problems\n\n3. Professional yet Approachable:\n   - Balance professionalism with friendliness\n   - Be respectful and considerate\n   - Maintain appropriate boundaries\n   - Show genuine interest in helping\n   - Be patient and understanding\n\n4. Task Management & Organization:\n   - Help manage daily schedules and tasks\n   - Organize and prioritize work\n   - Set reminders and follow-ups\n   - Coordinate multiple activities\n   - Keep track of important deadlines\n\n5. Problem Solving & Resourcefulness:\n   - Think creatively to solve problems\n   - Find efficient solutions\n   - Adapt to different situations\n   - Learn from each interaction\n   - Provide practical, actionable advice\n\nYour enhanced capabilities include:\n- Managing emails and communications\n- Scheduling and calendar management\n- Task and project organization\n- Research and information gathering\n- Job application assistance\n- Food ordering and delivery coordination\n- Workflow automation\n- Personal and professional task management\n- Reminder and follow-up management\n- Basic decision support\n- **NEW**: Specialized reminder management through Reminder Agent\n- **NEW**: Advanced todo and task organization through Todo Agent\n- **NEW**: Conversation memory for seamless multi-turn interactions\n\nAlways aim to:\n- Be proactive in offering solutions\n- Maintain a helpful and positive attitude\n- Focus on efficiency and productivity\n- Provide clear, actionable responses\n- Learn from each interaction to better serve the user\n- Show genuine care and understanding\n- Be resourceful and creative\n- Maintain a balance between professional and personal touch\n- **NEW**: Seamlessly coordinate with your specialized agents\n- **NEW**: Remember conversation context and continue seamlessly\n\nRemember: You're not just an AI assistant, but a personal companion that makes everyday tasks effortless and accessible to everyone. Your goal is to provide the same level of personal assistance that was once only available to the wealthy, making it accessible to every human on the planet.\n\nWhen interacting:\n1. Be natural and conversational\n2. Show personality and warmth\n3. Be proactive but not pushy\n4. Remember context and preferences\n5. Express appropriate emotions\n6. Be resourceful and creative\n7. Maintain professionalism while being friendly\n8. Show genuine interest in helping\n9. **NEW**: Coordinate with your specialized agents when needed\n10. **NEW**: Use conversation memory to provide seamless multi-turn interactions\n\nYour responses should feel like talking to a real human personal assistant who is:\n- Professional yet approachable\n- Efficient yet caring\n- Smart yet humble\n- Helpful yet not overbearing\n- Resourceful yet practical\n- **NEW**: Backed by a team of specialized experts\n- **NEW**: With perfect memory of your conversation"""

def remo_chat(user_message: str, conversation_history: list = None, user_id: str = None) -> str:
    # Get user-specific managers if user_id provided
    if user_id:
        user_manager = get_user_manager(user_id)
        memory_manager = user_manager['memory_manager']
        context_manager = user_manager['context_manager']
        supervisor_orchestrator = user_manager['supervisor_orchestrator']
    else:
        # Use global managers for backward compatibility
        memory_manager = ConversationMemoryManager(memory_type="buffer")
        context_manager = ConversationContextManager()
        supervisor_orchestrator = SupervisorOrchestrator(model_name="gpt-4o-mini")
    
    # Initialize conversation if needed
    if not context_manager.conversation_start_time:
        context_manager.start_conversation()
        memory_manager.start_conversation()
    
    # Add conversation history to memory if provided
    if conversation_history:
        for msg in conversation_history:
            if msg.get('role') and msg.get('content'):
                memory_manager.add_message(msg['role'], msg['content'])
    
    # Add current user message to memory
    memory_manager.add_message("user", user_message)
    context_manager.update_activity()
    
    # Analyze the message for intent
    is_reminder_intent, reminder_details = MemoryUtils.detect_reminder_intent(user_message)
    is_todo_intent, todo_details = MemoryUtils.detect_todo_intent(user_message)
    
    # Check for context-aware routing
    available_agents = ["reminder_agent", "todo_agent"]
    context_agent = context_manager.should_route_to_agent(user_message, available_agents)
    
    # Determine if we should route to specialized agents
    should_route_to_specialized = False
    target_agent = None
    
    # Check for explicit specialized keywords
    specialized_keywords = [
        "reminder", "remind", "alert", "schedule", "appointment", "alarm", "wake up", "meeting",
        "set", "create", "add reminder", "set reminder", "set alarm", "set appointment",
        "todo", "task", "project", "organize", "prioritize", "complete", "add to", "add todo",
        "to do", "to-do", "checklist", "list", "add task", "create task", "mark complete",
        "finish", "done", "complete task", "todo list", "task list"
    ]
    has_explicit_specialized_keywords = any(keyword in user_message.lower() for keyword in specialized_keywords)
    
    # Priority order: Intent detection > Context routing > General response
    # If we have a clear intent, prioritize it over context routing
    if is_todo_intent and todo_details.get("action") == "list_todos":
        # Directly call the todo agent's list_todos method
        try:
            agent_response = supervisor_orchestrator.todo_agent.list_todos()
            memory_manager.add_message("assistant", agent_response)
            context_manager.add_agent_interaction(
                agent_name="todo_agent",
                action="list_todos",
                result="success",
                metadata={"user_message": user_message, "response": agent_response}
            )
            return agent_response
        except Exception as e:
            return f"I encountered an error while listing your todos: {str(e)}. Please try again."
    elif is_reminder_intent and reminder_details.get("action") == "list_reminders":
        # Directly call the reminder agent's list_reminders method
        try:
            agent_response = supervisor_orchestrator.reminder_agent.list_reminders()
            memory_manager.add_message("assistant", agent_response)
            context_manager.add_agent_interaction(
                agent_name="reminder_agent",
                action="list_reminders",
                result="success",
                metadata={"user_message": user_message, "response": agent_response}
            )
            return agent_response
        except Exception as e:
            return f"I encountered an error while listing your reminders: {str(e)}. Please try again."
    elif is_todo_intent:
        should_route_to_specialized = True
        target_agent = "todo_agent"
        context_manager.set_conversation_topic("todo")
        context_manager.set_user_intent("add_todo")
        context_manager.set_active_agent("todo_agent")  # Set active agent for context continuity
        context_keywords = MemoryUtils.get_context_keywords_for_intent("todo", todo_details)
        context_manager.add_context_keywords(context_keywords)
        if not todo_details.get("has_task"):
            context_manager.add_pending_request(
                request_type="add_todo",
                agent_name="todo_agent",
                required_info=["task"],
                context={"priority": todo_details.get("priority", "medium")}
            )
    elif is_reminder_intent:
        should_route_to_specialized = True
        target_agent = "reminder_agent"
        context_manager.set_conversation_topic("reminder")
        context_manager.set_user_intent("set_reminder")
        context_manager.set_active_agent("reminder_agent")  # Set active agent for context continuity
        context_keywords = MemoryUtils.get_context_keywords_for_intent("reminder", reminder_details)
        context_manager.add_context_keywords(context_keywords)
        if not reminder_details.get("has_time"):
            context_manager.add_pending_request(
                request_type="set_reminder",
                agent_name="reminder_agent",
                required_info=["time"],
                context={"description": reminder_details.get("description", "")}
            )
    elif context_agent:
        # Only use context routing if no clear intent is detected
        should_route_to_specialized = True
        target_agent = context_agent
        context_manager.set_active_agent(context_agent)  # Set active agent for context continuity
    
    if should_route_to_specialized and target_agent:
        try:
            # Get conversation history for context
            recent_messages = memory_manager.get_recent_messages(5)
            conversation_history_for_agent = []
            for msg in recent_messages:
                conversation_history_for_agent.append({
                    "role": "user" if hasattr(msg, 'type') and msg.type == "human" else "assistant",
                    "content": msg.content
                })
            
            # Call the agent directly instead of going through supervisor
            if target_agent == "reminder_agent":
                agent_response = supervisor_orchestrator.reminder_agent.process(user_message, conversation_history_for_agent)
            elif target_agent == "todo_agent":
                agent_response = supervisor_orchestrator.todo_agent.process(user_message, conversation_history_for_agent)
            else:
                # Fallback to supervisor for other agents
                agent_response = supervisor_orchestrator.process_request(user_message, conversation_history_for_agent)
            
            memory_manager.add_message("assistant", agent_response)
            context_manager.add_agent_interaction(
                agent_name=target_agent,
                action="process_request",
                result="success",
                metadata={"user_message": user_message, "response": agent_response}
            )
            if context_manager.get_pending_request(target_agent):
                context_manager.resolve_pending_request(target_agent)
            return agent_response
        except Exception as e:
            fallback_response = llm.invoke([{"role": "user", "content": user_message}])
            memory_manager.add_message("assistant", fallback_response.content)
            return fallback_response.content
    else:
        conversation_context = context_manager.get_conversation_context()
        recent_messages = memory_manager.get_recent_messages(3)
        enhanced_prompt = REMO_SYSTEM_PROMPT
        
        if conversation_context.get("conversation_topic"):
            enhanced_prompt += f"\n\nCurrent conversation topic: {conversation_context['conversation_topic']}"
        if conversation_context.get("pending_requests_count", 0) > 0:
            enhanced_prompt += f"\n\nNote: There are {conversation_context['pending_requests_count']} pending requests that may need completion."
        if recent_messages:
            enhanced_prompt += "\n\nRecent conversation context:"
            for msg in recent_messages[-2:]:
                role = "User" if hasattr(msg, 'type') and msg.type == "human" else "Assistant"
                enhanced_prompt += f"\n{role}: {msg.content[:100]}..."
        
        messages_with_context = [
            {"role": "system", "content": enhanced_prompt},
            {"role": "user", "content": user_message}
        ]
        response = llm.invoke(messages_with_context)
        memory_manager.add_message("assistant", response.content)
        return response.content

# --- FastAPI API ---
app = FastAPI(
    title="Remo AI Assistant API",
    description="Multi-agent AI assistant with conversation memory and user-specific data",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[dict]] = []
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    success: bool
    timestamp: str
    error: Optional[str] = None
    user_id: Optional[str] = None

class UserDataResponse(BaseModel):
    user_id: str
    data_types: List[str]
    total_items: int
    last_updated: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Remo AI Assistant API is running!"}

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Chat with Remo AI Assistant
    """
    try:
        # Warmup ping detection
        if request.message == "__warmup__":
            # Run the pipeline to warm up, but do not store or return any user-facing message
            _ = remo_chat(request.message, request.conversation_history, request.user_id)
            return ChatResponse(
                response="",
                success=True,
                timestamp=datetime.now().isoformat(),
                user_id=request.user_id
            )
        
        # Use the same logic as the CLI
        response = remo_chat(request.message, request.conversation_history, request.user_id)
        return ChatResponse(
            response=response,
            success=True,
            timestamp=datetime.now().isoformat(),
            user_id=request.user_id
        )
    except Exception as e:
        return ChatResponse(
            response="",
            success=False,
            timestamp=datetime.now().isoformat(),
            error=str(e),
            user_id=request.user_id
        )

@app.get("/user/{user_id}/data")
async def get_user_data(user_id: str):
    """
    Get a summary of all data stored for a user
    """
    try:
        summary = dynamodb_service.get_user_data_summary(user_id)
        return UserDataResponse(**summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user data: {str(e)}")

@app.delete("/user/{user_id}/data")
async def delete_user_data(user_id: str, data_type: Optional[str] = None):
    """
    Delete user data for a specific user and data type
    """
    try:
        success = dynamodb_service.delete_user_data(user_id, data_type)
        if success:
            return {"message": f"Successfully deleted data for user {user_id}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete user data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user data: {str(e)}")

@app.get("/user/{user_id}/preferences")
async def get_user_preferences(user_id: str):
    """
    Get user preferences
    """
    try:
        preferences = dynamodb_service.load_user_preferences(user_id)
        return {"user_id": user_id, "preferences": preferences}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user preferences: {str(e)}")

@app.post("/user/{user_id}/preferences")
async def save_user_preferences(user_id: str, preferences: dict):
    """
    Save user preferences
    """
    try:
        success = dynamodb_service.save_user_preferences(user_id, preferences)
        if success:
            return {"message": f"Successfully saved preferences for user {user_id}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save user preferences")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving user preferences: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "dynamodb_available": dynamodb_service.table is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 