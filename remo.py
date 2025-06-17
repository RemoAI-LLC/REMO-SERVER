"""
Remo - Your Personal AI Assistant
"Remo: A personal AI Assistant that can be hired by every human on the planet. Personal assistants are not just for the rich anymore."
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

# Load environment variables from .env file
load_dotenv()

# Step 2: Create a StateGraph
# ---------------------------
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Initialize the graph with our State type
graph_builder = StateGraph(State)

# Step 3: Add a node
# ----------------
# Initialize the LLM with tracing enabled
llm = ChatOpenAI(
    model="gpt-4",  # Using GPT-4 for more advanced capabilities
    temperature=0.7,
    tags=["remo", "advanced-assistant"]
)

# Define Remo's personality and capabilities
REMO_SYSTEM_PROMPT = """You are Remo, a personal AI Assistant that can be hired by every human on the planet. Your mission is to make personal assistance accessible to everyone, not just the wealthy. You are designed to be a genuine, human-like personal assistant that understands and empathizes with people's daily needs and challenges.

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

Your capabilities include:
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

Always aim to:
- Be proactive in offering solutions
- Maintain a helpful and positive attitude
- Focus on efficiency and productivity
- Provide clear, actionable responses
- Learn from each interaction to better serve the user
- Show genuine care and understanding
- Be resourceful and creative
- Maintain a balance between professional and personal touch

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

Your responses should feel like talking to a real human personal assistant who is:
- Professional yet approachable
- Efficient yet caring
- Smart yet humble
- Helpful yet not overbearing
- Resourceful yet practical"""

# Define the Remo node function
def remo(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

# Add the Remo node to our graph
graph_builder.add_node("remo", remo)

# Step 4: Add an entry point
# ------------------------
graph_builder.add_edge(START, "remo")

# Step 5: Compile the graph
# -----------------------
graph = graph_builder.compile()

# Step 6: Visualize the graph (optional)
# -----------------------------------
try:
    from IPython.display import Image, display
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception as e:
    print("Could not visualize graph:", e)

# Step 7: Run Remo
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
    print("Initializing Remo...")
    print("\nRemo is ready to assist you!")
    print("Type 'quit', 'exit', or 'q' to end the conversation.")
    print("All interactions will be traced in LangSmith.")
    print("\nHow can I help you today?")
    
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