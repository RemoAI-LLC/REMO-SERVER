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
from ..utils.dynamodb_service import DynamoDBService

class ConversationMemoryManager:
    """
    Manages conversation memory for the Remo multi-agent system.
    Uses LangChain memory components to maintain conversation context.
    """
    
    def __init__(self, memory_type: str = "buffer", max_tokens: int = 2000, user_id: str = None):
        """
        Initialize the conversation memory manager.
        
        Args:
            memory_type: Type of memory to use ("buffer" or "summary")
            max_tokens: Maximum tokens for summary memory
            user_id: Privy user ID for user-specific storage
        """
        self.memory_type = memory_type
        self.max_tokens = max_tokens
        self.user_id = user_id
        self.conversation_id = None
        self.memory = None
        self.conversation_start_time = None
        self.last_activity = None
        
        # Initialize DynamoDB service for user-specific storage
        self.dynamodb_service = DynamoDBService()
        
        # Initialize memory based on type
        self._initialize_memory()
        
        # Load existing memory if user_id is provided
        if self.user_id:
            self._load_user_memory()
    
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
    
    def _load_user_memory(self):
        """Load user-specific memory from DynamoDB."""
        if not self.user_id:
            return
        
        try:
            # Load conversation memory
            memory_data = self.dynamodb_service.load_conversation_memory(self.user_id)
            if memory_data:
                self.conversation_id = memory_data.get('conversation_id')
                self.conversation_start_time = datetime.fromisoformat(memory_data.get('conversation_start_time')) if memory_data.get('conversation_start_time') else None
                self.last_activity = datetime.fromisoformat(memory_data.get('last_activity')) if memory_data.get('last_activity') else None
                
                # Restore messages if available
                if memory_data.get('messages'):
                    for msg_data in memory_data['messages']:
                        if msg_data.get('role') == 'user':
                            message = HumanMessage(content=msg_data.get('content', ''))
                        else:
                            message = AIMessage(content=msg_data.get('content', ''))
                        
                        if hasattr(self.memory, 'chat_memory'):
                            self.memory.chat_memory.add_message(message)
                
                print(f"Loaded conversation memory for user {self.user_id}")
        except Exception as e:
            print(f"Error loading user memory: {e}")
    
    def _save_user_memory(self):
        """Save user-specific memory to DynamoDB."""
        if not self.user_id:
            return
        
        try:
            # Prepare memory data for storage
            memory_data = {
                'conversation_id': self.conversation_id,
                'conversation_start_time': self.conversation_start_time.isoformat() if self.conversation_start_time else None,
                'last_activity': self.last_activity.isoformat() if self.last_activity else None,
                'memory_type': self.memory_type,
                'messages': []
            }
            
            # Add messages if available
            if hasattr(self.memory, 'chat_memory') and self.memory.chat_memory.messages:
                for msg in self.memory.chat_memory.messages:
                    msg_data = {
                        'role': 'user' if isinstance(msg, HumanMessage) else 'assistant',
                        'content': msg.content,
                        'timestamp': datetime.now().isoformat()
                    }
                    memory_data['messages'].append(msg_data)
            
            # Save to DynamoDB
            self.dynamodb_service.save_conversation_memory(self.user_id, memory_data)
            
        except Exception as e:
            print(f"Error saving user memory: {e}")
    
    def set_user_id(self, user_id: str):
        """Set the user ID and load existing memory."""
        self.user_id = user_id
        self._load_user_memory()
    
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
        
        # Save to DynamoDB if user_id is set
        if self.user_id:
            self._save_user_memory()
        
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
        
        # Save to DynamoDB if user_id is set
        if self.user_id:
            self._save_user_memory()
    
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
            "message_count": 0,
            "user_id": self.user_id
        }
        
        try:
            messages = self.get_recent_messages(10)
            context["message_count"] = len(messages)
            
            # Convert messages to serializable format
            for msg in messages:
                context["recent_messages"].append({
                    "role": "user" if isinstance(msg, HumanMessage) else "assistant",
                    "content": msg.content,
                    "timestamp": datetime.now().isoformat()
                })
        except Exception as e:
            print(f"Error getting context for agent: {e}")
        
        return context
    
    def is_conversation_active(self, timeout_minutes: int = 30) -> bool:
        """
        Check if the conversation is still active based on last activity.
        
        Args:
            timeout_minutes: Minutes of inactivity before considering conversation inactive
            
        Returns:
            True if conversation is active, False otherwise
        """
        if not self.last_activity:
            return False
        
        timeout_delta = timedelta(minutes=timeout_minutes)
        return datetime.now() - self.last_activity < timeout_delta
    
    def clear_memory(self) -> None:
        """Clear all conversation memory."""
        self._initialize_memory()
        self.conversation_id = None
        self.conversation_start_time = None
        self.last_activity = None
        
        # Save cleared state to DynamoDB if user_id is set
        if self.user_id:
            self._save_user_memory()
    
    def save_conversation(self, filepath: str = None) -> str:
        """
        Save conversation to a file (legacy method, now uses DynamoDB).
        
        Args:
            filepath: Optional filepath (not used with DynamoDB)
            
        Returns:
            Success message
        """
        if self.user_id:
            self._save_user_memory()
            return f"Conversation saved to DynamoDB for user {self.user_id}"
        else:
            return "No user ID set, cannot save to DynamoDB"
    
    def load_conversation(self, filepath: str) -> bool:
        """
        Load conversation from a file (legacy method, now uses DynamoDB).
        
        Args:
            filepath: Filepath (not used with DynamoDB)
            
        Returns:
            True if successful, False otherwise
        """
        if self.user_id:
            self._load_user_memory()
            return True
        else:
            return False 