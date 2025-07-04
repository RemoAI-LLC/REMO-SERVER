"""
Visualize Remo's Multi-Agent Graph Structure with Memory System
This script generates a visual representation of Remo's complete multi-agent orchestration system.
Shows the supervisor pattern with specialized agents, conversation memory, and context management.
"""

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import os

# Import the multi-agent orchestration system
from src.orchestration import SupervisorOrchestrator

# Import the memory system
from src.memory import ConversationMemoryManager, ConversationContextManager, MemoryUtils

# Load environment variables
load_dotenv()

try:
    from langchain_aws import ChatBedrock
except ImportError:
    ChatBedrock = None
import boto3
import json

def visualize_complete_system():
    """Visualize the complete Remo system including memory and multi-agent orchestration."""
    
    print("🎭 Remo Complete System Visualization")
    print("=" * 60)
    
    # Initialize the supervisor orchestrator
    try:
        supervisor_orchestrator = SupervisorOrchestrator(model_name=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0"))
        print("✅ Multi-agent system initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize multi-agent system: {e}")
        return
    
    # Initialize memory system
    try:
        memory_manager = ConversationMemoryManager(memory_type="buffer")
        context_manager = ConversationContextManager()
        print("✅ Memory system initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize memory system: {e}")
        return
    
    # Get the supervisor graph
    supervisor_graph = supervisor_orchestrator.get_supervisor()
    
    # Visualize the supervisor graph
    print("\n📊 Generating complete system graph visualization...")
    try:
        # Get the graph visualization
        graph_image = supervisor_graph.get_graph().draw_mermaid_png()
        
        # Save the graph as a PNG file
        with open("remo_complete_system_graph.png", "wb") as f:
            f.write(graph_image)
        
        print("✅ Complete system graph visualization saved as 'remo_complete_system_graph.png'")
        
        # Try to display in IPython if available
        try:
            from IPython.display import Image, display
            display(Image(graph_image))
            print("📱 Graph displayed in notebook")
        except:
            print("💻 Run in Jupyter notebook to see inline visualization")
            
    except Exception as e:
        print(f"❌ Could not visualize system graph: {e}")
    
    # Show complete system architecture
    print("\n🏗️ Complete System Architecture:")
    print("-" * 40)
    print("User Input → Remo Entrypoint")
    print("                ↓")
    print("        ┌─────────────────────────────────┐")
    print("        │        Memory System            │")
    print("        │  ┌─────────────────────────────┐ │")
    print("        │  │ ConversationMemoryManager   │ │")
    print("        │  │ • Buffer/Summary Memory     │ │")
    print("        │  │ • Message History           │ │")
    print("        │  │ • Conversation Persistence  │ │")
    print("        │  └─────────────────────────────┘ │")
    print("        │  ┌─────────────────────────────┐ │")
    print("        │  │ ConversationContextManager  │ │")
    print("        │  │ • Pending Requests          │ │")
    print("        │  │ • Context Keywords          │ │")
    print("        │  │ • Agent Interaction History │ │")
    print("        │  └─────────────────────────────┘ │")
    print("        │  ┌─────────────────────────────┐ │")
    print("        │  │ MemoryUtils                 │ │")
    print("        │  │ • Intent Detection          │ │")
    print("        │  │ • Time/Task Extraction      │ │")
    print("        │  │ • Context Analysis          │ │")
    print("        │  └─────────────────────────────┘ │")
    print("        └─────────────────────────────────┘")
    print("                ↓")
    print("        ┌─────────────────────────────────┐")
    print("        │    Supervisor Orchestrator      │")
    print("        │ • Intelligent Routing           │")
    print("        │ • Multi-Agent Coordination      │")
    print("        │ • Response Aggregation          │")
    print("        └─────────────────────────────────┘")
    print("                ↓")
    print("        ┌─────────────────────────────────┐")
    print("        │      Specialized Agents         │")
    print("        │  ┌─────────────┬─────────────┐  │")
    print("        │  │ Reminder    │ Todo        │  │")
    print("        │  │ Agent       │ Agent       │  │")
    print("        │  │             │             │  │")
    print("        │  │ • set_reminder│ • add_todo│  │")
    print("        │  │ • list_reminders│ • list_todos│")
    print("        │  │ • update_reminder│ • mark_complete│")
    print("        │  │ • delete_reminder│ • update_todo│")
    print("        │  │ • mark_complete│ • delete_todo│")
    print("        │  │             │ • prioritize│  │")
    print("        │  └─────────────┴─────────────┘  │")
    print("        └─────────────────────────────────┘")
    print("                ↓")
    print("        Coordinated Response → User")

def visualize_memory_system():
    """Visualize the memory system components and flow."""
    
    print("\n🧠 Memory System Architecture:")
    print("-" * 35)
    print("Conversation Flow with Memory:")
    print()
    print("1. User Input")
    print("   ↓")
    print("2. MemoryManager.add_message()")
    print("   ↓")
    print("3. ContextManager.update_activity()")
    print("   ↓")
    print("4. MemoryUtils.detect_intent()")
    print("   ↓")
    print("5. ContextManager.should_route_to_agent()")
    print("   ↓")
    print("6. Agent Processing with Context")
    print("   ↓")
    print("7. MemoryManager.add_message() (Response)")
    print("   ↓")
    print("8. ContextManager.resolve_pending_request()")
    print()
    
    print("Memory Types Supported:")
    print("• Buffer Memory (Default): Exact conversation history")
    print("• Summary Memory: Compressed conversation history")
    print("• Vector Memory (Future): Semantic search across conversations")
    print("• Entity Memory (Future): Person/entity tracking")
    print()
    
    print("Context Management Features:")
    print("• Pending Request Tracking")
    print("• Context Keyword Generation")
    print("• Agent Interaction History")
    print("• Conversation State Management")
    print("• Intent Detection & Routing")

def visualize_agent_capabilities():
    """Visualize the capabilities of each specialized agent."""
    
    print("\n🤖 Agent Capabilities Overview:")
    print("-" * 35)
    
    # Reminder Agent
    print("📅 Reminder Agent:")
    print("   Tools:")
    print("   • set_reminder(title, datetime_str, description)")
    print("   • list_reminders(show_completed)")
    print("   • update_reminder(reminder_id, title, datetime_str, description)")
    print("   • delete_reminder(reminder_id)")
    print("   • mark_reminder_complete(reminder_id)")
    print("   Memory Features:")
    print("   • Remembers incomplete reminder requests")
    print("   • Recognizes time expressions in follow-up messages")
    print("   • Maintains context across conversation turns")
    print("   • Handles multi-turn reminder setup")
    print()
    
    # Todo Agent
    print("✅ Todo Agent:")
    print("   Tools:")
    print("   • add_todo(title, description, priority, category)")
    print("   • list_todos(category, show_completed, priority)")
    print("   • mark_todo_complete(todo_id)")
    print("   • update_todo(todo_id, title, description, priority, category)")
    print("   • delete_todo(todo_id)")
    print("   • prioritize_todos()")
    print("   Memory Features:")
    print("   • Remembers incomplete todo requests")
    print("   • Recognizes task descriptions in follow-up messages")
    print("   • Maintains priority and category context")
    print("   • Handles multi-turn todo creation")
    print()

def visualize_multi_turn_examples():
    """Show examples of multi-turn conversations with memory."""
    
    print("\n🔄 Multi-Turn Conversation Examples:")
    print("-" * 40)
    
    print("Example 1: Reminder Setup")
    print("User: 'Set a reminder for tomorrow'")
    print("Remo: 'What time would you like the reminder?'")
    print("User: '6am'")
    print("Remo: 'Perfect! I'll set your reminder for tomorrow at 6am.'")
    print("✅ Memory maintains context between turns")
    print()
    
    print("Example 2: Todo Creation")
    print("User: 'Add a high priority todo'")
    print("Remo: 'What task would you like to add?'")
    print("User: 'finish project report'")
    print("Remo: 'I'll add that high priority task to your todo list.'")
    print("✅ Memory remembers priority context")
    print()
    
    print("Example 3: Context Switching")
    print("User: 'Set an alarm for tomorrow'")
    print("Remo: 'What time would you like the alarm?'")
    print("User: 'Actually make it 7am'")
    print("Remo: 'I'll update your alarm to 7am tomorrow.'")
    print("✅ Memory handles context updates")

def show_system_stats():
    """Show system statistics and information."""
    
    print("\n📊 System Statistics:")
    print("-" * 25)
    
    # Agent information
    try:
        supervisor_orchestrator = SupervisorOrchestrator(model_name=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0"))
        agent_info = supervisor_orchestrator.get_agent_info()
        print(f"• Specialized Agents: {len(agent_info)}")
        for agent_name, description in agent_info.items():
            print(f"  - {agent_name.replace('_', ' ').title()}: {description}")
    except Exception as e:
        print(f"• Specialized Agents: Error loading - {e}")
    
    # Memory system info
    print("• Memory System Components: 3")
    print("  - ConversationMemoryManager")
    print("  - ConversationContextManager") 
    print("  - MemoryUtils")
    
    # Supported memory types
    print("• Memory Types Supported: 4")
    print("  - Buffer Memory (Current)")
    print("  - Summary Memory")
    print("  - Vector Memory (Future)")
    print("  - Entity Memory (Future)")
    
    # Intent detection
    print("• Intent Detection: 2 types")
    print("  - Reminder Intent")
    print("  - Todo Intent")
    
    # Tools available
    print("• Total Tools Available: 11")
    print("  - Reminder Tools: 5")
    print("  - Todo Tools: 6")

def main():
    """Main function to run complete system visualization."""
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key in the .env file")
        return
    
    # Visualize complete system
    visualize_complete_system()
    
    # Visualize memory system
    visualize_memory_system()
    
    # Visualize agent capabilities
    visualize_agent_capabilities()
    
    # Show multi-turn examples
    visualize_multi_turn_examples()
    
    # Show system stats
    show_system_stats()
    
    print("\n🎉 Complete system visualization finished!")
    print("\n📁 Generated files:")
    print("   • remo_complete_system_graph.png - Complete system structure")
    print("\n💡 The visualization shows:")
    print("   • Multi-agent orchestration with supervisor pattern")
    print("   • Conversation memory system with context management")
    print("   • Specialized agents with focused capabilities")
    print("   • Multi-turn conversation support")
    print("   • Intent detection and intelligent routing")
    print("\n🚀 Remo is now a truly conversational AI assistant!")

if __name__ == "__main__":
    main() 