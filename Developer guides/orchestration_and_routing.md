# 🤖 Agent Orchestration & Routing

Remo uses a sophisticated multi-layered orchestration system that combines intent detection, context management, and intelligent routing to provide seamless user experiences. This guide explains how routing works and how to extend it.

## 🏗️ Architecture Overview

The orchestration system consists of three main components:

1. **Intent Detection Layer** (`src/memory/memory_utils.py`)
2. **Context Management Layer** (`src/memory/context_manager.py`)
3. **Routing Decision Layer** (`app.py`)

## 🎯 Intent Detection System

### Enhanced Intent Detection

The system uses advanced pattern matching and keyword analysis to accurately detect user intents:

```python
# Todo Intent Detection
todo_patterns = [
    r'\b(add|create|make|new)\s+(?:a\s+)?(?:todo|task|item)\b',
    r'\b(?:add|create|make)\s+(?:.*?)\s+(?:to my|to the)\s+(?:to do|todo|to-do)\b',
    r'\b(?:add|create|make)\s+(?:.*?)\s+(?:to do\'s|todos)\b',
    # ... more patterns
]

# Reminder Intent Detection
reminder_patterns = [
    r'\b(set|create|add|make|schedule)\s+(?:a\s+)?(?:reminder|remind|alert|alarm|notification)\b',
    r'\b(?:don\'t forget|remember|remind me)\s+(?:to|about|that)\b',
    # ... more patterns
]
```

### Key Improvements

- **Natural Language Support**: Handles variations like "to do's", "todos", "todo list"
- **Clarification Detection**: Recognizes when users are correcting routing mistakes
- **False Positive Prevention**: Prioritizes todo keywords over reminder keywords
- **Task Extraction**: Intelligently extracts tasks from natural language

### Example Usage

```python
from src.memory.memory_utils import MemoryUtils

# Detect intents
is_todo, todo_details = MemoryUtils.detect_todo_intent("add groceries to my to do's")
is_reminder, reminder_details = MemoryUtils.detect_reminder_intent("remind me to call mom")

# Extract tasks
task = MemoryUtils.extract_task_from_message("add going to groceries to my to do's")
# Returns: "going to groceries"
```

## 🧠 Context Management

### Conversation Context Manager

The `ConversationContextManager` maintains conversation state and provides intelligent routing:

```python
class ConversationContextManager:
    def __init__(self, user_id: str = None):
        self.current_state = ConversationState.IDLE
        self.active_agent = None
        self.pending_requests = []
        self.conversation_topic = None
        self.context_keywords = set()
```

### Context-Aware Routing

The system uses multiple strategies for routing decisions:

1. **Active Agent Continuity**: Maintains context with the current agent
2. **Pending Request Resolution**: Routes to agents with incomplete requests
3. **Keyword-Based Routing**: Uses specific keywords for agent selection
4. **Clarification Pattern Detection**: Recognizes when users are correcting intent

### Routing Logic

```python
def should_route_to_agent(self, message: str, available_agents: List[str]) -> Optional[str]:
    # Priority order:
    # 1. Active agent with pending request
    # 2. Context keywords from recent interactions
    # 3. Active agent for context continuity
    # 4. Explicit agent mentions with intelligent keyword matching
    # 5. Clarification patterns
```

## 🚦 Routing Decision Layer

### Priority-Based Routing

The main routing logic in `app.py` uses a clear priority order:

```python
# Priority order: Intent Detection > Context Routing > General Response
if is_todo_intent:
    target_agent = "todo_agent"
    # Set todo context and keywords
elif is_reminder_intent:
    target_agent = "reminder_agent"
    # Set reminder context and keywords
elif context_agent:
    # Only use context routing if no clear intent is detected
    target_agent = context_agent
```

### Agent-Specific Keywords

```python
# Todo Agent Keywords (Higher Priority)
todo_keywords = [
    "todo", "task", "project", "organize", "checklist", 
    "to do", "to-do", "to do's", "todos"
]

# Reminder Agent Keywords (More Specific)
reminder_keywords = [
    "reminder", "remind", "alert", "schedule", "alarm", 
    "wake up", "appointment"
]
```

## 🔧 Supervisor Orchestrator

### Agent Coordination

The supervisor orchestrator coordinates specialized agents:

```python
class SupervisorOrchestrator:
    def __init__(self, model_name: str = "gpt-4o-mini", user_id: str = None):
        self.reminder_agent = ReminderAgent(model_name, user_id)
        self.todo_agent = TodoAgent(model_name, user_id)
        self.supervisor = self._create_supervisor()
```

### Direct Agent Routing

For better performance and context continuity, the system routes directly to agents:

```python
# Call the agent directly instead of going through supervisor
if target_agent == "reminder_agent":
    agent_response = supervisor_orchestrator.reminder_agent.process(
        user_message, conversation_history_for_agent
    )
elif target_agent == "todo_agent":
    agent_response = supervisor_orchestrator.todo_agent.process(
        user_message, conversation_history_for_agent
    )
```

