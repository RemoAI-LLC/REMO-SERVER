"""
Visualize Remo's Multi-Agent Graph Structure
This script generates a visual representation of Remo's multi-agent orchestration system.
Shows the supervisor pattern with specialized agents for reminders and todos.
"""

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Import the multi-agent orchestration system
from src.orchestration import SupervisorOrchestrator

# Load environment variables
load_dotenv()

def visualize_multi_agent_system():
    """Visualize the multi-agent orchestration system."""
    
    print("🎭 Remo Multi-Agent System Visualization")
    print("=" * 50)
    
    # Initialize the supervisor orchestrator
    try:
        supervisor_orchestrator = SupervisorOrchestrator(model_name="gpt-4")
        print("✅ Multi-agent system initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize multi-agent system: {e}")
        return
    
    # Get the supervisor graph
    supervisor_graph = supervisor_orchestrator.get_supervisor()
    
    # Visualize the supervisor graph
    print("\n📊 Generating multi-agent graph visualization...")
    try:
        # Get the graph visualization
        graph_image = supervisor_graph.get_graph().draw_mermaid_png()
        
        # Save the graph as a PNG file
        with open("remo_multi_agent_graph.png", "wb") as f:
            f.write(graph_image)
        
        print("✅ Multi-agent graph visualization saved as 'remo_multi_agent_graph.png'")
        
        # Try to display in IPython if available
        try:
            from IPython.display import Image, display
            display(Image(graph_image))
            print("📱 Graph displayed in notebook")
        except:
            print("💻 Run in Jupyter notebook to see inline visualization")
            
    except Exception as e:
        print(f"❌ Could not visualize multi-agent graph: {e}")
    
    # Show agent information
    print("\n🤖 Multi-Agent System Overview:")
    print("-" * 30)
    agent_info = supervisor_orchestrator.get_agent_info()
    for agent_name, description in agent_info.items():
        print(f"• {agent_name.replace('_', ' ').title()}: {description}")
    
    # Show system architecture
    print("\n🏗️ System Architecture:")
    print("-" * 25)
    print("User Input → Remo (Supervisor) → Specialized Agents")
    print("                ↓")
    print("        ┌─────────────┬─────────────┐")
    print("        │ Reminder    │ Todo        │")
    print("        │ Agent       │ Agent       │")
    print("        │             │             │")
    print("        │ • Set       │ • Add       │")
    print("        │ • List      │ • List      │")
    print("        │ • Update    │ • Update    │")
    print("        │ • Delete    │ • Delete    │")
    print("        │ • Complete  │ • Complete  │")
    print("        └─────────────┴─────────────┘")
    print("                ↓")
    print("        Coordinated Response → User")

def main():
    """Main function to run multi-agent visualization."""
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key in the .env file")
        return
    
    # Visualize multi-agent system
    visualize_multi_agent_system()
    
    print("\n🎉 Multi-agent visualization complete!")
    print("\n📁 Generated file:")
    print("   • remo_multi_agent_graph.png - Multi-agent system structure")
    print("\n💡 The graph shows the supervisor pattern with specialized agents")

if __name__ == "__main__":
    main() 