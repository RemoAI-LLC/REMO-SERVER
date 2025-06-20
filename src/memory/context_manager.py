"""
Conversation Context Manager
Manages conversation context, pending requests, and agent interaction state.
Provides intelligent routing based on conversation history and context.
"""

from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from enum import Enum
import json

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
    
    def __init__(self):
        """Initialize the conversation context manager."""
        self.current_state = ConversationState.IDLE
        self.active_agent = None
        self.pending_requests: List[PendingRequest] = []
        self.conversation_topic = None
        self.last_user_intent = None
        self.agent_interaction_history: List[Dict] = []
        self.context_keywords: Set[str] = set()
        self.conversation_start_time = None
        self.last_activity = None
    
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
    
    def update_activity(self) -> None:
        """Update the last activity timestamp."""
        self.last_activity = datetime.now()
    
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
        Record an agent interaction.
        
        Args:
            agent_name: Name of the agent
            action: Action performed
            result: Result of the action
            metadata: Additional metadata
        """
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name,
            "action": action,
            "result": result,
            "metadata": metadata or {}
        }
        
        self.agent_interaction_history.append(interaction)
        self.update_activity()
    
    def get_recent_interactions(self, count: int = 5) -> List[Dict]:
        """Get recent agent interactions."""
        return self.agent_interaction_history[-count:] if self.agent_interaction_history else []
    
    def should_route_to_agent(self, message: str, available_agents: List[str]) -> Optional[str]:
        """
        Determine if a message should be routed to a specific agent.
        
        Args:
            message: The user message
            available_agents: List of available agent names
            
        Returns:
            Agent name to route to, or None for basic Remo
        """
        # Check if there's a pending request that this message might complete
        pending_request = self.get_pending_request()
        if pending_request:
            # Check if the message provides the required information
            message_lower = message.lower()
            
            # Simple heuristic: if message contains time-related words, it might be completing a reminder
            time_keywords = ["am", "pm", "morning", "afternoon", "evening", "night", "today", "tomorrow"]
            if any(keyword in message_lower for keyword in time_keywords):
                if "reminder" in pending_request.request_type.lower():
                    return pending_request.agent_name
            
            # Check if message contains task-related words for todo requests
            task_keywords = ["task", "todo", "item", "thing", "work", "project"]
            if any(keyword in message_lower for keyword in task_keywords):
                if "todo" in pending_request.request_type.lower():
                    return pending_request.agent_name
        
        # Check if message contains context keywords
        if self.has_context_keywords(message):
            if self.active_agent:
                return self.active_agent
        
        # Check conversation topic
        if self.conversation_topic:
            topic_lower = self.conversation_topic.lower()
            if "reminder" in topic_lower and "reminder_agent" in available_agents:
                return "reminder_agent"
            elif "todo" in topic_lower and "todo_agent" in available_agents:
                return "todo_agent"
        
        return None
    
    def get_conversation_context(self) -> Dict[str, Any]:
        """Get the current conversation context."""
        return {
            "state": self.current_state.value,
            "active_agent": self.active_agent,
            "conversation_topic": self.conversation_topic,
            "last_user_intent": self.last_user_intent,
            "pending_requests_count": len(self.pending_requests),
            "context_keywords": list(self.context_keywords),
            "conversation_start": self.conversation_start_time.isoformat() if self.conversation_start_time else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "recent_interactions": self.get_recent_interactions(3)
        }
    
    def is_conversation_active(self, timeout_minutes: int = 30) -> bool:
        """Check if the conversation is still active."""
        if self.last_activity is None:
            return False
        
        timeout_delta = timedelta(minutes=timeout_minutes)
        return datetime.now() - self.last_activity < timeout_delta
    
    def cleanup_expired_requests(self) -> int:
        """
        Remove expired pending requests.
        
        Returns:
            Number of requests removed
        """
        initial_count = len(self.pending_requests)
        self.pending_requests = [req for req in self.pending_requests if not req.is_expired()]
        removed_count = initial_count - len(self.pending_requests)
        
        # Update state if no more pending requests
        if not self.pending_requests and self.current_state == ConversationState.WAITING_FOR_INPUT:
            self.current_state = ConversationState.IDLE
            self.active_agent = None
        
        return removed_count
    
    def save_context(self, filepath: str) -> None:
        """Save conversation context to a file."""
        context_data = {
            "current_state": self.current_state.value,
            "active_agent": self.active_agent,
            "conversation_topic": self.conversation_topic,
            "last_user_intent": self.last_user_intent,
            "pending_requests": [req.to_dict() for req in self.pending_requests],
            "agent_interaction_history": self.agent_interaction_history,
            "context_keywords": list(self.context_keywords),
            "conversation_start": self.conversation_start_time.isoformat() if self.conversation_start_time else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None
        }
        
        with open(filepath, 'w') as f:
            json.dump(context_data, f, indent=2)
    
    def load_context(self, filepath: str) -> bool:
        """Load conversation context from a file."""
        try:
            with open(filepath, 'r') as f:
                context_data = json.load(f)
            
            self.current_state = ConversationState(context_data["current_state"])
            self.active_agent = context_data.get("active_agent")
            self.conversation_topic = context_data.get("conversation_topic")
            self.last_user_intent = context_data.get("last_user_intent")
            
            # Load pending requests
            self.pending_requests = []
            for req_data in context_data.get("pending_requests", []):
                self.pending_requests.append(PendingRequest.from_dict(req_data))
            
            self.agent_interaction_history = context_data.get("agent_interaction_history", [])
            self.context_keywords = set(context_data.get("context_keywords", []))
            
            if context_data.get("conversation_start"):
                self.conversation_start_time = datetime.fromisoformat(context_data["conversation_start"])
            if context_data.get("last_activity"):
                self.last_activity = datetime.fromisoformat(context_data["last_activity"])
            
            return True
        except Exception as e:
            print(f"Failed to load context: {e}")
            return False 