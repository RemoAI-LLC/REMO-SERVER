"""
Build a basic chatbot using LangGraph with LangSmith tracing
This chatbot is the basis for building more sophisticated capabilities and introduces key LangGraph concepts.
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
# This is where your OpenAI API key should be stored
load_dotenv()

# Step 2: Create a StateGraph
# ---------------------------
# Define the State type for our graph
# State is a TypedDict that defines what data our chatbot will maintain
class State(TypedDict):
    # Messages will be a list that gets appended to rather than overwritten
    # thanks to the add_messages annotation
    messages: Annotated[list, add_messages]

# Initialize the graph with our State type
# This creates a state machine that will manage our chatbot's flow
graph_builder = StateGraph(State)

# Step 3: Add a node
# ----------------
# Initialize the LLM (Language Model) with tracing enabled
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    # Enable tracing for this LLM
    tags=["chatbot", "langgraph-tutorial"]
)

# Define the chatbot node function
# This function will be called each time we need to generate a response
def chatbot(state: State):
    # The function takes the current state and returns a dictionary
    # with the updated messages
    return {"messages": [llm.invoke(state["messages"])]}

# Add the chatbot node to our graph
# The first argument is the node name, second is the function to call
graph_builder.add_node("chatbot", chatbot)

# Step 4: Add an entry point
# ------------------------
# Add an edge from START to our chatbot node
# This tells the graph where to begin processing each time it runs
graph_builder.add_edge(START, "chatbot")

# Step 5: Compile the graph
# -----------------------
# Compile the graph to make it executable
# This creates a CompiledGraph we can invoke on our state
graph = graph_builder.compile()

# Step 6: Visualize the graph (optional)
# -----------------------------------
# You can visualize the graph using the get_graph method
# This requires IPython and additional dependencies
try:
    from IPython.display import Image, display
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception as e:
    print("Could not visualize graph:", e)

# Step 7: Run the chatbot
# ---------------------
def stream_graph_updates(user_input: str):
    """
    Stream the updates from the graph as they happen
    This function processes user input and streams the bot's responses
    """
    # Create initial messages with system message
    messages = [
        {"role": "system", "content": "You are a helpful, friendly assistant who always answers cheerfully."},
        {"role": "user", "content": user_input}
    ]
    
    for event in graph.stream({"messages": messages}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)

def main():
    """
    Main function to run the chatbot
    Handles the chat loop and user interaction
    """
    print("Chatbot initialized! Type 'quit', 'exit', or 'q' to end the conversation.")
    print("All interactions will be traced in LangSmith under project: pr-crazy-thump-12")
    
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            stream_graph_updates(user_input)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break

if __name__ == "__main__":
    main() 