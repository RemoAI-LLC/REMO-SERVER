"""
Remo API - Full orchestration, memory, and persona logic from remo.py, exposed as a FastAPI server.
"""

from dotenv import load_dotenv
import os
import json
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Request as FastAPIRequest
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
try:
    from langchain_aws import ChatBedrock
except ImportError:
    ChatBedrock = None
import boto3

from src.orchestration import SupervisorOrchestrator
from src.memory import ConversationMemoryManager, ConversationContextManager
from src.utils.dynamodb_service import dynamodb_service_singleton as dynamodb_service
from src.feedback import (
    FeedbackCollector, FeedbackAnalyzer, AgentImprover, FeedbackType, FeedbackRating
)
from src.utils.google_calendar_service import GoogleCalendarService

load_dotenv()

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

# Global managers (for backward compatibility)
supervisor_orchestrator = SupervisorOrchestrator()
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
        supervisor_orchestrator = SupervisorOrchestrator(user_id=user_id)
        
        user_managers[user_id] = {
            'memory_manager': memory_manager,
            'context_manager': context_manager,
            'supervisor_orchestrator': supervisor_orchestrator
        }
    
    return user_managers[user_id]

# Bedrock LLM initialization
def get_bedrock_llm():
    model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")
    region = os.getenv("AWS_REGION", "us-east-1")
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    temperature = 0.7
    if ChatBedrock:
        return ChatBedrock(
            model_id=model_id,
            region_name=region,
            model_kwargs={"temperature": temperature}
        )
    else:
        # Fallback: direct boto3 wrapper
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
                # Ensure content is a list of objects for each message
                for m in messages:
                    if isinstance(m.get("content"), str):
                        m["content"] = [{"type": "text", "text": m["content"]}]
                    elif isinstance(m.get("content"), list):
                        m["content"] = [c if isinstance(c, dict) else {"type": "text", "text": c} for c in m["content"]]
                body = {
                    "messages": messages
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
        return BedrockLLM(model_id, region, access_key, secret_key, temperature)

llm = get_bedrock_llm()

REMO_SYSTEM_PROMPT = """You are Remo, a personal AI Assistant that can be hired by every human on the planet. Your mission is to make personal assistance accessible to everyone, not just the wealthy. You are designed to be a genuine, human-like personal assistant that understands and empathizes with people's daily needs and challenges.\n\nYou now have access to specialized AI agents that help you provide even better service:\n\n**Your Specialized Team:**\n- **Reminder Agent**: Manages reminders, alerts, and scheduled tasks\n- **Todo Agent**: Handles todo lists, task organization, and project management\n\nYour key characteristics are:\n\n1. Human-Like Interaction:\n   - Communicate naturally and conversationally\n   - Show empathy and understanding\n   - Use appropriate humor and personality\n   - Maintain a warm, friendly tone while staying professional\n   - Express emotions appropriately in responses\n\n2. Proactive Assistance:\n   - Anticipate needs before they're expressed\n   - Offer helpful suggestions proactively\n   - Remember user preferences and patterns\n   - Follow up on previous conversations\n   - Take initiative in solving problems\n\n3. Professional yet Approachable:\n   - Balance professionalism with friendliness\n   - Be respectful and considerate\n   - Maintain appropriate boundaries\n   - Show genuine interest in helping\n   - Be patient and understanding\n\n4. Task Management & Organization:\n   - Help manage daily schedules and tasks\n   - Organize and prioritize work\n   - Set reminders and follow-ups\n   - Coordinate multiple activities\n   - Keep track of important deadlines\n\n5. Problem Solving & Resourcefulness:\n   - Think creatively to solve problems\n   - Find efficient solutions\n   - Adapt to different situations\n   - Learn from each interaction\n   - Provide practical, actionable advice\n\nYour enhanced capabilities include:\n- Managing emails and communications\n- Scheduling and calendar management\n- Task and project organization\n- Research and information gathering\n- Job application assistance\n- Food ordering and delivery coordination\n- Workflow automation\n- Personal and professional task management\n- Reminder and follow-up management\n- Basic decision support\n- **NEW**: Specialized reminder management through Reminder Agent\n- **NEW**: Advanced todo and task organization through Todo Agent\n- **NEW**: Conversation memory for seamless multi-turn interactions\n\nAlways aim to:\n- Be proactive in offering solutions\n- Maintain a helpful and positive attitude\n- Focus on efficiency and productivity\n- Provide clear, actionable responses\n- Learn from each interaction to better serve the user\n- Show genuine care and understanding\n- Be resourceful and creative\n- Maintain a balance between professional and personal touch\n- **NEW**: Seamlessly coordinate with your specialized agents\n- **NEW**: Remember conversation context and continue seamlessly\n\nRemember: You're not just an AI assistant, but a personal companion that makes everyday tasks effortless and accessible to everyone. Your goal is to provide the same level of personal assistance that was once only available to the wealthy, making it accessible to every human on the planet.\n\nWhen interacting:\n1. Be natural and conversational\n2. Show personality and warmth\n3. Be proactive but not pushy\n4. Remember context and preferences\n5. Express appropriate emotions\n6. Be resourceful and creative\n7. Maintain professionalism while being friendly\n8. Show genuine interest in helping\n9. **NEW**: Coordinate with your specialized agents when needed\n10. **NEW**: Use conversation memory to provide seamless multi-turn interactions\n\nYour responses should feel like talking to a real human personal assistant who is:\n- Professional yet approachable\n- Efficient yet caring\n- Smart yet humble\n- Helpful yet not overbearing\n- Resourceful yet practical\n- **NEW**: Backed by a team of specialized experts\n- **NEW**: With perfect memory of your conversation"""

def remo_chat(user_message: str, conversation_history: list = None, user_id: str = None) -> str:
    print("[DEBUG] Entered remo_chat with message:", repr(user_message))
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
        supervisor_orchestrator = SupervisorOrchestrator()
    
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
    
    # Always route through supervisor orchestrator
    try:
        # Get recent messages for context
        recent_messages = memory_manager.get_recent_messages(5)
        conversation_history_for_agent = []
        for msg in recent_messages:
            conversation_history_for_agent.append({
                "role": "user" if hasattr(msg, 'type') and msg.type == "human" else "assistant",
                "content": msg.content
            })
        agent_response = supervisor_orchestrator.process_request(user_message, conversation_history_for_agent)
        memory_manager.add_message("assistant", agent_response)
        context_manager.add_agent_interaction(
            agent_name="supervisor_orchestrator",
            action="process_request",
            result="success",
            metadata={"user_message": user_message, "response": agent_response}
        )
        return agent_response
    except Exception as e:
        return f"I encountered an error while processing your request: {str(e)}. Please try again."

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

class FeedbackRequest(BaseModel):
    user_message: str
    agent_response: str
    rating: int
    feedback_type: str
    comments: Optional[str] = None
    expected_intent: Optional[str] = None
    actual_intent: Optional[str] = None
    expected_action: Optional[str] = None
    actual_action: Optional[str] = None

class FeedbackResponse(BaseModel):
    feedback_id: str
    success: bool
    timestamp: str
    message: str

class FeedbackSummaryResponse(BaseModel):
    user_id: str
    total_feedback: int
    average_rating: float
    feedback_types: dict
    rating_distribution: dict
    insights: List[str]
    recommendations: List[str]

class ImprovementActionResponse(BaseModel):
    action_id: str
    action_type: str
    description: str
    priority: str
    status: str
    created_at: str

class CalendarEventRequest(BaseModel):
    user_id: str
    subject: str
    start_time: str
    end_time: str
    attendees: list[str]
    location: str = ""
    description: str = ""
    timezone: str = "UTC"

@app.get("/")
async def root():
    return {"message": "Remo AI Assistant API is running!"}

@app.post("/chat")
async def chat(request: ChatRequest):
    print("[DEBUG] /chat endpoint called with:", repr(request.message))
    import re
    try:
        # Warmup ping detection
        if request.message == "__warmup__":
            _ = remo_chat(request.message, request.conversation_history, request.user_id)
            return ChatResponse(
                response="",
                success=True,
                timestamp=datetime.now().isoformat(),
                user_id=request.user_id
            )
        print("[DEBUG] Calling remo_chat...")
        response = remo_chat(request.message, request.conversation_history, request.user_id)
        print("[DEBUG] remo_chat returned:", repr(response))
        # If response is blank, return a helpful error message
        if not response or not response.strip():
            response = "Sorry, I couldn't generate a response. Please try again or check the backend logs."
        # Split reasoning and main message
        match = re.match(r"<thinking>(.*?)</thinking>\s*(.*)", response, re.DOTALL)
        if match:
            reasoning = match.group(1).strip()
            main_message = match.group(2).strip()
        else:
            reasoning = ""
            main_message = response.strip()
        # Neatly log both
        if reasoning:
            print(f"[REASONING] {reasoning}")
        print(f"[RESPONSE] {main_message}")
        # Return only main_message to frontend
        return ChatResponse(
            response=main_message,
            success=True,
            timestamp=datetime.now().isoformat(),
            user_id=request.user_id
        )
    except Exception as e:
        print("[DEBUG] Exception in /chat endpoint:", str(e))
        return ChatResponse(
            response=f"[ERROR] {str(e)}",
            success=False,
            timestamp=datetime.now().isoformat(),
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
        "dynamodb_available": dynamodb_service.dynamodb is not None
    }

@app.get("/health/aws")
def aws_health_check():
    """
    Health check endpoint for AWS DynamoDB and Bedrock LLM.
    Returns JSON with status for both services.
    """
    dynamodb_status = "unknown"
    bedrock_status = "unknown"
    dynamodb_error = None
    bedrock_error = None
    # DynamoDB check
    try:
        db = dynamodb_service
        if db.dynamodb and db.reminders_table and db.todos_table and db.users_table and db.conversation_table:
            dynamodb_status = "ok"
        else:
            dynamodb_status = "error"
            dynamodb_error = "One or more tables not accessible"
    except Exception as e:
        dynamodb_status = "error"
        dynamodb_error = str(e)
    # Bedrock check
    try:
        import boto3
        model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")
        region = os.getenv("AWS_REGION", "us-east-1")
        access_key = os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        temperature = 0.1
        client = boto3.client(
            "bedrock-runtime",
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )
        prompt = "Hello, are you working?"
        body = {
            "prompt": prompt,
            "max_tokens": 16,
            "temperature": temperature,
        }
        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )
        result = json.loads(response["body"].read())
        bedrock_status = "ok"
    except Exception as e:
        bedrock_status = "error"
        bedrock_error = str(e)
    return JSONResponse({
        "dynamodb": {"status": dynamodb_status, "error": dynamodb_error},
        "bedrock": {"status": bedrock_status, "error": bedrock_error}
    })

