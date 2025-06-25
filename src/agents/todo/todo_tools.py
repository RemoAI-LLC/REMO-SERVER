"""
Todo Tools
Provides functions for creating, managing, and organizing todo items and tasks.
Uses DynamoDB for user-specific storage.
"""

from typing import Dict, List, Optional
from datetime import datetime
import json
import os
import sys

# Add the parent directory to the path to import DynamoDB service
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from utils.dynamodb_service import DynamoDBService

# Initialize DynamoDB service
dynamodb_service = DynamoDBService()

def _load_todos(user_id: str = None) -> List[Dict]:
    """Load todos for a specific user from DynamoDB"""
    if not user_id:
        return []
    
    try:
        todo_data = dynamodb_service.load_todo_data(user_id)
        return todo_data.get("todos", []) if todo_data else []
    except Exception as e:
        print(f"Error loading todos for user {user_id}: {e}")
        return []

def _save_todos(user_id: str, todos: List[Dict]) -> bool:
    """Save todos for a specific user to DynamoDB"""
    if not user_id:
        return False
    
    try:
        todo_data = {
            "todos": todos,
            "last_updated": datetime.now().isoformat()
        }
        return dynamodb_service.save_todo_data(user_id, todo_data)
    except Exception as e:
        print(f"Error saving todos for user {user_id}: {e}")
        return False

def add_todo(title: str, description: str = "", priority: str = "medium", category: str = "general", user_id: str = None) -> str:
    """
    Add a new todo item with title, description, priority, and category.
    
    Args:
        title: The title/name of the todo item
        description: Optional description of the task
        priority: Priority level (low, medium, high, urgent)
        category: Category for organization (work, personal, shopping, etc.)
        user_id: User ID for user-specific storage
    
    Returns:
        Confirmation message with todo details
    """
    # Validate priority
    valid_priorities = ["low", "medium", "high", "urgent"]
    if priority.lower() not in valid_priorities:
        priority = "medium"
    
    todos = _load_todos(user_id)
    
    todo = {
        "id": f"todo_{len(todos) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "title": title,
        "description": description,
        "priority": priority.lower(),
        "category": category.lower(),
        "created": datetime.now().isoformat(),
        "completed": False,
        "completed_at": None
    }
    
    todos.append(todo)
    
    if _save_todos(user_id, todos):
        return f"✅ Todo added: '{title}' (Priority: {priority.title()}, Category: {category.title()})"
    else:
        return "❌ Failed to save todo to database"

def list_todos(category: str = None, show_completed: bool = False, priority: str = None, user_id: str = None) -> str:
    """
    List todos with optional filtering by category, completion status, and priority.
    
    Args:
        category: Filter by specific category
        show_completed: Whether to include completed todos
        priority: Filter by priority level
        user_id: User ID for user-specific storage
    
    Returns:
        Formatted list of todos
    """
    todos = _load_todos(user_id)
    
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

def mark_todo_complete(todo_id: str, user_id: str = None) -> str:
    """
    Mark a todo item as completed.
    
    Args:
        todo_id: ID of the todo to mark as complete
        user_id: User ID for user-specific storage
    
    Returns:
        Confirmation message
    """
    todos = _load_todos(user_id)
    
    for todo in todos:
        if todo["id"] == todo_id:
            todo["completed"] = True
            todo["completed_at"] = datetime.now().isoformat()
            
            if _save_todos(user_id, todos):
                return f"✅ Todo '{todo['title']}' marked as completed!"
            else:
                return "❌ Failed to save todo completion"
    
    return f"❌ Todo with ID '{todo_id}' not found"

def update_todo(todo_id: str, title: str = None, description: str = None, priority: str = None, category: str = None, user_id: str = None) -> str:
    """
    Update an existing todo's details.
    
    Args:
        todo_id: ID of the todo to update
        title: New title (optional)
        description: New description (optional)
        priority: New priority (optional)
        category: New category (optional)
        user_id: User ID for user-specific storage
    
    Returns:
        Confirmation message
    """
    todos = _load_todos(user_id)
    
    for todo in todos:
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
            
            if _save_todos(user_id, todos):
                return f"✅ Todo '{todo['title']}' updated successfully"
            else:
                return "❌ Failed to save todo update"
    
    return f"❌ Todo with ID '{todo_id}' not found"

def delete_todo(todo_id: str, user_id: str = None) -> str:
    """
    Delete a todo item by ID.
    
    Args:
        todo_id: ID of the todo to delete
        user_id: User ID for user-specific storage
    
    Returns:
        Confirmation message
    """
    todos = _load_todos(user_id)
    
    for i, todo in enumerate(todos):
        if todo["id"] == todo_id:
            deleted_title = todo["title"]
            todos.pop(i)
            
            if _save_todos(user_id, todos):
                return f"✅ Todo '{deleted_title}' deleted successfully"
            else:
                return "❌ Failed to save todo deletion"
    
    return f"❌ Todo with ID '{todo_id}' not found"

def prioritize_todos(user_id: str = None) -> str:
    """
    Show todos organized by priority with recommendations.
    
    Args:
        user_id: User ID for user-specific storage
    
    Returns:
        Prioritized list with recommendations
    """
    todos = _load_todos(user_id)
    
    if not todos:
        return "📝 No todos found to prioritize."
    
    # Filter out completed todos
    active_todos = [t for t in todos if not t.get("completed", False)]
    
    if not active_todos:
        return "🎉 All todos are completed! Great job!"
    
    # Group by priority
    priority_groups = {"urgent": [], "high": [], "medium": [], "low": []}
    
    for todo in active_todos:
        priority = todo.get("priority", "medium")
        if priority in priority_groups:
            priority_groups[priority].append(todo)
    
    result = "🎯 Priority Recommendations:\n\n"
    
    # Show urgent items first
    if priority_groups["urgent"]:
        result += "🚨 URGENT (Do these first!):\n"
        for todo in priority_groups["urgent"]:
            result += f"   • {todo['title']}\n"
        result += "\n"
    
    # Show high priority items
    if priority_groups["high"]:
        result += "🔴 HIGH PRIORITY:\n"
        for todo in priority_groups["high"]:
            result += f"   • {todo['title']}\n"
        result += "\n"
    
    # Show medium priority items
    if priority_groups["medium"]:
        result += "🟡 MEDIUM PRIORITY:\n"
        for todo in priority_groups["medium"]:
            result += f"   • {todo['title']}\n"
        result += "\n"
    
    # Show low priority items
    if priority_groups["low"]:
        result += "🟢 LOW PRIORITY:\n"
        for todo in priority_groups["low"]:
            result += f"   • {todo['title']}\n"
        result += "\n"
    
    # Add recommendations
    total_active = len(active_todos)
    urgent_count = len(priority_groups["urgent"])
    high_count = len(priority_groups["high"])
    
    result += "💡 Recommendations:\n"
    if urgent_count > 0:
        result += f"   • Focus on the {urgent_count} urgent items first\n"
    if high_count > 0:
        result += f"   • Then tackle the {high_count} high priority items\n"
    if total_active > 5:
        result += f"   • Consider breaking down larger tasks (you have {total_active} active todos)\n"
    
    return result 