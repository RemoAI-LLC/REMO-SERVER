"""
Conversation Context Manager
Manages conversation context, pending requests, and agent interaction state.
Provides intelligent routing based on conversation history and context.
"""

from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from enum import Enum
import json
import sys
import os
import re

# Add the parent directory to the path to import DynamoDB service (optional)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
try:
    from utils.dynamodb_service import DynamoDBService
    DYNAMODB_AVAILABLE = True
except ImportError:
    DYNAMODB_AVAILABLE = False

class ConversationState(Enum):
    """Enumeration of possible conversation states."""
    IDLE = "idle"
    WAITING_FOR_INPUT = "waiting_for_input"
    AGENT_ACTIVE = "agent_active"
    MULTI_AGENT = "multi_agent"
    ERROR = "error"

class PendingRequest:
    """Represents a pending request that needs additional information."""
    
    def __init__(self, request_type: str, agent_name: str, required_info: List[str], context: Dict = None):
        self.request_type = request_type
        self.agent_name = agent_name
        self.required_info = required_info
        self.context = context or {}
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            'request_type': self.request_type,
            'agent_name': self.agent_name,
            'required_info': self.required_info,
            'context': self.context,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PendingRequest':
        """Create from dictionary."""
        pending_request = cls(
            request_type=data['request_type'],
            agent_name=data['agent_name'],
            required_info=data['required_info'],
            context=data.get('context', {})
        )
        pending_request.created_at = datetime.fromisoformat(data['created_at'])
        pending_request.last_updated = datetime.fromisoformat(data['last_updated'])
        return pending_request

