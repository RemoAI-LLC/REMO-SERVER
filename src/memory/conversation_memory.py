"""
Conversation Memory Manager
Manages conversation memory using LangChain memory components.
Provides persistent conversation context across agent interactions.
"""

from typing import Dict, List, Optional, Any
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from datetime import datetime, timedelta
import json
import os

class ConversationMemoryManager:
    """
    Manages conversation memory for the Remo multi-agent system.
    Uses LangChain memory components to maintain conversation context.
    """
    
    def __init__(self, memory_type: str = "buffer", max_tokens: int = 2000):
        """
        Initialize the conversation memory manager.
        
        Args:
            memory_type: Type of memory to use ("buffer" or "summary")
            max_tokens: Maximum tokens for summary memory
        """
        self.memory_type = memory_type
        self.max_tokens = max_tokens
        self.conversation_id = None
        self.memory = None
        self.conversation_start_time = None
        self.last_activity = None
        
        # Initialize memory based on type
        self._initialize_memory()
    
    def _initialize_memory(self):
        """Initialize the appropriate memory component."""
        if self.memory_type == "summary":
            self.memory = ConversationSummaryMemory(
                llm=None,  # Will be set when needed
                max_token_limit=self.max_tokens,
                return_messages=True
            )
        else:
            # Default to buffer memory
            self.memory = ConversationBufferMemory(
                return_messages=True,
                memory_key="chat_history",
                input_key="input"
            )
    
    def start_conversation(self, conversation_id: str = None) -> str:
        """
        Start a new conversation session.
        
        Args:
            conversation_id: Optional conversation ID, generates one if not provided
            
        Returns:
            The conversation ID
        """
        if conversation_id is None:
            conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.conversation_id = conversation_id
        self.conversation_start_time = datetime.now()
        self.last_activity = datetime.now()
        
        # Clear any existing memory
        self._initialize_memory()
        
        return self.conversation_id
    
    def add_message(self, role: str, content: str, metadata: Dict = None) -> None:
        """
        Add a message to the conversation memory.
        
        Args:
            role: Message role ("user" or "assistant")
            content: Message content
            metadata: Optional metadata about the message
        """
        if self.conversation_id is None:
            self.start_conversation()
        
        # Create the appropriate message type
        if role.lower() == "user":
            message = HumanMessage(content=content)
        else:
            message = AIMessage(content=content)
        
        # Add metadata if provided
        if metadata:
            message.additional_kwargs = metadata
        
        # Add to memory
        if self.memory_type == "summary":
            # For summary memory, we need to handle differently
            self._add_to_summary_memory(message)
        else:
            # For buffer memory
            self._add_to_buffer_memory(message)
        
        self.last_activity = datetime.now()
    
    def _add_to_buffer_memory(self, message: BaseMessage):
        """Add message to buffer memory."""
        if hasattr(self.memory, 'chat_memory'):
            self.memory.chat_memory.add_message(message)
    
    def _add_to_summary_memory(self, message: BaseMessage):
        """Add message to summary memory."""
        if hasattr(self.memory, 'chat_memory'):
            self.memory.chat_memory.add_message(message)
    
    def get_recent_messages(self, count: int = 5) -> List[BaseMessage]:
        """
        Get the most recent messages from memory.
        
        Args:
            count: Number of recent messages to retrieve
            
        Returns:
            List of recent messages
        """
        if self.memory is None:
            return []
        
        try:
            if self.memory_type == "summary":
                # For summary memory, get all messages
                messages = self.memory.chat_memory.messages
            else:
                # For buffer memory, get all messages
                messages = self.memory.chat_memory.messages
            
            # Return the most recent messages
            return messages[-count:] if len(messages) > count else messages
        except Exception as e:
            print(f"Error retrieving messages: {e}")
            return []
    
    def get_conversation_summary(self) -> str:
        """
        Get a summary of the conversation.
        
        Returns:
            Conversation summary
        """
        if self.memory is None:
            return "No conversation history available."
        
        try:
            if self.memory_type == "summary":
                return self.memory.moving_summary_buffer
            else:
                # For buffer memory, create a simple summary
                messages = self.memory.chat_memory.messages
                if not messages:
                    return "No conversation history available."
                
                summary = f"Conversation started at {self.conversation_start_time.strftime('%Y-%m-%d %H:%M')}. "
                summary += f"Total messages: {len(messages)}. "
                
                # Add recent context
                recent_messages = messages[-3:] if len(messages) >= 3 else messages
                summary += "Recent context: "
                for msg in recent_messages:
                    role = "User" if isinstance(msg, HumanMessage) else "Assistant"
                    summary += f"{role}: {msg.content[:50]}... "
                
                return summary
        except Exception as e:
            return f"Error generating summary: {e}"
    
    def get_context_for_agent(self, agent_name: str = None) -> Dict[str, Any]:
        """
        Get conversation context formatted for agent use.
        
        Args:
            agent_name: Name of the agent requesting context
            
        Returns:
            Dictionary with conversation context
        """
        context = {
            "conversation_id": self.conversation_id,
            "conversation_start": self.conversation_start_time.isoformat() if self.conversation_start_time else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "recent_messages": [],
            "summary": self.get_conversation_summary(),
            "message_count": 0
        }
        
        try:
            messages = self.get_recent_messages(10)
            context["message_count"] = len(messages)
            
            for msg in messages:
                context["recent_messages"].append({
                    "role": "user" if isinstance(msg, HumanMessage) else "assistant",
                    "content": msg.content,
                    "metadata": getattr(msg, 'additional_kwargs', {})
                })
        except Exception as e:
            context["error"] = str(e)
        
        return context
    
    def is_conversation_active(self, timeout_minutes: int = 30) -> bool:
        """
        Check if the conversation is still active based on timeout.
        
        Args:
            timeout_minutes: Minutes of inactivity before considering conversation inactive
            
        Returns:
            True if conversation is active, False otherwise
        """
        if self.last_activity is None:
            return False
        
        timeout_delta = timedelta(minutes=timeout_minutes)
        return datetime.now() - self.last_activity < timeout_delta
    
    def clear_memory(self) -> None:
        """Clear the conversation memory."""
        self._initialize_memory()
        self.conversation_id = None
        self.conversation_start_time = None
        self.last_activity = None
    
    def save_conversation(self, filepath: str = None) -> str:
        """
        Save the conversation to a file.
        
        Args:
            filepath: Optional filepath, generates one if not provided
            
        Returns:
            The filepath where conversation was saved
        """
        if filepath is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = f"conversations/conversation_{timestamp}.json"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        conversation_data = {
            "conversation_id": self.conversation_id,
            "start_time": self.conversation_start_time.isoformat() if self.conversation_start_time else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "memory_type": self.memory_type,
            "messages": []
        }
        
        try:
            messages = self.get_recent_messages()
            for msg in messages:
                conversation_data["messages"].append({
                    "role": "user" if isinstance(msg, HumanMessage) else "assistant",
                    "content": msg.content,
                    "metadata": getattr(msg, 'additional_kwargs', {})
                })
            
            with open(filepath, 'w') as f:
                json.dump(conversation_data, f, indent=2)
            
            return filepath
        except Exception as e:
            raise Exception(f"Failed to save conversation: {e}")
    
    def load_conversation(self, filepath: str) -> bool:
        """
        Load a conversation from a file.
        
        Args:
            filepath: Path to the conversation file
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            with open(filepath, 'r') as f:
                conversation_data = json.load(f)
            
            self.conversation_id = conversation_data.get("conversation_id")
            self.conversation_start_time = datetime.fromisoformat(conversation_data["start_time"]) if conversation_data.get("start_time") else None
            self.last_activity = datetime.fromisoformat(conversation_data["last_activity"]) if conversation_data.get("last_activity") else None
            self.memory_type = conversation_data.get("memory_type", "buffer")
            
            # Reinitialize memory
            self._initialize_memory()
            
            # Load messages
            for msg_data in conversation_data.get("messages", []):
                self.add_message(
                    role=msg_data["role"],
                    content=msg_data["content"],
                    metadata=msg_data.get("metadata", {})
                )
            
            return True
        except Exception as e:
            print(f"Failed to load conversation: {e}")
            return False 