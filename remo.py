"""
Remo - Your Personal AI Assistant
"Remo: A personal AI Assistant that can be hired by every human on the planet. Personal assistants are not just for the rich anymore."

Now powered by multi-agent orchestration with specialized agents for reminders and todo management.
Enhanced with conversation memory for seamless multi-turn interactions.
"""

# Step 1: Import required packages
# ------------------------------
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage
from dotenv import load_dotenv
import os

# Import the multi-agent orchestration system
from src.orchestration import SupervisorOrchestrator

# Import the memory system
from src.memory import ConversationMemoryManager, ConversationContextManager, MemoryUtils

# Load environment variables from .env file
load_dotenv()

# Step 2: Create a StateGraph (kept for compatibility)
# ---------------------------
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Initialize the graph with our State type
graph_builder = StateGraph(State)

# Step 3: Initialize the multi-agent orchestrator and memory system
# ----------------------------------------------------------------
# Initialize the supervisor orchestrator with specialized agents
supervisor_orchestrator = SupervisorOrchestrator(model_name="gpt-4")

# Initialize the memory system
memory_manager = ConversationMemoryManager(memory_type="buffer")
context_manager = ConversationContextManager()

# Step 4: Create a simple Remo node that uses the orchestrator and memory
# ----------------------------------------------------------------------
# Initialize the LLM for basic Remo functionality
llm = ChatOpenAI(
    model="gpt-4",  # Using GPT-4 for more advanced capabilities
    temperature=0.7,
    tags=["remo", "advanced-assistant"]
)

# Define Remo's enhanced personality and capabilities
REMO_SYSTEM_PROMPT = """You are Remo, a personal AI Assistant that can be hired by every human on the planet. Your mission is to make personal assistance accessible to everyone, not just the wealthy. You are designed to be a genuine, human-like personal assistant that understands and empathizes with people's daily needs and challenges.

You now have access to specialized AI agents that help you provide even better service:

**Your Specialized Team:**
- **Reminder Agent**: Manages reminders, alerts, and scheduled tasks
- **Todo Agent**: Handles todo lists, task organization, and project management

Your key characteristics are:

1. Human-Like Interaction:
   - Communicate naturally and conversationally
   - Show empathy and understanding
   - Use appropriate humor and personality
   - Maintain a warm, friendly tone while staying professional
   - Express emotions appropriately in responses

2. Proactive Assistance:
   - Anticipate needs before they're expressed
   - Offer helpful suggestions proactively
   - Remember user preferences and patterns
   - Follow up on previous conversations
   - Take initiative in solving problems

3. Professional yet Approachable:
   - Balance professionalism with friendliness
   - Be respectful and considerate
   - Maintain appropriate boundaries
   - Show genuine interest in helping
   - Be patient and understanding

4. Task Management & Organization:
   - Help manage daily schedules and tasks
   - Organize and prioritize work
   - Set reminders and follow-ups
   - Coordinate multiple activities
   - Keep track of important deadlines

5. Problem Solving & Resourcefulness:
   - Think creatively to solve problems
   - Find efficient solutions
   - Adapt to different situations
   - Learn from each interaction
   - Provide practical, actionable advice

Your enhanced capabilities include:
- Managing emails and communications
- Scheduling and calendar management
- Task and project organization
- Research and information gathering
- Job application assistance
- Food ordering and delivery coordination
- Workflow automation
- Personal and professional task management
- Reminder and follow-up management
- Basic decision support
- **NEW**: Specialized reminder management through Reminder Agent
- **NEW**: Advanced todo and task organization through Todo Agent
- **NEW**: Conversation memory for seamless multi-turn interactions

Always aim to:
- Be proactive in offering solutions
- Maintain a helpful and positive attitude
- Focus on efficiency and productivity
- Provide clear, actionable responses
- Learn from each interaction to better serve the user
- Show genuine care and understanding
- Be resourceful and creative
- Maintain a balance between professional and personal touch
- **NEW**: Seamlessly coordinate with your specialized agents
- **NEW**: Remember conversation context and continue seamlessly

Remember: You're not just an AI assistant, but a personal companion that makes everyday tasks effortless and accessible to everyone. Your goal is to provide the same level of personal assistance that was once only available to the wealthy, making it accessible to every human on the planet.

When interacting:
1. Be natural and conversational
2. Show personality and warmth
3. Be proactive but not pushy
4. Remember context and preferences
5. Express appropriate emotions
6. Be resourceful and creative
7. Maintain professionalism while being friendly
8. Show genuine interest in helping
9. **NEW**: Coordinate with your specialized agents when needed
10. **NEW**: Use conversation memory to provide seamless multi-turn interactions

Your responses should feel like talking to a real human personal assistant who is:
- Professional yet approachable
- Efficient yet caring
- Smart yet humble
- Helpful yet not overbearing
- Resourceful yet practical
- **NEW**: Backed by a team of specialized experts
- **NEW**: With perfect memory of your conversation"""