class ConversationContextManager:
    """
    Manages conversation context, pending requests, and agent interaction state.
    Provides intelligent routing based on conversation history and context.
    """
    
    def __init__(self, user_id: str = None):
        """Initialize the conversation context manager."""
        self.user_id = user_id
        self.current_state = ConversationState.IDLE
        self.active_agent = None
        self.pending_requests: List[PendingRequest] = []
        self.conversation_topic = None
        self.last_user_intent = None
        self.agent_interaction_history: List[Dict] = []
        self.context_keywords: Set[str] = set()
        self.conversation_start_time = None
        self.last_activity = None
        
        # Initialize DynamoDB service if available and user_id provided
        self.dynamodb_service = None
        if DYNAMODB_AVAILABLE and user_id:
            self.dynamodb_service = DynamoDBService()
            self._load_user_context()
    
    def _load_user_context(self):
        """Load user-specific context from DynamoDB if available."""
        if not self.dynamodb_service or not self.user_id:
            return
        
        try:
            context_data = self.dynamodb_service.load_conversation_context(self.user_id)
            if context_data:
                self.current_state = ConversationState(context_data.get('current_state', 'idle'))
                self.active_agent = context_data.get('active_agent')
                self.conversation_topic = context_data.get('conversation_topic')
                self.last_user_intent = context_data.get('last_user_intent')
                self.context_keywords = set(context_data.get('context_keywords', []))
                self.conversation_start_time = datetime.fromisoformat(context_data.get('conversation_start_time')) if context_data.get('conversation_start_time') else None
                self.last_activity = datetime.fromisoformat(context_data.get('last_activity')) if context_data.get('last_activity') else None
                
                # Restore pending requests
                self.pending_requests = []
                for req_data in context_data.get('pending_requests', []):
                    self.pending_requests.append(PendingRequest.from_dict(req_data))
                
                # Restore agent interaction history
                self.agent_interaction_history = context_data.get('agent_interaction_history', [])
                
                print(f"Loaded conversation context for user {self.user_id}")
        except Exception as e:
            print(f"Error loading user context: {e}")
    
    def _save_user_context(self):
        """Save user-specific context to DynamoDB if available."""
        if not self.dynamodb_service or not self.user_id:
            return
        
        try:
            # Prepare context data for storage
            context_data = {
                'current_state': self.current_state.value,
                'active_agent': self.active_agent,
                'conversation_topic': self.conversation_topic,
                'last_user_intent': self.last_user_intent,
                'context_keywords': list(self.context_keywords),
                'conversation_start_time': self.conversation_start_time.isoformat() if self.conversation_start_time else None,
                'last_activity': self.last_activity.isoformat() if self.last_activity else None,
                'pending_requests': [req.to_dict() for req in self.pending_requests],
                'agent_interaction_history': self.agent_interaction_history
            }
            
            # Save to DynamoDB
            self.dynamodb_service.save_conversation_context(self.user_id, context_data)
            
        except Exception as e:
            print(f"Error saving user context: {e}")
    
    def set_user_id(self, user_id: str):
        """Set the user ID and initialize DynamoDB service if available."""
        self.user_id = user_id
        if DYNAMODB_AVAILABLE and user_id:
            self.dynamodb_service = DynamoDBService()
            self._load_user_context()
    
    def start_conversation(self) -> None:
        """Start a new conversation session."""
        self.current_state = ConversationState.IDLE
        self.active_agent = None
        self.pending_requests.clear()
        self.conversation_topic = None
        self.last_user_intent = None
        self.agent_interaction_history.clear()
        self.context_keywords.clear()
        self.conversation_start_time = datetime.now()
        self.last_activity = datetime.now()
        
        # Save to DynamoDB if available
        if self.dynamodb_service and self.user_id:
            self._save_user_context()
    
    def update_activity(self) -> None:
        """Update the last activity timestamp."""
        self.last_activity = datetime.now()
        
        # Save to DynamoDB if available
        if self.dynamodb_service and self.user_id:
            self._save_user_context()
    
    def set_conversation_topic(self, topic: str) -> None:
        """Set the current conversation topic."""
        self.conversation_topic = topic
        self.update_activity()
    
    def set_user_intent(self, intent: str) -> None:
        """Set the last user intent."""
        self.last_user_intent = intent
        self.update_activity()
    
    def add_pending_request(self, request_type: str, agent_name: str, 
                          required_info: List[str], context: Dict = None) -> None:
        """
        Add a pending request that needs additional information.
        
        Args:
            request_type: Type of request (e.g., "set_reminder", "add_todo")
            agent_name: Name of the agent handling the request
            required_info: List of required information items
            context: Additional context for the request
        """
        pending_request = PendingRequest(
            request_type=request_type,
            agent_name=agent_name,
            required_info=required_info,
            context=context
        )
        
        self.pending_requests.append(pending_request)
        self.current_state = ConversationState.WAITING_FOR_INPUT
        self.active_agent = agent_name
        self.update_activity()
    
    def get_pending_request(self, agent_name: str) -> Optional[PendingRequest]:
        """
        Get a pending request for a specific agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Pending request or None
        """
        for request in self.pending_requests:
            if request.agent_name == agent_name:
                return request
        return None
    
    def resolve_pending_request(self, agent_name: str) -> bool:
        """
        Resolve a pending request for a specific agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            True if resolved, False if not found
        """
        for i, request in enumerate(self.pending_requests):
            if request.agent_name == agent_name:
                del self.pending_requests[i]
                
                # Update state if no more pending requests
                if not self.pending_requests:
                    # Don't immediately clear the active agent - keep it for context continuity
                    self.current_state = ConversationState.AGENT_ACTIVE
                    # Keep the active_agent set for a few more turns
                
                self.update_activity()
                return True
        return False
    
    def add_agent_interaction(self, agent_name: str, action: str, result: str, metadata: Dict = None) -> None:
        """
        Record an agent interaction.
        
        Args:
            agent_name: Name of the agent
            action: Action performed
            result: Result of the action
            metadata: Additional metadata
        """
        interaction = {
            'agent_name': agent_name,
            'action': action,
            'result': result,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self.agent_interaction_history.append(interaction)
        
        # Keep only recent interactions (last 50)
        if len(self.agent_interaction_history) > 50:
            self.agent_interaction_history = self.agent_interaction_history[-50:]
        
        self.update_activity()
    
    def get_recent_interactions(self, count: int = 10) -> List[Dict]:
        """
        Get recent agent interactions.
        
        Args:
            count: Number of interactions to retrieve
            
        Returns:
            List of recent interactions
        """
        return self.agent_interaction_history[-count:] if self.agent_interaction_history else []
    
    def add_context_keywords(self, keywords: List[str]) -> None:
        """
        Add context keywords for routing.
        
        Args:
            keywords: List of keywords to add
        """
        self.context_keywords.update(keywords)
        self.update_activity()
    
    def has_context_keywords(self, message: str) -> bool:
        """
        Check if a message contains context keywords.
        
        Args:
            message: Message to check
            
        Returns:
            True if message contains context keywords
        """
        message_lower = message.lower()
        return any(keyword.lower() in message_lower for keyword in self.context_keywords)
    
    def get_conversation_context(self) -> Dict[str, Any]:
        """
        Get the current conversation context.
        
        Returns:
            Dictionary with conversation context
        """
        return {
            'current_state': self.current_state.value,
            'active_agent': self.active_agent,
            'conversation_topic': self.conversation_topic,
            'last_user_intent': self.last_user_intent,
            'context_keywords': list(self.context_keywords),
            'pending_requests_count': len(self.pending_requests),
            'recent_interactions': self.get_recent_interactions(5),
            'conversation_start_time': self.conversation_start_time.isoformat() if self.conversation_start_time else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None
        }
    
    def should_route_to_agent(self, message: str, available_agents: List[str]) -> Optional[str]:
        """
        Determine if a message should be routed to a specific agent.
        
        Args:
            message: User message
            available_agents: List of available agents
            
        Returns:
            Agent name to route to, or None
        """
        message_lower = message.lower()
        
        # Check if there's an active agent and pending request
        if self.active_agent and self.active_agent in available_agents:
            pending_request = self.get_pending_request(self.active_agent)
            if pending_request:
                return self.active_agent
        
        # Check for context keywords
        if self.has_context_keywords(message):
            # Find the most recent agent interaction
            recent_interactions = self.get_recent_interactions(3)
            for interaction in reversed(recent_interactions):
                if interaction["agent_name"] in available_agents:
                    return interaction["agent_name"]
        
        # Check if we have an active agent from recent interactions (context continuity)
        if self.active_agent and self.active_agent in available_agents:
            # If we have an active agent, stay with it for context continuity
            recent_interactions = self.get_recent_interactions(2)
            if recent_interactions and recent_interactions[-1]["agent_name"] == self.active_agent:
                return self.active_agent
        
        # Check for explicit agent mentions with more intelligent keyword matching
        # First, check for todo-specific keywords (higher priority to avoid false positives)
        todo_keywords = ["todo", "task", "project", "organize", "checklist", "to do", "to-do", "to do's", "todos"]
        if "todo_agent" in available_agents:
            if any(keyword in message_lower for keyword in todo_keywords):
                return "todo_agent"
        
        # Then check for reminder-specific keywords (more specific to avoid false positives)
        reminder_keywords = ["reminder", "remind", "alert", "schedule", "alarm", "wake up", "appointment"]
        if "reminder_agent" in available_agents:
            if any(keyword in message_lower for keyword in reminder_keywords):
                # Additional check: if the message also contains todo keywords, prioritize todo
                if not any(todo_keyword in message_lower for todo_keyword in todo_keywords):
                    return "reminder_agent"
        
        # Check for clarification patterns that indicate the user wants to correct the routing
        clarification_patterns = [
            r"i asked you to add.*to do",
            r"i want.*to do",
            r"i need.*to do",
            r"add.*to do",
            r"create.*to do",
            r"make.*to do"
        ]
        
        for pattern in clarification_patterns:
            if re.search(pattern, message_lower):
                if "todo_agent" in available_agents:
                    return "todo_agent"
        
        return None
    
    def clear_context(self) -> None:
        """Clear all conversation context."""
        self.current_state = ConversationState.IDLE
        self.active_agent = None
        self.pending_requests.clear()
        self.conversation_topic = None
        self.last_user_intent = None
        self.agent_interaction_history.clear()
        self.context_keywords.clear()
        self.conversation_start_time = None
        self.last_activity = None
        
        # Save to DynamoDB if available
        if self.dynamodb_service and self.user_id:
            self._save_user_context()
    
    def get_context_summary(self) -> str:
        """
        Get a summary of the current context.
        
        Returns:
            Context summary string
        """
        summary = f"Conversation State: {self.current_state.value}\n"
        
        if self.active_agent:
            summary += f"Active Agent: {self.active_agent}\n"
        
        if self.conversation_topic:
            summary += f"Topic: {self.conversation_topic}\n"
        
        if self.last_user_intent:
            summary += f"Last Intent: {self.last_user_intent}\n"
        
        if self.pending_requests:
            summary += f"Pending Requests: {len(self.pending_requests)}\n"
            for req in self.pending_requests:
                summary += f"  - {req.agent_name}: {req.request_type} (needs: {', '.join(req.required_info)})\n"
        
        if self.context_keywords:
            summary += f"Context Keywords: {', '.join(self.context_keywords)}\n"
        
        return summary
    
    def save_context(self, filepath: str) -> None:
        """
        Save context to a file (legacy method, now uses DynamoDB if available).
        
        Args:
            filepath: Filepath (not used with DynamoDB)
        """
        if self.dynamodb_service and self.user_id:
            self._save_user_context()
        else:
            print("No user ID set or DynamoDB not available, cannot save context")
    
    def load_context(self, filepath: str) -> bool:
        """
        Load context from a file (legacy method, now uses DynamoDB if available).
        
        Args:
            filepath: Filepath (not used with DynamoDB)
            
        Returns:
            True if successful, False otherwise
        """
        if self.dynamodb_service and self.user_id:
            self._load_user_context()
            return True
        else:
            return False
    
    def clear_active_agent_after_delay(self, turns: int = 3) -> None:
        """
        Clear the active agent after a certain number of turns.
        This should be called after a few messages to gradually clear context.
        
        Args:
            turns: Number of turns to wait before clearing (default: 3)
        """
        # For now, we'll implement a simple version
        # In a more sophisticated implementation, you'd track turn counts
        if self.current_state == ConversationState.AGENT_ACTIVE and not self.pending_requests:
            # If no pending requests and we've been in AGENT_ACTIVE state, 
            # gradually transition to IDLE
            self.current_state = ConversationState.IDLE
            self.active_agent = None
            self.update_activity()
    
    def set_active_agent(self, agent_name: str) -> None:
        """Set the currently active agent for context continuity."""
        self.active_agent = agent_name
        self.current_state = ConversationState.AGENT_ACTIVE
        self.update_activity() 