"""
Memory Utilities
Utility functions for memory management, keyword detection, and conversation analysis.
Provides helper functions for the memory system.
"""

from typing import List, Dict, Set, Tuple, Optional
import re
from datetime import datetime

class MemoryUtils:
    """Utility class for memory management and conversation analysis."""
    
    # Time-related keywords that might complete a reminder request
    TIME_KEYWORDS = {
        "morning": ["6am", "7am", "8am", "9am", "10am", "11am", "morning", "early"],
        "afternoon": ["12pm", "1pm", "2pm", "3pm", "4pm", "5pm", "afternoon", "noon"],
        "evening": ["6pm", "7pm", "8pm", "9pm", "10pm", "evening", "night"],
        "specific_times": ["am", "pm", "o'clock", "oclock", "sharp", "exactly"]
    }
    
    # Task-related keywords that might complete a todo request
    TASK_KEYWORDS = {
        "work": ["work", "project", "meeting", "presentation", "report", "email", "call"],
        "personal": ["personal", "family", "home", "house", "grocery", "shopping"],
        "health": ["exercise", "workout", "gym", "doctor", "appointment", "health"],
        "general": ["task", "item", "thing", "todo", "to do", "to-do", "checklist"]
    }
    
    # Reminder-related keywords
    REMINDER_KEYWORDS = {
        "set": ["set", "create", "add", "make", "schedule"],
        "reminder": ["reminder", "remind", "alert", "alarm", "notification"],
        "time": ["time", "when", "schedule", "appointment", "meeting"],
        "description": ["for", "about", "regarding", "concerning", "related to"]
    }
    
    # Todo-related keywords
    TODO_KEYWORDS = {
        "add": ["add", "create", "make", "new", "set up"],
        "todo": ["todo", "task", "item", "thing", "work", "project"],
        "priority": ["urgent", "important", "high", "medium", "low", "priority"],
        "category": ["work", "personal", "shopping", "health", "family", "home"]
    }
    
    @classmethod
    def extract_time_from_message(cls, message: str) -> Optional[str]:
        """
        Extract time information from a message.
        
        Args:
            message: The user message
            
        Returns:
            Extracted time string or None
        """
        message_lower = message.lower().strip()
        
        # Check for specific time patterns
        time_patterns = [
            r'(\d{1,2}:\d{2}\s*(?:am|pm)?)',  # 6:30, 6:30am, 6:30 pm
            r'(\d{1,2}\s*(?:am|pm))',  # 6am, 6 pm, 6 AM
            r'(\d{1,2}\s*o\'?clock)',  # 6 o'clock, 6oclock
            r'(morning|afternoon|evening|night)',  # time periods
            r'(today|tomorrow)',  # relative dates
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, message_lower)
            if match:
                return match.group(1)
        
        return None
    
    @classmethod
    def extract_task_from_message(cls, message: str) -> Optional[str]:
        """
        Extract task information from a message.
        
        Args:
            message: The user message
            
        Returns:
            Extracted task string or None
        """
        message_lower = message.lower().strip()
        
        # Remove common filler words
        filler_words = ["add", "create", "make", "new", "todo", "task", "item", "thing"]
        for word in filler_words:
            message_lower = message_lower.replace(word, "").strip()
        
        # If message is too short after cleaning, return None
        if len(message_lower) < 2:
            return None
        
        return message_lower
    
    @classmethod
    def detect_reminder_intent(cls, message: str) -> Tuple[bool, Dict]:
        """
        Detect if a message has reminder-related intent.
        
        Args:
            message: The user message
            
        Returns:
            Tuple of (is_reminder_intent, intent_details)
        """
        message_lower = message.lower()
        
        # Check for reminder-related keywords
        has_reminder_keywords = any(
            keyword in message_lower 
            for keywords in cls.REMINDER_KEYWORDS.values() 
            for keyword in keywords
        )
        
        if not has_reminder_keywords:
            return False, {}
        
        # Extract details
        intent_details = {
            "action": "set_reminder",
            "has_time": cls.extract_time_from_message(message) is not None,
            "has_description": any(word in message_lower for word in ["for", "about", "regarding"]),
            "time": cls.extract_time_from_message(message),
            "confidence": 0.8
        }
        
        return True, intent_details
    
    @classmethod
    def detect_todo_intent(cls, message: str) -> Tuple[bool, Dict]:
        """
        Detect if a message has todo-related intent.
        
        Args:
            message: The user message
            
        Returns:
            Tuple of (is_todo_intent, intent_details)
        """
        message_lower = message.lower()
        
        # Check for todo-related keywords
        has_todo_keywords = any(
            keyword in message_lower 
            for keywords in cls.TODO_KEYWORDS.values() 
            for keyword in keywords
        )
        
        if not has_todo_keywords:
            return False, {}
        
        # Extract details
        intent_details = {
            "action": "add_todo",
            "has_task": cls.extract_task_from_message(message) is not None,
            "has_priority": any(word in message_lower for word in ["urgent", "important", "high", "medium", "low"]),
            "has_category": any(word in message_lower for word in ["work", "personal", "shopping", "health"]),
            "task": cls.extract_task_from_message(message),
            "confidence": 0.8
        }
        
        return True, intent_details
    
    @classmethod
    def is_context_response(cls, message: str, context_keywords: Set[str]) -> bool:
        """
        Check if a message is a response to a previous context.
        
        Args:
            message: The user message
            context_keywords: Set of context keywords from previous conversation
            
        Returns:
            True if message appears to be a context response
        """
        if not context_keywords:
            return False
        
        message_lower = message.lower()
        
        # Check if message contains any context keywords
        has_context_keywords = any(keyword.lower() in message_lower for keyword in context_keywords)
        
        # Check if message is short (likely a response)
        is_short_response = len(message.strip()) < 50
        
        # Check if message contains time or task information
        has_time_info = cls.extract_time_from_message(message) is not None
        has_task_info = cls.extract_task_from_message(message) is not None
        
        return has_context_keywords and (is_short_response or has_time_info or has_task_info)
    
    @classmethod
    def get_context_keywords_for_intent(cls, intent_type: str, details: Dict) -> List[str]:
        """
        Generate context keywords for a specific intent.
        
        Args:
            intent_type: Type of intent ("reminder" or "todo")
            details: Intent details
            
        Returns:
            List of context keywords
        """
        keywords = []
        
        if intent_type == "reminder":
            if details.get("has_time"):
                keywords.extend(["time", "when", "schedule"])
            if details.get("has_description"):
                keywords.extend(["for", "about", "description"])
            keywords.extend(["reminder", "alarm", "alert"])
        
        elif intent_type == "todo":
            if details.get("has_task"):
                keywords.extend(["task", "item", "thing"])
            if details.get("has_priority"):
                keywords.extend(["priority", "urgent", "important"])
            if details.get("has_category"):
                keywords.extend(["work", "personal", "shopping", "health"])
            keywords.extend(["todo", "task", "project"])
        
        return keywords
    
    @classmethod
    def analyze_conversation_flow(cls, messages: List[Dict]) -> Dict:
        """
        Analyze the flow of a conversation.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            
        Returns:
            Analysis of the conversation flow
        """
        if not messages:
            return {"flow_type": "empty", "confidence": 0.0}
        
        analysis = {
            "flow_type": "general",
            "confidence": 0.5,
            "intents_detected": [],
            "context_changes": 0,
            "agent_interactions": 0
        }
        
        for i, message in enumerate(messages):
            if message.get("role") == "user":
                content = message.get("content", "")
                
                # Detect intents
                is_reminder, reminder_details = cls.detect_reminder_intent(content)
                is_todo, todo_details = cls.detect_todo_intent(content)
                
                if is_reminder:
                    analysis["intents_detected"].append({
                        "type": "reminder",
                        "details": reminder_details,
                        "position": i
                    })
                    analysis["flow_type"] = "reminder_setup"
                    analysis["confidence"] = 0.8
                
                elif is_todo:
                    analysis["intents_detected"].append({
                        "type": "todo",
                        "details": todo_details,
                        "position": i
                    })
                    analysis["flow_type"] = "todo_setup"
                    analysis["confidence"] = 0.8
        
        # Count context changes
        analysis["context_changes"] = len(analysis["intents_detected"])
        
        return analysis
    
    @classmethod
    def should_continue_conversation(cls, message: str, context: Dict) -> bool:
        """
        Determine if a conversation should continue based on context.
        
        Args:
            message: The user message
            context: Current conversation context
            
        Returns:
            True if conversation should continue
        """
        # Check if there are pending requests
        if context.get("pending_requests_count", 0) > 0:
            return True
        
        # Check if message is a short response (likely continuing conversation)
        if len(message.strip()) < 30:
            return True
        
        # Check if message contains time or task information
        has_time = cls.extract_time_from_message(message) is not None
        has_task = cls.extract_task_from_message(message) is not None
        
        if has_time or has_task:
            return True
        
        return False
    
    @classmethod
    def get_conversation_summary(cls, messages: List[Dict]) -> str:
        """
        Generate a summary of the conversation.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Conversation summary
        """
        if not messages:
            return "No conversation history available."
        
        summary_parts = []
        
        # Count messages by role
        user_messages = [msg for msg in messages if msg.get("role") == "user"]
        assistant_messages = [msg for msg in messages if msg.get("role") == "assistant"]
        
        summary_parts.append(f"Conversation with {len(user_messages)} user messages and {len(assistant_messages)} assistant responses.")
        
        # Analyze intents
        intents = []
        for msg in user_messages:
            content = msg.get("content", "")
            is_reminder, _ = cls.detect_reminder_intent(content)
            is_todo, _ = cls.detect_todo_intent(content)
            
            if is_reminder:
                intents.append("reminder")
            elif is_todo:
                intents.append("todo")
        
        if intents:
            intent_counts = {}
            for intent in intents:
                intent_counts[intent] = intent_counts.get(intent, 0) + 1
            
            intent_summary = ", ".join([f"{count} {intent} requests" for intent, count in intent_counts.items()])
            summary_parts.append(f"Detected intents: {intent_summary}.")
        
        # Add recent context
        if messages:
            recent_messages = messages[-3:] if len(messages) >= 3 else messages
            recent_context = "Recent context: "
            for msg in recent_messages:
                role = msg.get("role", "unknown").title()
                content = msg.get("content", "")[:50]
                recent_context += f"{role}: {content}... "
            summary_parts.append(recent_context)
        
        return " ".join(summary_parts) 