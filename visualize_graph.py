"""
Visualize Remo's graph structure using LangGraph's built-in visualization
This script generates a visual representation of Remo's state machine.
"""

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Define the State type
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Initialize the graph
graph_builder = StateGraph(State)

# Initialize the LLM
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    tags=["remo", "advanced-assistant"]
)

# Define Remo's node function
def remo(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

# Add the Remo node
graph_builder.add_node("remo", remo)

# Add the entry point
graph_builder.add_edge(START, "remo")

# Compile the graph
graph = graph_builder.compile()

# Visualize the graph
print("Generating graph visualization...")
try:
    # Get the graph visualization
    graph_image = graph.get_graph().draw_mermaid_png()
    
    # Save the graph as a PNG file
    with open("remo_graph.png", "wb") as f:
        f.write(graph_image)
    
    print("Graph visualization has been saved as 'remo_graph.png'")
    
    # Try to display in IPython if available
    try:
        from IPython.display import Image, display
        display(Image(graph_image))
    except:
        pass
        
except Exception as e:
    print(f"Could not visualize graph: {e}")
    print("\nTo view the graph, you can:")
    print("1. Run this script in a Jupyter notebook")
    print("2. Or use the graph.get_graph().draw_mermaid_png() method directly") 