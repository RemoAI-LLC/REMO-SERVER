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
        
        # Enhanced time patterns
        time_patterns = [
            # Specific times with AM/PM
            r'(\d{1,2}:\d{2}\s*(?:am|pm))',  # 6:30am, 6:30 pm
            r'(\d{1,2}\s*(?:am|pm))',  # 6am, 6 pm, 6 AM
            # Times without AM/PM (assume based on context)
            r'(\d{1,2}:\d{2})',  # 6:30
            # O'clock format
            r'(\d{1,2}\s*o\'?clock)',  # 6 o'clock, 6oclock
            # Time periods
            r'(morning|afternoon|evening|night)',
            # Relative dates with times
            r'(tomorrow|today)\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)',
            r'(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\s+(tomorrow|today)',
            # Natural language time expressions
            r'(in the morning|in the afternoon|in the evening|at night)',
            r'(early morning|late morning|early afternoon|late afternoon|early evening|late evening)'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, message_lower)
            if match:
                time_str = match.group(1)
                
                # Handle relative dates with times
                if 'tomorrow' in time_str or 'today' in time_str:
                    # Extract just the time part
                    time_match = re.search(r'(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)', time_str)
                    if time_match:
                        time_str = time_match.group(1)
                
                # Clean up the time string
                time_str = time_str.strip()
                
                # Add AM/PM if missing and it's a reasonable hour
                if re.match(r'^\d{1,2}(?::\d{2})?$', time_str):
                    hour = int(time_str.split(':')[0])
                    if hour < 12:
                        time_str += ' am'
                    else:
                        time_str += ' pm'
                
                return time_str
        
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
        
        # Remove common filler words and phrases
        filler_words = [
            "add", "create", "make", "new", "todo", "task", "item", "thing",
            "to my", "to the", "to do", "to-do", "to do's", "todos", "list",
            "can you", "could you", "please", "i need", "i want", "i'd like"
        ]
        
        # Clean the message
        cleaned_message = message_lower
        for word in filler_words:
            cleaned_message = cleaned_message.replace(word, "").strip()
        
        # Remove extra whitespace and punctuation
        cleaned_message = re.sub(r'\s+', ' ', cleaned_message).strip()
        cleaned_message = re.sub(r'^\s*[,.]\s*', '', cleaned_message)
        cleaned_message = re.sub(r'\s*[,.]\s*$', '', cleaned_message)
        
        # If message is too short after cleaning, return None
        if len(cleaned_message) < 2:
            return None
        
        # Try to extract the task more intelligently
        # Look for patterns like "add [task] to my to do's"
        task_patterns = [
            r'(?:add|create|make)\s+(.*?)\s+(?:to my|to the)\s+(?:todo|task|list|to do|to-do|to do\'s|todos)',
            r'(?:add|create|make)\s+(.*?)\s+(?:todo|task|list|to do|to-do|to do\'s|todos)',
            r'(?:add|create|make)\s+(.*?)$',
            r'(?:todo|task|item)\s+(?:to|for|about)\s+(.*?)$'
        ]
        
        for pattern in task_patterns:
            match = re.search(pattern, message_lower)
            if match:
                task = match.group(1).strip()
                # Clean up the extracted task
                task = re.sub(r'\s+', ' ', task).strip()
                task = re.sub(r'^\s*[,.]\s*', '', task)
                task = re.sub(r'\s*[,.]\s*$', '', task)
                if len(task) >= 2:
                    return task
        
        # If no pattern match, return the cleaned message
        return cleaned_message if len(cleaned_message) >= 2 else None
    
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
        
        # Explicit patterns for listing reminders
        list_patterns = [
            r"show (me )?all (my )?(reminders|alerts|alarms|reminder list)",
            r"list (all )?(my )?(reminders|alerts|alarms|reminder list)",
            r"display (all )?(my )?(reminders|alerts|alarms|reminder list)",
            r"what (are|is) (my )?(reminders|alerts|alarms|reminder list)",
            r"see (all )?(my )?(reminders|alerts|alarms|reminder list)"
        ]
        if any(re.search(pattern, message_lower) for pattern in list_patterns):
            return True, {"action": "list_reminders", "confidence": 1.0}
        
        # First check if it's explicitly a todo request (to avoid false positives)
        todo_keywords = ["todo", "task", "item", "thing", "project", "work", "priority", "to do", "to-do", "to do's", "todos"]
        if any(keyword in message_lower for keyword in todo_keywords):
            # If it contains todo keywords, it's likely a todo, not a reminder
            return False, {}
        
        # Enhanced reminder detection patterns (more specific and precise)
        reminder_patterns = [
            # Direct reminder requests with explicit reminder keywords
            r'\b(set|create|add|make|schedule)\s+(?:a\s+)?(?:reminder|remind|alert|alarm|notification)\b',
            r'\b(reminder|remind|alert|alarm|notification)\s+(?:for|to|about)\b',
            r'\b(?:can you|could you|please)\s+(?:set|create|add|make)\s+(?:a\s+)?(?:reminder|remind|alert|alarm|notification)\b',
            r'\b(?:i need|i want|i\'d like)\s+(?:a\s+)?(?:reminder|remind|alert|alarm|notification)\b',
            # Specific reminder phrases
            r'\b(?:don\'t forget|remember|remind me)\s+(?:to|about|that)\b',
            r'\b(?:set|create|add)\s+(?:a\s+)?(?:reminder|remind|alert|alarm|notification)\s+(?:for|about|to)\b',
            # Time-based patterns with explicit reminder context
            r'\b(?:remind me|set reminder|create reminder)\s+(?:for|about|to)\b',
            # Wake up and appointment patterns
            r'\b(?:wake up|wake me|get up)\s+(?:at|by)\b',
            r'\b(?:appointment|meeting)\s+(?:at|on|for)\b',
            # Schedule patterns
            r'\b(?:schedule|book)\s+(?:an\s+)?(?:appointment|meeting|call)\b'
        ]
        
        # Check for reminder patterns
        has_reminder_pattern = any(re.search(pattern, message_lower) for pattern in reminder_patterns)
        
        # Check for explicit reminder keywords (more specific)
        reminder_keywords = ["reminder", "remind", "alert", "alarm", "don't forget", "remember", "notification", "wake up", "appointment", "schedule"]
        has_reminder_keywords = any(keyword in message_lower for keyword in reminder_keywords)
        
        # Check for time information
        has_time_info = cls.extract_time_from_message(message) is not None
        
        # Only detect as reminder if we have explicit reminder keywords or patterns
        # AND it's not a todo request
        if (has_reminder_pattern or has_reminder_keywords) and not any(todo_keyword in message_lower for todo_keyword in todo_keywords):
            intent_details = {
                "action": "set_reminder",
                "has_time": has_time_info,
                "has_description": any(word in message_lower for word in ["for", "about", "regarding", "to"]),
                "time": cls.extract_time_from_message(message),
                "description": cls.extract_reminder_description(message),
                "confidence": 0.9 if has_reminder_pattern else 0.8
            }
            return True, intent_details
        
        return False, {}
    
    @classmethod
    def extract_reminder_description(cls, message: str) -> Optional[str]:
        """
        Extract reminder description from a message.
        
        Args:
            message: The user message
            
        Returns:
            Extracted description or None
        """
        message_lower = message.lower()
        
        # Look for description after "for", "about", "to", etc.
        description_patterns = [
            r'\b(?:for|about|to|regarding)\s+(.+?)(?:\s+(?:tomorrow|today|at|on|in|\d{1,2}(?::\d{2})?\s*(?:am|pm)?))',
            r'\b(?:remind me to|don\'t forget to|remember to)\s+(.+?)(?:\s+(?:tomorrow|today|at|on|in|\d{1,2}(?::\d{2})?\s*(?:am|pm)?))',
            r'\b(?:add|set|create|make)\s+(?:a\s+)?(?:reminder|remind|alert|alarm)\s+(?:for|about|to)\s+(.+?)(?:\s+(?:tomorrow|today|at|on|in|\d{1,2}(?::\d{2})?\s*(?:am|pm)?))',
        ]
        
        for pattern in description_patterns:
            match = re.search(pattern, message_lower)
            if match:
                description = match.group(1).strip()
                # Clean up the description
                description = re.sub(r'\b(?:add|set|create|make|reminder|remind|alert|alarm)\b', '', description).strip()
                # Remove trailing "for" if it's at the end
                description = re.sub(r'\s+for\s*$', '', description).strip()
                if description and len(description) > 2:
                    return description
        
        return None
    
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
        
        # Explicit patterns for listing todos
        list_patterns = [
            r"show (me )?all (my )?(todos|to do's|tasks|todo list)",
            r"list (all )?(my )?(todos|to do's|tasks|todo list)",
            r"display (all )?(my )?(todos|to do's|tasks|todo list)",
            r"what (are|is) (my )?(todos|to do's|tasks|todo list)",
            r"see (all )?(my )?(todos|to do's|tasks|todo list)"
        ]
        if any(re.search(pattern, message_lower) for pattern in list_patterns):
            return True, {"action": "list_todos", "confidence": 1.0}
        
        # Enhanced todo detection patterns - more comprehensive
        todo_patterns = [
            # Direct todo requests
            r'\b(add|create|make|new)\s+(?:a\s+)?(?:todo|task|item)\b',
            r'\b(todo|task|item)\s+(?:to|for|about)\b',
            r'\b(?:can you|could you|please)\s+(?:add|create|make)\s+(?:a\s+)?(?:todo|task|item)\b',
            r'\b(?:i need|i want|i\'d like)\s+(?:a\s+)?(?:todo|task|item)\b',
            # Specific todo phrases - more flexible
            r'\b(?:add|create|make)\s+(?:.*?)\s+(?:to my|to the)\s+(?:todo|task|list)\b',
            r'\b(?:add|create|make)\s+(?:.*?)\s+(?:to do|todo|to-do)\b',
            r'\b(?:add|create|make)\s+(?:.*?)\s+(?:to my|to the)\s+(?:to do|todo|to-do)\b',
            # "to do's" pattern specifically
            r'\b(?:add|create|make)\s+(?:.*?)\s+(?:to my|to the)\s+(?:to do\'s|todos)\b',
            r'\b(?:add|create|make)\s+(?:.*?)\s+(?:to do\'s|todos)\b',
            # Priority-based patterns
            r'\b(?:high|medium|low|urgent|important)\s+(?:priority)\s+(?:todo|task|item)\b',
            r'\b(?:todo|task|item)\s+(?:.*?)\s+(?:high|medium|low|urgent|important)\s+(?:priority)\b',
            # General task patterns
            r'\b(?:add|create|make)\s+(?:.*?)\s+(?:task|item|thing)\b',
            r'\b(?:add|create|make)\s+(?:task|item|thing)\s+(?:.*?)\b'
        ]
        
        # Check for todo patterns
        has_todo_pattern = any(re.search(pattern, message_lower) for pattern in todo_patterns)
        
        # Check for todo-related keywords (more comprehensive)
        todo_keywords = [
            "todo", "task", "item", "thing", "project", "work", "priority",
            "to do", "to-do", "checklist", "list", "add to", "create task",
            "add task", "mark complete", "finish", "done", "complete task"
        ]
        has_todo_keywords = any(keyword in message_lower for keyword in todo_keywords)
        
        # Check for priority keywords (strong indicator of todo intent)
        has_priority_keywords = any(word in message_lower for word in ["urgent", "important", "high", "medium", "low", "priority"])
        
        # Check for time information (common in todos)
        has_time_info = cls.extract_time_from_message(message) is not None
        
        # Check for action verbs that indicate todo intent
        action_verbs = ["add", "create", "make", "new", "set up", "organize", "prioritize"]
        has_action_verbs = any(verb in message_lower for verb in action_verbs)
        
        # If we have todo patterns, strong todo indicators, or action verbs with task context
        if (has_todo_pattern or 
            (has_todo_keywords and (has_priority_keywords or has_time_info or has_action_verbs)) or
            (has_action_verbs and any(word in message_lower for word in ["task", "item", "thing", "project", "work"]))):
            
            intent_details = {
                "action": "add_todo",
                "has_task": cls.extract_task_from_message(message) is not None,
                "has_priority": has_priority_keywords,
                "has_category": any(word in message_lower for word in ["work", "personal", "shopping", "health"]),
                "has_time": has_time_info,
                "task": cls.extract_task_from_message(message),
                "priority": cls.extract_priority_from_message(message),
                "time": cls.extract_time_from_message(message),
                "confidence": 0.9 if has_todo_pattern else 0.8
            }
            return True, intent_details
        
        return False, {}
    
    @classmethod
    def extract_priority_from_message(cls, message: str) -> Optional[str]:
        """
        Extract priority information from a message.
        
        Args:
            message: The user message
            
        Returns:
            Extracted priority string or None
        """
        message_lower = message.lower()
        
        priority_patterns = [
            r'\b(high|medium|low|urgent|important)\s+(?:priority)\b',
            r'\b(?:priority)\s+(?:is\s+)?(high|medium|low|urgent|important)\b',
            r'\b(high|medium|low|urgent|important)\s+(?:priority)\s+(?:todo|task|item)\b'
        ]
        
        for pattern in priority_patterns:
            match = re.search(pattern, message_lower)
            if match:
                return match.group(1).lower()
        
        return None
    
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