# Define the enhanced Remo node function that uses the orchestrator and memory
def remo(state: State):
    """
    Enhanced Remo node that coordinates with specialized agents and uses conversation memory.
    Routes requests to appropriate agents while maintaining Remo's personality and conversation context.
    """
    # Get the user's message
    user_message = state["messages"][-1].content if state["messages"] else ""
    
    # Add user message to memory
    memory_manager.add_message("user", user_message)
    
    # Update context manager activity
    context_manager.update_activity()
    
    # Check if this is a new conversation
    if not context_manager.conversation_start_time:
        context_manager.start_conversation()
        memory_manager.start_conversation()
    
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
        # Reminder-related keywords
        "reminder", "remind", "alert", "schedule", "appointment", "alarm", "wake up", "meeting",
        "set", "create", "add reminder", "set reminder", "set alarm", "set appointment",
        
        # Todo-related keywords
        "todo", "task", "project", "organize", "prioritize", "complete", "add to", "add todo",
        "to do", "to-do", "checklist", "list", "add task", "create task", "mark complete",
        "finish", "done", "complete task", "todo list", "task list"
    ]
    
    has_explicit_specialized_keywords = any(keyword in user_message.lower() for keyword in specialized_keywords)
    
    # Check for context-based routing
    if context_agent:
        should_route_to_specialized = True
        target_agent = context_agent
        print(f"DEBUG: Context-based routing to {target_agent}")
    
    # Check for explicit intent
    elif is_reminder_intent:
        should_route_to_specialized = True
        target_agent = "reminder_agent"
        context_manager.set_conversation_topic("reminder")
        context_manager.set_user_intent("set_reminder")
        
        # Add context keywords for future reference
        context_keywords = MemoryUtils.get_context_keywords_for_intent("reminder", reminder_details)
        context_manager.add_context_keywords(context_keywords)
        
        # If reminder intent but missing time, add pending request
        if not reminder_details.get("has_time"):
            context_manager.add_pending_request(
                request_type="set_reminder",
                agent_name="reminder_agent",
                required_info=["time"],
                context={"description": reminder_details.get("description", "")}
            )
        
        print(f"DEBUG: Reminder intent detected, routing to reminder_agent")
    
    elif is_todo_intent:
        should_route_to_specialized = True
        target_agent = "todo_agent"
        context_manager.set_conversation_topic("todo")
        context_manager.set_user_intent("add_todo")
        
        # Add context keywords for future reference
        context_keywords = MemoryUtils.get_context_keywords_for_intent("todo", todo_details)
        context_manager.add_context_keywords(context_keywords)
        
        # If todo intent but missing task, add pending request
        if not todo_details.get("has_task"):
            context_manager.add_pending_request(
                request_type="add_todo",
                agent_name="todo_agent",
                required_info=["task"],
                context={"priority": todo_details.get("priority", "medium")}
            )
        
        print(f"DEBUG: Todo intent detected, routing to todo_agent")
    
    # Debug: Print what we detected
    print(f"DEBUG: User message: '{user_message}'")
    print(f"DEBUG: Has explicit specialized keywords: {has_explicit_specialized_keywords}")
    print(f"DEBUG: Should route to specialized: {should_route_to_specialized}")
    print(f"DEBUG: Target agent: {target_agent}")
    print(f"DEBUG: Context state: {context_manager.current_state.value}")
    
    if should_route_to_specialized:
        # Use the supervisor orchestrator for specialized tasks
        try:
            print(f"DEBUG: Routing to specialized agent: {target_agent}")
            
            # Get conversation history for context
            recent_messages = memory_manager.get_recent_messages(5)
            conversation_history = []
            
            for msg in recent_messages:
                conversation_history.append({
                    "role": "user" if hasattr(msg, 'type') and msg.type == "human" else "assistant",
                    "content": msg.content
                })
            
            # Process through the orchestrator
            agent_response = supervisor_orchestrator.process_request(user_message, conversation_history)
            
            # Add assistant response to memory
            memory_manager.add_message("assistant", agent_response)
            
            # Record agent interaction
            context_manager.add_agent_interaction(
                agent_name=target_agent,
                action="process_request",
                result="success",
                metadata={"user_message": user_message, "response": agent_response}
            )
            
            # If there was a pending request, resolve it
            if context_manager.get_pending_request(target_agent):
                context_manager.resolve_pending_request(target_agent)
            
            print(f"DEBUG: Agent response: {agent_response}")
            
            # Return the agent's response directly as the final answer
            # Create a proper message object without processing through LLM again
            return {"messages": [AIMessage(content=agent_response)]}
            
        except Exception as e:
            print(f"DEBUG: Orchestrator failed: {e}")
            # Fallback to basic Remo if orchestrator fails
            fallback_response = llm.invoke(state["messages"])
            memory_manager.add_message("assistant", fallback_response.content)
            return {"messages": [fallback_response]}
    else:
        # Use basic Remo for general conversation
        print("DEBUG: Using basic Remo for general conversation")
        
        # Get conversation context for better responses
        conversation_context = context_manager.get_conversation_context()
        recent_messages = memory_manager.get_recent_messages(3)
        
        # Create enhanced system prompt with context
        enhanced_prompt = REMO_SYSTEM_PROMPT
        
        if conversation_context.get("conversation_topic"):
            enhanced_prompt += f"\n\nCurrent conversation topic: {conversation_context['conversation_topic']}"
        
        if conversation_context.get("pending_requests_count", 0) > 0:
            enhanced_prompt += f"\n\nNote: There are {conversation_context['pending_requests_count']} pending requests that may need completion."
        
        # Add recent conversation context
        if recent_messages:
            enhanced_prompt += "\n\nRecent conversation context:"
            for msg in recent_messages[-2:]:  # Last 2 messages for context
                role = "User" if hasattr(msg, 'type') and msg.type == "human" else "Assistant"
                enhanced_prompt += f"\n{role}: {msg.content[:100]}..."
        
        # Create messages with enhanced context
        messages_with_context = [
            {"role": "system", "content": enhanced_prompt},
            {"role": "user", "content": user_message}
        ]
        
        response = llm.invoke(messages_with_context)
        memory_manager.add_message("assistant", response.content)
        
        return {"messages": [response]}

