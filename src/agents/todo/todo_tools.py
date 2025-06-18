"""
Todo Tools
Provides functions for creating, managing, and organizing todo items and tasks.
Uses simple in-memory storage for demonstration purposes.
"""

from typing import Dict, List, Optional
from datetime import datetime
import json
import os

# In-memory storage for todos (in production, use a proper database)
TODOS_STORAGE_FILE = "todos.json"

def _load_todos() -> Dict[str, List[Dict]]:
    """Load todos from storage file"""
    if os.path.exists(TODOS_STORAGE_FILE):
        try:
            with open(TODOS_STORAGE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"todos": []}
    return {"todos": []}

def _save_todos(todos: Dict[str, List[Dict]]):
    """Save todos to storage file"""
    with open(TODOS_STORAGE_FILE, 'w') as f:
        json.dump(todos, f, indent=2)

def add_todo(title: str, description: str = "", priority: str = "medium", category: str = "general") -> str:
    """
    Add a new todo item with title, description, priority, and category.
    
    Args:
        title: The title/name of the todo item
        description: Optional description of the task
        priority: Priority level (low, medium, high, urgent)
        category: Category for organization (work, personal, shopping, etc.)
    
    Returns:
        Confirmation message with todo details
    """
    # Validate priority
    valid_priorities = ["low", "medium", "high", "urgent"]
    if priority.lower() not in valid_priorities:
        priority = "medium"
    
    todo = {
        "id": f"todo_{len(_load_todos()['todos']) + 1}",
        "title": title,
        "description": description,
        "priority": priority.lower(),
        "category": category.lower(),
        "created": datetime.now().isoformat(),
        "completed": False,
        "completed_at": None
    }
    
    todos_data = _load_todos()
    todos_data["todos"].append(todo)
    _save_todos(todos_data)
    
    return f"✅ Todo added: '{title}' (Priority: {priority.title()}, Category: {category.title()})"

def list_todos(category: str = None, show_completed: bool = False, priority: str = None) -> str:
    """
    List todos with optional filtering by category, completion status, and priority.
    
    Args:
        category: Filter by specific category
        show_completed: Whether to include completed todos
        priority: Filter by priority level
    
    Returns:
        Formatted list of todos
    """
    todos_data = _load_todos()
    todos = todos_data["todos"]
    
    if not todos:
        return "📝 No todos found."
    
    # Apply filters
    if category:
        todos = [t for t in todos if t.get("category", "").lower() == category.lower()]
    
    if priority:
        todos = [t for t in todos if t.get("priority", "").lower() == priority.lower()]
    
    if not show_completed:
        todos = [t for t in todos if not t.get("completed", False)]
    
    if not todos:
        return "📝 No todos match your criteria."
    
    # Sort by priority and creation date
    priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
    todos.sort(key=lambda x: (priority_order.get(x.get("priority", "medium"), 2), x.get("created", "")))
    
    result = "📋 Your Todos:\n\n"
    for todo in todos:
        status = "✅" if todo.get("completed", False) else "⏳"
        priority_emoji = {"urgent": "🚨", "high": "🔴", "medium": "🟡", "low": "🟢"}
        priority_icon = priority_emoji.get(todo.get("priority", "medium"), "🟡")
        
        result += f"{status} {priority_icon} {todo['title']}\n"
        result += f"   📂 {todo.get('category', 'general').title()}\n"
        if todo.get("description"):
            result += f"   📝 {todo['description']}\n"
        result += f"   📅 Created: {datetime.fromisoformat(todo['created']).strftime('%Y-%m-%d %H:%M')}\n"
        if todo.get("completed_at"):
            result += f"   ✅ Completed: {datetime.fromisoformat(todo['completed_at']).strftime('%Y-%m-%d %H:%M')}\n"
        result += "\n"
    
    return result

def mark_todo_complete(todo_id: str) -> str:
    """
    Mark a todo item as completed.
    
    Args:
        todo_id: ID of the todo to mark as complete
    
    Returns:
        Confirmation message
    """
    todos_data = _load_todos()
    
    for todo in todos_data["todos"]:
        if todo["id"] == todo_id:
            todo["completed"] = True
            todo["completed_at"] = datetime.now().isoformat()
            _save_todos(todos_data)
            return f"✅ Todo '{todo['title']}' marked as completed!"
    
    return f"❌ Todo with ID '{todo_id}' not found"

def update_todo(todo_id: str, title: str = None, description: str = None, priority: str = None, category: str = None) -> str:
    """
    Update an existing todo's details.
    
    Args:
        todo_id: ID of the todo to update
        title: New title (optional)
        description: New description (optional)
        priority: New priority (optional)
        category: New category (optional)
    
    Returns:
        Confirmation message
    """
    todos_data = _load_todos()
    
    for todo in todos_data["todos"]:
        if todo["id"] == todo_id:
            if title:
                todo["title"] = title
            if description is not None:
                todo["description"] = description
            if priority:
                valid_priorities = ["low", "medium", "high", "urgent"]
                if priority.lower() in valid_priorities:
                    todo["priority"] = priority.lower()
            if category:
                todo["category"] = category.lower()
            
            _save_todos(todos_data)
            return f"✅ Todo '{todo['title']}' updated successfully"
    
    return f"❌ Todo with ID '{todo_id}' not found"

def delete_todo(todo_id: str) -> str:
    """
    Delete a todo item by ID.
    
    Args:
        todo_id: ID of the todo to delete
    
    Returns:
        Confirmation message
    """
    todos_data = _load_todos()
    
    for i, todo in enumerate(todos_data["todos"]):
        if todo["id"] == todo_id:
            deleted_title = todo["title"]
            todos_data["todos"].pop(i)
            _save_todos(todos_data)
            return f"✅ Todo '{deleted_title}' deleted successfully"
    
    return f"❌ Todo with ID '{todo_id}' not found"

def prioritize_todos() -> str:
    """
    Show todos organized by priority with recommendations.
    
    Returns:
        Prioritized list with recommendations
    """
    todos_data = _load_todos()
    todos = [t for t in todos_data["todos"] if not t.get("completed", False)]
    
    if not todos:
        return "📝 No active todos found."
    
    # Group by priority
    priority_groups = {"urgent": [], "high": [], "medium": [], "low": []}
    for todo in todos:
        priority = todo.get("priority", "medium")
        priority_groups[priority].append(todo)
    
    result = "🎯 Priority Overview:\n\n"
    
    for priority in ["urgent", "high", "medium", "low"]:
        todos_in_priority = priority_groups[priority]
        if todos_in_priority:
            priority_emoji = {"urgent": "🚨", "high": "🔴", "medium": "🟡", "low": "🟢"}
            result += f"{priority_emoji[priority]} {priority.upper()} Priority ({len(todos_in_priority)} items):\n"
            for todo in todos_in_priority:
                result += f"   • {todo['title']}\n"
            result += "\n"
    
    # Add recommendations
    urgent_count = len(priority_groups["urgent"])
    high_count = len(priority_groups["high"])
    
    if urgent_count > 0:
        result += "💡 Recommendation: Focus on urgent tasks first!\n"
    elif high_count > 3:
        result += "💡 Recommendation: Consider breaking down some high-priority tasks.\n"
    else:
        result += "💡 Recommendation: You're doing great! Keep up the good work.\n"
    
    return result 