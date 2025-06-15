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
    model="gpt-3.5-turbo",
    temperature=0.7
)

# Define the chatbot node
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

# Add the node and edge
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")

# Compile the graph
graph = graph_builder.compile()

# Visualize the graph
print("Generating graph visualization...")
try:
    # Get the graph structure
    graph_structure = graph.get_graph()
    
    # Print the graph structure in a readable format
    print("\nGraph Structure:")
    print("---------------")
    print("Nodes:")
    for node in graph_structure.nodes:
        print(f"  - {node}")
    
    print("\nEdges:")
    for edge in graph_structure.edges:
        print(f"  - {edge[0]} -> {edge[1]}")
    
    # Try to save as a simple text file
    with open("chatbot_graph.txt", "w") as f:
        f.write("Chatbot Graph Structure\n")
        f.write("=====================\n\n")
        f.write("Nodes:\n")
        for node in graph_structure.nodes:
            f.write(f"  - {node}\n")
        f.write("\nEdges:\n")
        for edge in graph_structure.edges:
            f.write(f"  - {edge[0]} -> {edge[1]}\n")
    
    print("\nGraph structure has been saved to 'chatbot_graph.txt'")
    
except Exception as e:
    print(f"Error visualizing graph: {e}") 