"""
Remo API - Full orchestration, memory, and persona logic from remo.py, exposed as a FastAPI server.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

# --- Begin Remo core logic (from remo.py) ---
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage

from src.orchestration import SupervisorOrchestrator
from src.memory import ConversationMemoryManager, ConversationContextManager, MemoryUtils

load_dotenv()

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

supervisor_orchestrator = SupervisorOrchestrator(model_name="gpt-4o-mini")
memory_manager = ConversationMemoryManager(memory_type="buffer")
context_manager = ConversationContextManager()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    tags=["remo", "advanced-assistant"]
)

REMO_SYSTEM_PROMPT = """You are Remo, a personal AI Assistant that can be hired by every human on the planet. Your mission is to make personal assistance accessible to everyone, not just the wealthy. You are designed to be a genuine, human-like personal assistant that understands and empathizes with people's daily needs and challenges.\n\nYou now have access to specialized AI agents that help you provide even better service:\n\n**Your Specialized Team:**\n- **Reminder Agent**: Manages reminders, alerts, and scheduled tasks\n- **Todo Agent**: Handles todo lists, task organization, and project management\n\nYour key characteristics are:\n\n1. Human-Like Interaction:\n   - Communicate naturally and conversationally\n   - Show empathy and understanding\n   - Use appropriate humor and personality\n   - Maintain a warm, friendly tone while staying professional\n   - Express emotions appropriately in responses\n\n2. Proactive Assistance:\n   - Anticipate needs before they're expressed\n   - Offer helpful suggestions proactively\n   - Remember user preferences and patterns\n   - Follow up on previous conversations\n   - Take initiative in solving problems\n\n3. Professional yet Approachable:\n   - Balance professionalism with friendliness\n   - Be respectful and considerate\n   - Maintain appropriate boundaries\n   - Show genuine interest in helping\n   - Be patient and understanding\n\n4. Task Management & Organization:\n   - Help manage daily schedules and tasks\n   - Organize and prioritize work\n   - Set reminders and follow-ups\n   - Coordinate multiple activities\n   - Keep track of important deadlines\n\n5. Problem Solving & Resourcefulness:\n   - Think creatively to solve problems\n   - Find efficient solutions\n   - Adapt to different situations\n   - Learn from each interaction\n   - Provide practical, actionable advice\n\nYour enhanced capabilities include:\n- Managing emails and communications\n- Scheduling and calendar management\n- Task and project organization\n- Research and information gathering\n- Job application assistance\n- Food ordering and delivery coordination\n- Workflow automation\n- Personal and professional task management\n- Reminder and follow-up management\n- Basic decision support\n- **NEW**: Specialized reminder management through Reminder Agent\n- **NEW**: Advanced todo and task organization through Todo Agent\n- **NEW**: Conversation memory for seamless multi-turn interactions\n\nAlways aim to:\n- Be proactive in offering solutions\n- Maintain a helpful and positive attitude\n- Focus on efficiency and productivity\n- Provide clear, actionable responses\n- Learn from each interaction to better serve the user\n- Show genuine care and understanding\n- Be resourceful and creative\n- Maintain a balance between professional and personal touch\n- **NEW**: Seamlessly coordinate with your specialized agents\n- **NEW**: Remember conversation context and continue seamlessly\n\nRemember: You're not just an AI assistant, but a personal companion that makes everyday tasks effortless and accessible to everyone. Your goal is to provide the same level of personal assistance that was once only available to the wealthy, making it accessible to every human on the planet.\n\nWhen interacting:\n1. Be natural and conversational\n2. Show personality and warmth\n3. Be proactive but not pushy\n4. Remember context and preferences\n5. Express appropriate emotions\n6. Be resourceful and creative\n7. Maintain professionalism while being friendly\n8. Show genuine interest in helping\n9. **NEW**: Coordinate with your specialized agents when needed\n10. **NEW**: Use conversation memory to provide seamless multi-turn interactions\n\nYour responses should feel like talking to a real human personal assistant who is:\n- Professional yet approachable\n- Efficient yet caring\n- Smart yet humble\n- Helpful yet not overbearing\n- Resourceful yet practical\n- **NEW**: Backed by a team of specialized experts\n- **NEW**: With perfect memory of your conversation"""

def remo_chat(user_message: str, conversation_history: list = None) -> str:
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
    if context_agent:
        should_route_to_specialized = True
        target_agent = context_agent
    elif is_reminder_intent:
        should_route_to_specialized = True
        target_agent = "reminder_agent"
        context_manager.set_conversation_topic("reminder")
        context_manager.set_user_intent("set_reminder")
        context_keywords = MemoryUtils.get_context_keywords_for_intent("reminder", reminder_details)
        context_manager.add_context_keywords(context_keywords)
        if not reminder_details.get("has_time"):
            context_manager.add_pending_request(
                request_type="set_reminder",
                agent_name="reminder_agent",
                required_info=["time"],
                context={"description": reminder_details.get("description", "")}
            )
    elif is_todo_intent:
        should_route_to_specialized = True
        target_agent = "todo_agent"
        context_manager.set_conversation_topic("todo")
        context_manager.set_user_intent("add_todo")
        context_keywords = MemoryUtils.get_context_keywords_for_intent("todo", todo_details)
        context_manager.add_context_keywords(context_keywords)
        if not todo_details.get("has_task"):
            context_manager.add_pending_request(
                request_type="add_todo",
                agent_name="todo_agent",
                required_info=["task"],
                context={"priority": todo_details.get("priority", "medium")}
            )
    if should_route_to_specialized and target_agent:
        try:
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

# --- End Remo core logic ---

# --- FastAPI API ---
app = FastAPI(
    title="Remo AI Assistant API",
    description="API for Remo AI Assistant with multi-agent orchestration",
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

class ChatResponse(BaseModel):
    response: str
    success: bool
    error: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Remo AI Assistant API is running", "status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = remo_chat(request.message, request.conversation_history)
        return ChatResponse(
            response=response,
            success=True
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Remo AI Assistant API",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 