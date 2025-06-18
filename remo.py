"""
Remo - Your Personal AI Assistant
"Remo: A personal AI Assistant that can be hired by every human on the planet. Personal assistants are not just for the rich anymore."

Now powered by multi-agent orchestration with specialized agents for reminders and todo management.
"""

# Step 1: Import required packages
# ------------------------------
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Import the multi-agent orchestration system
from src.orchestration import SupervisorOrchestrator

# Load environment variables from .env file
load_dotenv()

# Step 2: Create a StateGraph (kept for compatibility)
# ---------------------------
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Initialize the graph with our State type
graph_builder = StateGraph(State)

# Step 3: Initialize the multi-agent orchestrator
# ----------------------------------------------
# Initialize the supervisor orchestrator with specialized agents
supervisor_orchestrator = SupervisorOrchestrator(model_name="gpt-4")

# Step 4: Create a simple Remo node that uses the orchestrator
# -----------------------------------------------------------
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

Your responses should feel like talking to a real human personal assistant who is:
- Professional yet approachable
- Efficient yet caring
- Smart yet humble
- Helpful yet not overbearing
- Resourceful yet practical
- **NEW**: Backed by a team of specialized experts"""

# Define the enhanced Remo node function that uses the orchestrator
def remo(state: State):
    """
    Enhanced Remo node that coordinates with specialized agents.
    Routes requests to appropriate agents while maintaining Remo's personality.
    """
    # Get the user's message
    user_message = state["messages"][-1].content if state["messages"] else ""
    
    # Check if the request involves specialized tasks (reminders or todos)
    specialized_keywords = [
        # Reminder-related keywords
        "reminder", "remind", "alert", "schedule", "appointment", "alarm", "wake up", "meeting",
        "set", "create", "add reminder", "set reminder", "set alarm", "set appointment",
        
        # Todo-related keywords
        "todo", "task", "project", "organize", "prioritize", "complete", "add to", "add todo",
        "to do", "to-do", "checklist", "list", "add task", "create task", "mark complete",
        "finish", "done", "complete task", "todo list", "task list"
    ]
    
    has_specialized_request = any(keyword in user_message.lower() for keyword in specialized_keywords)
    
    # Debug: Print what we detected
    print(f"DEBUG: User message: '{user_message}'")
    print(f"DEBUG: Has specialized request: {has_specialized_request}")
    
    if has_specialized_request:
        # Use the supervisor orchestrator for specialized tasks
        try:
            print("DEBUG: Routing to specialized agents...")
            # Convert state messages to the format expected by the orchestrator
            conversation_history = []
            for msg in state["messages"][:-1]:  # Exclude the current user message
                conversation_history.append({
                    "role": msg.type,
                    "content": msg.content
                })
            
            # Process through the orchestrator
            response = supervisor_orchestrator.process_request(user_message, conversation_history)
            print(f"DEBUG: Agent response: {response}")
            return {"messages": [llm.invoke([{"role": "system", "content": REMO_SYSTEM_PROMPT}, {"role": "user", "content": response}])]}
        except Exception as e:
            print(f"DEBUG: Orchestrator failed: {e}")
            # Fallback to basic Remo if orchestrator fails
            return {"messages": [llm.invoke(state["messages"])]}
    else:
        # Use basic Remo for general conversation
        print("DEBUG: Using basic Remo for general conversation")
        return {"messages": [llm.invoke(state["messages"])]}

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
    print("Initializing Remo with multi-agent orchestration...")
    print("\n🤖 Remo is ready to assist you!")
    print("🔄 Now powered by specialized agents for reminders and todo management")
    print("Type 'quit', 'exit', or 'q' to end the conversation.")
    print("All interactions will be traced in LangSmith.")
    print("\nHow can I help you today?")
    
    # Display available agents
    agent_info = supervisor_orchestrator.get_agent_info()
    print("\n📋 Available Specialists:")
    for agent_name, description in agent_info.items():
        print(f"   • {agent_name.replace('_', ' ').title()}: {description}")
    print()
    
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("\nRemo: Thank you for chatting with me! Have a great day!")
                break
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