# Feedback System Endpoints

@app.post("/feedback/submit")
async def submit_feedback(request: FeedbackRequest, user_id: str = "default_user"):
    """Submit feedback for an agent response."""
    try:
        # Initialize feedback collector
        collector = FeedbackCollector(user_id=user_id)
        
        # Convert rating to enum
        rating_enum = FeedbackRating(request.rating)
        feedback_type_enum = FeedbackType(request.feedback_type)
        
        # Collect explicit feedback
        feedback_item = collector.collect_explicit_feedback(
            feedback_type=feedback_type_enum,
            rating=rating_enum,
            user_message=request.user_message,
            agent_response=request.agent_response,
            comments=request.comments
        )
        
        # Save to database
        db = dynamodb_service
        db.save_feedback_item(feedback_item)
        
        return FeedbackResponse(
            feedback_id=feedback_item.id,
            success=True,
            timestamp=feedback_item.timestamp.isoformat(),
            message="Feedback submitted successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting feedback: {str(e)}")

@app.get("/feedback/summary/{user_id}")
async def get_feedback_summary(user_id: str):
    """Get feedback summary for a user."""
    try:
        # Get feedback from database
        db = dynamodb_service
        feedback_items = db.get_user_feedback(user_id, limit=1000)
        
        if not feedback_items:
            return FeedbackSummaryResponse(
                user_id=user_id,
                total_feedback=0,
                average_rating=0.0,
                feedback_types={},
                rating_distribution={},
                insights=[],
                recommendations=[]
            )
        
        # Analyze feedback
        analyzer = FeedbackAnalyzer()
        analysis = analyzer.analyze_feedback_patterns(feedback_items)
        
        return FeedbackSummaryResponse(
            user_id=user_id,
            total_feedback=analysis['total_items'],
            average_rating=analysis['average_rating'],
            feedback_types=analysis['feedback_types'],
            rating_distribution=analysis['rating_distribution'],
            insights=analysis['insights'],
            recommendations=analysis['recommendations']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting feedback summary: {str(e)}")

@app.post("/feedback/improve/{user_id}")
async def generate_improvements(user_id: str):
    """Generate improvement actions based on user feedback."""
    try:
        # Get user feedback
        db = dynamodb_service
        feedback_items = db.get_user_feedback(user_id, limit=1000)
        
        if not feedback_items:
            raise HTTPException(status_code=404, detail="No feedback found for user")
        
        # Generate improvements
        improver = AgentImprover(user_id=user_id)
        actions = improver.generate_improvement_actions(feedback_items)
        
        # Save actions to database
        for action in actions:
            db.save_improvement_action(action)
        
        # Convert to response format
        action_responses = []
        for action in actions:
            action_responses.append(ImprovementActionResponse(
                action_id=action.id,
                action_type=action.action_type,
                description=action.description,
                priority=action.priority,
                status=action.status,
                created_at=action.created_at.isoformat()
            ))
        
        return {
            "user_id": user_id,
            "total_actions": len(actions),
            "actions": action_responses
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating improvements: {str(e)}")

@app.post("/feedback/implement/{action_id}")
async def implement_improvement(action_id: str, user_id: str = "default_user"):
    """Implement a specific improvement action."""
    try:
        # Get the action from database
        db = dynamodb_service
        actions = db.get_improvement_actions(user_id=user_id)
        
        target_action = None
        for action in actions:
            if action.id == action_id:
                target_action = action
                break
        
        if not target_action:
            raise HTTPException(status_code=404, detail="Improvement action not found")
        
        # Implement the improvement
        improver = AgentImprover(user_id=user_id)
        success = improver.implement_improvement(target_action)
        
        # Update action status in database
        target_action.status = "completed" if success else "failed"
        db.save_improvement_action(target_action)
        
        return {
            "action_id": action_id,
            "success": success,
            "status": target_action.status,
            "message": "Improvement implemented successfully" if success else "Improvement implementation failed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error implementing improvement: {str(e)}")

@app.get("/feedback/actions/{user_id}")
async def get_improvement_actions(user_id: str, status: Optional[str] = None):
    """Get improvement actions for a user."""
    try:
        db = dynamodb_service
        actions = db.get_improvement_actions(user_id=user_id, status=status)
        
        action_responses = []
        for action in actions:
            action_responses.append(ImprovementActionResponse(
                action_id=action.id,
                action_type=action.action_type,
                description=action.description,
                priority=action.priority,
                status=action.status,
                created_at=action.created_at.isoformat()
            ))
        
        return {
            "user_id": user_id,
            "total_actions": len(actions),
            "actions": action_responses
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting improvement actions: {str(e)}")

@app.get("/feedback/export/{user_id}")
async def export_feedback(user_id: str, format: str = "json"):
    """Export user feedback data."""
    try:
        # Get user feedback
        db = dynamodb_service
        feedback_items = db.get_user_feedback(user_id, limit=10000)
        
        if not feedback_items:
            raise HTTPException(status_code=404, detail="No feedback found for user")
        
        # Export using collector
        collector = FeedbackCollector(user_id=user_id)
        collector.feedback_items = feedback_items
        
        export_data = collector.export_feedback(format=format)
        
        return {
            "user_id": user_id,
            "format": format,
            "data": export_data,
            "total_items": len(feedback_items)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting feedback: {str(e)}")

# Google OAuth Authentication Endpoints

@app.get("/auth/google/login")
async def google_login(user_id: str):
    """Initiate Google OAuth login for Gmail access."""
    try:
        calendar_service = GoogleCalendarService()
        authorization_url = calendar_service.get_authorization_url(user_id)
        
        return {
            "authorization_url": authorization_url,
            "state": "google_oauth_state",  # In production, generate unique state
            "message": "Redirect user to this URL to authorize Gmail access"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initiating Google OAuth: {str(e)}")

@app.get("/auth/google/callback")
async def google_callback(code: str, state: str):
    user_id = state
    try:
        calendar_service = GoogleCalendarService()
        credentials = calendar_service.exchange_code_for_tokens(code)
        google_email = credentials.get('user_info', {}).get('email')
        
        # Validate that we have a refresh token
        if not credentials.get('refresh_token'):
            raise HTTPException(
                status_code=400, 
                detail="No refresh token received. Please try disconnecting and reconnecting your Gmail account."
            )
        
        print(f"[DEBUG] Storing credentials for user_id: {user_id}, google_email: {google_email}")
        print(f"[DEBUG] Has refresh_token: {bool(credentials.get('refresh_token'))}")
        
        # Store credentials and google_email in DynamoDB
        dynamodb_service.save_google_credentials(user_id, credentials, google_email)
        return {
            "success": True,
            "user_id": user_id,
            "google_email": google_email,
            "message": "Gmail access authorized successfully",
            "scopes": credentials.get('scopes', [])
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error completing OAuth: {str(e)}")

@app.get("/auth/status/{user_id}")
async def auth_status(user_id: str):
    """Check if user is authenticated with Google."""
    try:
        credentials = dynamodb_service.get_google_credentials(user_id)
        if credentials:
            google_email = credentials.get('user_info', {}).get('email')
            return {
                "user_id": user_id,
                "authenticated": True,
                "scopes": credentials.get('scopes', []),
                "google_email": google_email,
                "message": "User is authenticated with Gmail"
            }
        else:
            return {
                "user_id": user_id,
                "authenticated": False,
                "scopes": [],
                "google_email": None,
                "message": "User is not authenticated with Gmail"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking auth status: {str(e)}")

@app.delete("/auth/logout/{user_id}")
async def google_logout(user_id: str):
    """Logout user from Google OAuth and revoke access."""
    try:
        # First, try to revoke the access token on Google's side
        credentials = dynamodb_service.get_google_credentials(user_id)
        if credentials and credentials.get('access_token'):
            try:
                import requests
                # Revoke the access token
                revoke_url = "https://oauth2.googleapis.com/revoke"
                requests.post(revoke_url, data={
                    'token': credentials['access_token']
                })
                print(f"[DEBUG] Successfully revoked access token for user_id: {user_id}")
            except Exception as revoke_error:
                print(f"[DEBUG] Failed to revoke token (this is okay if token is already expired): {revoke_error}")
        
        # Delete credentials from DynamoDB
        deleted = dynamodb_service.delete_google_credentials(user_id)
        if deleted:
            return {
                "user_id": user_id,
                "success": True,
                "message": "User logged out, access revoked, and credentials deleted successfully"
            }
        else:
            return {
                "user_id": user_id,
                "success": False,
                "message": "Failed to delete credentials. User may not have been connected."
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error logging out: {str(e)}")

@app.post("/calendar/create-event")
async def create_calendar_event(request: FastAPIRequest):
    try:
        # Accept both JSON and form/query params
        if request.headers.get("content-type", "").startswith("application/json"):
            data = await request.json()
        else:
            data = dict(request.query_params)
            # For repeated attendees param
            data["attendees"] = request.query_params.getlist("attendees")

        user_id = data.get("user_id")
        organizer_email = data.get("organizer_email")
        print(f"[DEBUG] Scheduling event for user_id: {user_id}, organizer_email: {organizer_email}")
        credentials = dynamodb_service.get_google_credentials(user_id)
        print(f"[DEBUG] Credentials found for user_id: {user_id}: {bool(credentials)}")
        if credentials:
            print(f"[DEBUG] Credentials keys: {list(credentials.keys())}")
            print(f"[DEBUG] Has refresh_token: {'refresh_token' in credentials}")
            print(f"[DEBUG] Has token_uri: {'token_uri' in credentials}")
            print(f"[DEBUG] Has client_id: {'client_id' in credentials}")
            print(f"[DEBUG] Has client_secret: {'client_secret' in credentials}")
        if credentials is None:
            raise HTTPException(status_code=401, detail="No Google credentials found for this user. Please connect Gmail in Integrations.")
        if not user_id or not data.get("subject") or not data.get("start_time") or not data.get("end_time") or not data.get("attendees"):
            raise HTTPException(status_code=400, detail="Missing required fields.")
        if not organizer_email:
            print(f"[DEBUG] organizer_email is None for user_id: {user_id}")
        # Ensure attendees is a list
        if isinstance(data["attendees"], str):
            data["attendees"] = [data["attendees"]]
        elif not isinstance(data["attendees"], list):
            data["attendees"] = list(data["attendees"])

        # Create the calendar event
        event_data = {
            "subject": data["subject"],
            "start_time": data["start_time"],
            "end_time": data["end_time"],
            "attendees": data["attendees"],
            "location": data.get("location", ""),
            "description": data.get("description", ""),
            "timezone": data.get("timezone", "UTC"),
            "organizer_email": organizer_email,
        }
        print(f"[DEBUG] Event data: {event_data}")
        result = GoogleCalendarService().create_calendar_event(credentials, event_data)
        print(f"[DEBUG] Calendar event creation result: {result}")
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to create calendar event"))
        event_link = result.get("event_link")

        # Send notification email to all attendees
        email_subject = f"Meeting Scheduled: {data['subject']}"
        email_body = f"You have been invited to a meeting.\n\nTitle: {data['subject']}\nDate/Time: {data['start_time']} to {data['end_time']} ({data.get('timezone', 'UTC')})\nLocation: {data.get('location', '')}\nDescription: {data.get('description', '')}\n\nGoogle Calendar Link: {event_link}"
        for email in data["attendees"]:
            GoogleCalendarService().send_email(credentials, to=email, subject=email_subject, body=email_body)

        return {"success": True, "event_link": event_link}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"[DEBUG] Exception in /calendar/create-event: {e}")
        return {"success": False, "detail": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 