## 🧪 Testing and Validation

### Intent Detection Testing

```python
# Test various message patterns
test_messages = [
    "can you add going to groceries to my to do's",
    "add going to groceries to my to do's",
    "remind me to go to groceries at 6pm",
    "i asked you to add the to do"
]

for message in test_messages:
    is_todo, todo_details = MemoryUtils.detect_todo_intent(message)
    is_reminder, reminder_details = MemoryUtils.detect_reminder_intent(message)
    print(f"{message}: Todo={is_todo}, Reminder={is_reminder}")
```

### Routing Validation

```python
# Test context manager routing
context_manager = ConversationContextManager('test_user')
routed_agent = context_manager.should_route_to_agent(
    "i asked you to add the to do", 
    ['reminder_agent', 'todo_agent']
)
# Should return: 'todo_agent'
```

## 🔄 Conversation Flow Examples

### Successful Todo Flow

```
User: "can you add going to groceries to my to do's"
→ Intent Detection: Todo intent detected
→ Routing: todo_agent
→ Response: "Absolutely! I'll add 'going to groceries' to your to-do list..."

User: "it is tomorrow time is 9:00 am"
→ Context: Active todo_agent with pending time info
→ Routing: todo_agent
→ Response: "The task 'Going to groceries' has been successfully added..."

User: "i asked you to add the to do"
→ Clarification Detection: Todo clarification pattern
→ Routing: todo_agent (overrides any previous routing)
→ Response: "The task 'Going to groceries' has been successfully added..."
```

### Reminder Flow

```
User: "remind me to call mom at 6pm"
→ Intent Detection: Reminder intent detected
→ Routing: reminder_agent
→ Response: "I'll set a reminder for you to call mom at 6pm..."
```

## 🛠️ Extending the System

### Adding New Agents

1. **Create the Agent**:
```python
class NewAgent:
    def __init__(self, model_name: str, user_id: str = None):
        # Initialize agent with tools and persona
        pass
    
    def process(self, user_message: str, conversation_history: List[Dict] = None) -> str:
        # Process user message and return response
        pass
```

2. **Add Intent Detection**:
```python
@classmethod
def detect_new_intent(cls, message: str) -> Tuple[bool, Dict]:
    # Add patterns and logic for new intent type
    pass
```

3. **Update Routing Logic**:
```python
# In app.py
elif is_new_intent:
    should_route_to_specialized = True
    target_agent = "new_agent"
    # Set context and keywords
```

4. **Add to Supervisor**:
```python
# In supervisor.py
self.new_agent = NewAgent(model_name, user_id)
supervisor = create_supervisor([
    self.reminder_agent.get_agent(),
    self.todo_agent.get_agent(),
    self.new_agent.get_agent(),
], model=self.llm, prompt=supervisor_prompt)
```

### Adding New Intent Types

1. **Define Keywords and Patterns**:
```python
NEW_INTENT_KEYWORDS = ["new_keyword1", "new_keyword2"]
new_intent_patterns = [
    r'\b(new_pattern1)\b',
    r'\b(new_pattern2)\b'
]
```

2. **Add Detection Method**:
```python
@classmethod
def detect_new_intent(cls, message: str) -> Tuple[bool, Dict]:
    # Implementation similar to detect_todo_intent
    pass
```

3. **Update Context Keywords**:
```python
def get_context_keywords_for_intent(cls, intent_type: str, details: Dict) -> List[str]:
    if intent_type == "new_intent":
        # Return relevant keywords
        pass
```

## 🎯 Best Practices

### Intent Detection
- Use specific, non-overlapping keywords for different intents
- Prioritize more specific intents over general ones
- Include clarification patterns for better user experience
- Test with natural language variations

### Context Management
- Maintain conversation state for context continuity
- Clear context appropriately to avoid confusion
- Use pending requests for multi-turn interactions
- Save context to persistent storage for user-specific data

### Routing Logic
- Prioritize intent detection over context routing
- Use direct agent routing for better performance
- Handle clarification messages appropriately
- Provide fallback responses for edge cases

### Testing
- Test with various natural language patterns
- Validate routing decisions with different contexts
- Test multi-turn conversations
- Verify user data persistence

## 🔍 Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# In memory_utils.py
logger = logging.getLogger(__name__)
logger.debug(f"Intent detection: todo={is_todo}, reminder={is_reminder}")
```

### Context Inspection

```python
# Get current context
context = context_manager.get_conversation_context()
print(f"Active agent: {context['active_agent']}")
print(f"Conversation topic: {context['conversation_topic']}")
print(f"Context keywords: {context['context_keywords']}")
```

### Routing Debug

```python
# Test routing decisions
routed_agent = context_manager.should_route_to_agent(message, available_agents)
print(f"Message: {message}")
print(f"Routed to: {routed_agent}")
print(f"Available agents: {available_agents}")
```

This enhanced orchestration system provides robust, context-aware routing that handles natural language variations and user clarifications effectively.