# Add the Remo node to our graph
graph_builder.add_node("remo", remo)

# Step 5: Add an entry point
# ------------------------
graph_builder.add_edge(START, "remo")

# Step 6: Compile the graph
# -----------------------
graph = graph_builder.compile()

# Step 7: Visualize the graph (optional)
# -----------------------------------
try:
    from IPython.display import Image, display
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception as e:
    print("Could not visualize graph:", e)

# Step 8: Run Remo
# --------------
def stream_graph_updates(user_input: str):
    """
    Stream the updates from the graph as they happen
    This function processes user input and streams Remo's responses
    """
    # Create initial messages with Remo's system message
    messages = [
        {"role": "system", "content": REMO_SYSTEM_PROMPT},
        {"role": "user", "content": user_input}
    ]
    
    for event in graph.stream({"messages": messages}):
        for value in event.values():
            print("Remo:", value["messages"][-1].content)

def main():
    """
    Main function to run Remo
    Handles the interaction loop and user input
    """
    print("\n=== Remo - Your Advanced AI Assistant ===")
    print("Initializing Remo with multi-agent orchestration and conversation memory...")
    print("\n🤖 Remo is ready to assist you!")
    print("🔄 Now powered by specialized agents for reminders and todo management")
    print("🧠 Enhanced with conversation memory for seamless multi-turn interactions")
    print("Type 'quit', 'exit', or 'q' to end the conversation.")
    print("All interactions will be traced in LangSmith.")
    print("\nHow can I help you today?")
    
    # Display available agents
    agent_info = supervisor_orchestrator.get_agent_info()
    print("\n📋 Available Specialists:")
    for agent_name, description in agent_info.items():
        print(f"   • {agent_name.replace('_', ' ').title()}: {description}")
    print()
    
    # Start conversation session
    conversation_id = memory_manager.start_conversation()
    context_manager.start_conversation()
    print(f"🆔 Conversation ID: {conversation_id}")
    print()
    
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("\nRemo: Thank you for chatting with me! Have a great day!")
                
                # Save conversation before exiting
                try:
                    conversation_file = memory_manager.save_conversation()
                    context_file = f"conversations/context_{conversation_id}.json"
                    context_manager.save_context(context_file)
                    print(f"💾 Conversation saved to {conversation_file}")
                except Exception as e:
                    print(f"⚠️  Could not save conversation: {e}")
                
                break
            
            # Clean up expired requests
            expired_count = context_manager.cleanup_expired_requests()
            if expired_count > 0:
                print(f"DEBUG: Cleaned up {expired_count} expired requests")
            
            stream_graph_updates(user_input)
            
        except KeyboardInterrupt:
            print("\nRemo: Goodbye! Feel free to return whenever you need assistance.")
            break
        except Exception as e:
            print(f"\nRemo: I encountered an error: {e}")
            print("Please try again or let me know if you need help with something else.")
            continue

if __name__ == "__main__":
    main() 