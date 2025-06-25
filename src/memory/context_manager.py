"""
Conversation Context Manager
Manages conversation context, pending requests, and agent interaction state.
Provides intelligent routing based on conversation history and context.
"""

from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from enum import Enum
import json
from ..utils.dynamodb_service import DynamoDBService

class ConversationState(Enum):
    """Enumeration of possible conversation states."""
    IDLE = "idle"
    WAITING_FOR_INPUT = "waiting_for_input"
    AGENT_ACTIVE = "agent_active"
    MULTI_AGENT = "multi_agent"
    ERROR = "error"

class PendingRequest:
    """Represents a pending request waiting for additional information."""
    
    def __init__(self, request_type: str, agent_name: str, required_info: List[str], 
                 context: Dict = None, created_at: datetime = None):
        self.request_type = request_type
        self.agent_name = agent_name
        self.required_info = required_info
        self.context = context or {}
        self.created_at = created_at or datetime.now()
        self.attempts = 0
        self.max_attempts = 3
    
    def is_expired(self, timeout_minutes: int = 10) -> bool:
        """Check if the pending request has expired."""
        timeout_delta = timedelta(minutes=timeout_minutes)
        return datetime.now() - self.created_at > timeout_delta
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "request_type": self.request_type,
            "agent_name": self.agent_name,
            "required_info": self.required_info,
            "context": self.context,
            "created_at": self.created_at.isoformat(),
            "attempts": self.attempts,
            "max_attempts": self.max_attempts
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PendingRequest':
        """Create from dictionary."""
        pending = cls(
            request_type=data["request_type"],
            agent_name=data["agent_name"],
            required_info=data["required_info"],
            context=data.get("context", {}),
            created_at=datetime.fromisoformat(data["created_at"])
        )
        pending.attempts = data.get("attempts", 0)
        pending.max_attempts = data.get("max_attempts", 3)
        return pending

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
        
        # Initialize DynamoDB service for user-specific storage
        self.dynamodb_service = DynamoDBService()
        
        # Load existing context if user_id is provided
        if self.user_id:
            self._load_user_context()
    
    def _load_user_context(self):
        """Load user-specific context from DynamoDB."""
        if not self.user_id:
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
        """Save user-specific context to DynamoDB."""
        if not self.user_id:
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
        """Set the user ID and load existing context."""
        self.user_id = user_id
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
        
        # Save to DynamoDB if user_id is set
        if self.user_id:
            self._save_user_context()
    
    def update_activity(self) -> None:
        """Update the last activity timestamp."""
        self.last_activity = datetime.now()
        
        # Save to DynamoDB if user_id is set
        if self.user_id:
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
    
    def get_pending_request(self, agent_name: str = None) -> Optional[PendingRequest]:
        """
        Get the most recent pending request.
        
        Args:
            agent_name: Optional agent name to filter by
            
        Returns:
            The most recent pending request or None
        """
        if not self.pending_requests:
            return None
        
        # Filter by agent if specified
        if agent_name:
            for request in reversed(self.pending_requests):
                if request.agent_name == agent_name and not request.is_expired():
                    return request
            return None
        
        # Return the most recent non-expired request
        for request in reversed(self.pending_requests):
            if not request.is_expired():
                return request
        
        return None
    
    def resolve_pending_request(self, agent_name: str = None) -> Optional[PendingRequest]:
        """
        Resolve and remove a pending request.
        
        Args:
            agent_name: Optional agent name to filter by
            
        Returns:
            The resolved request or None
        """
        request = self.get_pending_request(agent_name)
        if request:
            self.pending_requests.remove(request)
            
            # Update state if no more pending requests
            if not self.pending_requests:
                self.current_state = ConversationState.IDLE
                self.active_agent = None
            
            self.update_activity()
        
        return request
    
    def add_context_keywords(self, keywords: List[str]) -> None:
        """Add keywords that provide context for future messages."""
        self.context_keywords.update(keywords)
        self.update_activity()
    
    def clear_context_keywords(self) -> None:
        """Clear context keywords."""
        self.context_keywords.clear()
        self.update_activity()
    
    def has_context_keywords(self, message: str) -> bool:
        """Check if a message contains any context keywords."""
        message_lower = message.lower()
        return any(keyword.lower() in message_lower for keyword in self.context_keywords)
    
    def set_active_agent(self, agent_name: str) -> None:
        """Set the currently active agent."""
        self.active_agent = agent_name
        self.current_state = ConversationState.AGENT_ACTIVE
        self.update_activity()
    
    def add_agent_interaction(self, agent_name: str, action: str, 
                            result: str, metadata: Dict = None) -> None:
        """
        Add an agent interaction to the history.
        
        Args:
            agent_name: Name of the agent
            action: Action performed
            result: Result of the action
            metadata: Additional metadata
        """
        interaction = {
            "agent_name": agent_name,
            "action": action,
            "result": result,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.agent_interaction_history.append(interaction)
        
        # Keep only the last 50 interactions
        if len(self.agent_interaction_history) > 50:
            self.agent_interaction_history = self.agent_interaction_history[-50:]
        
        self.update_activity()
    
    def get_recent_interactions(self, count: int = 5) -> List[Dict]:
        """Get the most recent agent interactions."""
        return self.agent_interaction_history[-count:] if len(self.agent_interaction_history) > count else self.agent_interaction_history
    
    def should_route_to_agent(self, message: str, available_agents: List[str]) -> Optional[str]:
        """
        Determine if a message should be routed to a specific agent.
        
        Args:
            message: User message
            available_agents: List of available agents
            
        Returns:
            Agent name to route to, or None
        """
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
        
        # Check for explicit agent mentions
        message_lower = message.lower()
        agent_keywords = {
            "reminder_agent": ["reminder", "remind", "alert", "schedule", "alarm"],
            "todo_agent": ["todo", "task", "project", "organize", "checklist"]
        }
        
        for agent_name, keywords in agent_keywords.items():
            if agent_name in available_agents:
                if any(keyword in message_lower for keyword in keywords):
                    return agent_name
        
        return None
    
    def get_conversation_context(self) -> Dict[str, Any]:
        """
        Get the current conversation context.
        
        Returns:
            Dictionary with conversation context
        """
        context = {
            "current_state": self.current_state.value,
            "active_agent": self.active_agent,
            "conversation_topic": self.conversation_topic,
            "last_user_intent": self.last_user_intent,
            "context_keywords": list(self.context_keywords),
            "conversation_start_time": self.conversation_start_time.isoformat() if self.conversation_start_time else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "pending_requests_count": len(self.pending_requests),
            "recent_interactions": self.get_recent_interactions(5),
            "user_id": self.user_id
        }
        
        return context
    
    def is_conversation_active(self, timeout_minutes: int = 30) -> bool:
        """
        Check if the conversation is still active.
        
        Args:
            timeout_minutes: Minutes of inactivity before considering conversation inactive
            
        Returns:
            True if conversation is active, False otherwise
        """
        if not self.last_activity:
            return False
        
        timeout_delta = timedelta(minutes=timeout_minutes)
        return datetime.now() - self.last_activity < timeout_delta
    
    def cleanup_expired_requests(self) -> int:
        """
        Clean up expired pending requests.
        
        Returns:
            Number of requests cleaned up
        """
        initial_count = len(self.pending_requests)
        self.pending_requests = [req for req in self.pending_requests if not req.is_expired()]
        cleaned_count = initial_count - len(self.pending_requests)
        
        if cleaned_count > 0:
            self.update_activity()
        
        return cleaned_count
    
    def save_context(self, filepath: str) -> None:
        """
        Save context to a file (legacy method, now uses DynamoDB).
        
        Args:
            filepath: Filepath (not used with DynamoDB)
        """
        if self.user_id:
            self._save_user_context()
        else:
            print("No user ID set, cannot save to DynamoDB")
    
    def load_context(self, filepath: str) -> bool:
        """
        Load context from a file (legacy method, now uses DynamoDB).
        
        Args:
            filepath: Filepath (not used with DynamoDB)
            
        Returns:
            True if successful, False otherwise
        """
        if self.user_id:
            self._load_user_context()
            return True
        else:
            return False 