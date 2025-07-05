"""
Todo Tools
Provides functions for creating, managing, and organizing todo items and tasks.
Uses enhanced DynamoDB service with proper table structure.
"""

from typing import Dict, List, Optional
from datetime import datetime
import json
import os
import sys

# Add the parent directory to the path to import DynamoDB service
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src.utils.dynamodb_service import dynamodb_service_singleton as dynamodb_service

def add_todo(task: str, priority: str = "medium", category: str = "general", due_date: str = None, user_id: str = None) -> str:
    """
    Add a new todo item with task description, priority, category, and optional due date.
    
    Args:
        task: The task description
        priority: Priority level (low, medium, high, urgent)
        category: Category for organization (work, personal, shopping, etc.)
        due_date: Optional due date (ISO format or natural language)
        user_id: User ID for user-specific storage
    
    Returns:
        Confirmation message with todo details
    """
    if not user_id:
        return "❌ User ID is required to add todos"
    
    # Validate priority
    valid_priorities = ["low", "medium", "high", "urgent"]
    if priority.lower() not in valid_priorities:
        priority = "medium"
    
    try:
        # Create todo data with new structure
        todo_data = {
            "todo_id": f"todo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id[-8:]}",
            "title": task,
            "description": task,  # Use task as description for now
            "priority": priority.lower(),
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        # Save to DynamoDB using new structure
        if dynamodb_service.save_todo(user_id, todo_data):
            return f"✅ Todo added: '{task}' (Priority: {priority.title()}, Category: {category.title()})"
        else:
            return "❌ Failed to save todo to database"
    
    except Exception as e:
        return f"❌ Failed to add todo: {str(e)}"

def list_todos(show_completed: bool = False, category: str = None, user_id: str = None) -> str:
    """
    List todos with optional filtering by category, completion status, and priority.
    
    Args:
        show_completed: Whether to include completed todos
        category: Filter by specific category
        user_id: User ID for user-specific storage
    
    Returns:
        Formatted list of todos
    """
    if not user_id:
        return "❌ User ID is required to list todos"
    
    try:
        # Get todos from DynamoDB using new structure
        if show_completed:
            todos = dynamodb_service.get_todos(user_id)
        else:
            todos = dynamodb_service.get_todos(user_id, status="pending")
        
        if not todos:
            return "📝 No todos found." if show_completed else "📝 No active todos found."
        
        # Sort by priority and creation date
        priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
        todos.sort(key=lambda x: (priority_order.get(x.get("priority", "medium"), 2), x.get("created_at", "")))
        
        result = "📋 Your Todos:\n\n"
        for todo in todos:
            status = "✅" if todo.get("status") == "done" else "⏳"
            priority_emoji = {"urgent": "🚨", "high": "🔴", "medium": "🟡", "low": "🟢"}
            priority_icon = priority_emoji.get(todo.get("priority", "medium"), "🟡")
            
            result += f"{status} {priority_icon} {todo['title']}\n"
            if todo.get("description") and todo.get("description") != todo.get("title"):
                result += f"   📝 {todo['description']}\n"
            result += f"   📅 Created: {datetime.fromisoformat(todo['created_at']).strftime('%Y-%m-%d %H:%M')}\n"
            result += f"   🆔 {todo['todo_id']}\n"
            result += "\n"
        
        return result
    
    except Exception as e:
        return f"❌ Error listing todos: {str(e)}"

def mark_todo_complete(todo_id: str, user_id: str = None) -> str:
    """
    Mark a todo item as completed.
    
    Args:
        todo_id: ID of the todo to mark as complete
        user_id: User ID for user-specific storage
    
    Returns:
        Confirmation message
    """
    if not user_id:
        return "❌ User ID is required to mark todos complete"
    
    try:
        # Update todo status
        if dynamodb_service.update_todo_status(user_id, todo_id, "done"):
            return f"✅ Todo marked as completed!"
        else:
            return "❌ Failed to mark todo as complete"
    
    except Exception as e:
        return f"❌ Error marking todo complete: {str(e)}"

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
    if not user_id:
        return "❌ User ID is required to update todos"
    
    try:
        # Get all todos for the user
        todos = dynamodb_service.get_todos(user_id)
        
        # Find the specific todo
        target_todo = None
        for todo in todos:
            if todo["todo_id"] == todo_id:
                target_todo = todo
                break
        
        if not target_todo:
            return f"❌ Todo with ID '{todo_id}' not found"
        
        # Update fields
        updated_data = target_todo.copy()
        if title:
            updated_data["title"] = title
        if description is not None:
            updated_data["description"] = description
        if priority:
            valid_priorities = ["low", "medium", "high", "urgent"]
            if priority.lower() in valid_priorities:
                updated_data["priority"] = priority.lower()
        
        # Save updated todo
        if dynamodb_service.save_todo(user_id, updated_data):
            return f"✅ Todo '{updated_data['title']}' updated successfully"
        else:
            return "❌ Failed to save todo update"
    
    except Exception as e:
        return f"❌ Error updating todo: {str(e)}"

def delete_todo(todo_id: str, user_id: str = None) -> str:
    """
    Delete a todo item by ID.
    
    Args:
        todo_id: ID of the todo to delete
        user_id: User ID for user-specific storage
    
    Returns:
        Confirmation message
    """
    if not user_id:
        return "❌ User ID is required to delete todos"
    
    try:
        # Get all todos for the user
        todos = dynamodb_service.get_todos(user_id)
        
        # Find the specific todo
        target_todo = None
        for todo in todos:
            if todo["todo_id"] == todo_id:
                target_todo = todo
                break
        
        if not target_todo:
            return f"❌ Todo with ID '{todo_id}' not found"
        
        # Delete the todo
        if dynamodb_service.delete_todo(user_id, todo_id):
            return f"✅ Todo '{target_todo['title']}' deleted successfully"
        else:
            return "❌ Failed to delete todo"
    
    except Exception as e:
        return f"❌ Error deleting todo: {str(e)}"

def prioritize_todos(user_id: str = None) -> str:
    """
    Prioritize and organize todos by importance and urgency.
    
    Args:
        user_id: User ID for user-specific storage
    
    Returns:
        Formatted prioritized todo list
    """
    if not user_id:
        return "❌ User ID is required to prioritize todos"
    
    try:
        # Get all pending todos
        todos = dynamodb_service.get_todos(user_id, status="pending")
        
        if not todos:
            return "📝 No active todos to prioritize."
        
        # Sort by priority
        priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
        todos.sort(key=lambda x: priority_order.get(x.get("priority", "medium"), 2))
        
        result = "🎯 Prioritized Todo List:\n\n"
        
        current_priority = None
        for todo in todos:
            priority = todo.get("priority", "medium")
            
            # Add priority header if it's a new priority level
            if priority != current_priority:
                priority_emoji = {"urgent": "🚨", "high": "🔴", "medium": "🟡", "low": "🟢"}
                priority_icon = priority_emoji.get(priority, "🟡")
                result += f"\n{priority_icon} {priority.upper()} PRIORITY:\n"
                current_priority = priority
            
            result += f"   ⏳ {todo['title']}\n"
            if todo.get("description") and todo.get("description") != todo.get("title"):
                result += f"      📝 {todo['description']}\n"
            result += f"      📅 Created: {datetime.fromisoformat(todo['created_at']).strftime('%Y-%m-%d %H:%M')}\n"
            result += f"      🆔 {todo['todo_id']}\n\n"
        
        return result
    
    except Exception as e:
        return f"❌ Error prioritizing todos: {str(e)}" 