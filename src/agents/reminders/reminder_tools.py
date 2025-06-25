"""
Reminder Tools
Provides functions for creating, managing, and tracking reminders.
Uses DynamoDB for user-specific storage.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import os
import sys

# Add the parent directory to the path to import DynamoDB service
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from utils.dynamodb_service import DynamoDBService

# Initialize DynamoDB service
dynamodb_service = DynamoDBService()

def _load_reminders(user_id: str = None) -> List[Dict]:
    """Load reminders for a specific user from DynamoDB"""
    if not user_id:
        return []
    
    try:
        reminder_data = dynamodb_service.load_reminder_data(user_id)
        return reminder_data.get("reminders", []) if reminder_data else []
    except Exception as e:
        print(f"Error loading reminders for user {user_id}: {e}")
        return []

def _save_reminders(user_id: str, reminders: List[Dict]) -> bool:
    """Save reminders for a specific user to DynamoDB"""
    if not user_id:
        return False
    
    try:
        reminder_data = {
            "reminders": reminders,
            "last_updated": datetime.now().isoformat()
        }
        return dynamodb_service.save_reminder_data(user_id, reminder_data)
    except Exception as e:
        print(f"Error saving reminders for user {user_id}: {e}")
        return False

def set_reminder(title: str, datetime_str: str, description: str = "", user_id: str = None) -> str:
    """
    Set a new reminder with title, datetime, and optional description.
    
    Args:
        title: The title/name of the reminder
        datetime_str: When the reminder should trigger (ISO format or natural language)
        description: Optional description of the reminder
        user_id: User ID for user-specific storage
    
    Returns:
        Confirmation message with reminder details
    """
    try:
        # Parse datetime (simple implementation - in production use better parsing)
        if "tomorrow" in datetime_str.lower():
            reminder_time = datetime.now() + timedelta(days=1)
        elif "today" in datetime_str.lower():
            reminder_time = datetime.now()
        else:
            # Try to parse as ISO format or specific time
            reminder_time = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
        
        reminders = _load_reminders(user_id)
        
        reminder = {
            "id": f"rem_{len(reminders) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "title": title,
            "datetime": reminder_time.isoformat(),
            "description": description,
            "created": datetime.now().isoformat(),
            "completed": False
        }
        
        reminders.append(reminder)
        
        if _save_reminders(user_id, reminders):
            return f"✅ Reminder set: '{title}' for {reminder_time.strftime('%Y-%m-%d %H:%M')}"
        else:
            return "❌ Failed to save reminder to database"
    
    except Exception as e:
        return f"❌ Failed to set reminder: {str(e)}"

def list_reminders(show_completed: bool = False, user_id: str = None) -> str:
    """
    List all reminders for a specific user, optionally including completed ones.
    
    Args:
        show_completed: Whether to include completed reminders
        user_id: User ID for user-specific storage
    
    Returns:
        Formatted list of reminders
    """
    reminders = _load_reminders(user_id)
    
    if not reminders:
        return "📝 No reminders found."
    
    # Filter reminders based on completion status
    if not show_completed:
        reminders = [r for r in reminders if not r.get("completed", False)]
    
    if not reminders:
        return "📝 No active reminders found."
    
    result = "📋 Your Reminders:\n\n"
    for reminder in reminders:
        status = "✅" if reminder.get("completed", False) else "⏰"
        reminder_time = datetime.fromisoformat(reminder["datetime"])
        result += f"{status} {reminder['title']}\n"
        result += f"   📅 {reminder_time.strftime('%Y-%m-%d %H:%M')}\n"
        if reminder.get("description"):
            result += f"   📝 {reminder['description']}\n"
        result += "\n"
    
    return result

def update_reminder(reminder_id: str, title: str = None, datetime_str: str = None, description: str = None, user_id: str = None) -> str:
    """
    Update an existing reminder's details.
    
    Args:
        reminder_id: ID of the reminder to update
        title: New title (optional)
        datetime_str: New datetime (optional)
        description: New description (optional)
        user_id: User ID for user-specific storage
    
    Returns:
        Confirmation message
    """
    reminders = _load_reminders(user_id)
    
    for reminder in reminders:
        if reminder["id"] == reminder_id:
            if title:
                reminder["title"] = title
            if datetime_str:
                try:
                    reminder_time = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
                    reminder["datetime"] = reminder_time.isoformat()
                except:
                    return f"❌ Invalid datetime format: {datetime_str}"
            if description is not None:
                reminder["description"] = description
            
            if _save_reminders(user_id, reminders):
                return f"✅ Reminder '{reminder['title']}' updated successfully"
            else:
                return "❌ Failed to save updated reminder"
    
    return f"❌ Reminder with ID '{reminder_id}' not found"

def delete_reminder(reminder_id: str, user_id: str = None) -> str:
    """
    Delete a reminder by ID.
    
    Args:
        reminder_id: ID of the reminder to delete
        user_id: User ID for user-specific storage
    
    Returns:
        Confirmation message
    """
    reminders = _load_reminders(user_id)
    
    for i, reminder in enumerate(reminders):
        if reminder["id"] == reminder_id:
            deleted_title = reminder["title"]
            reminders.pop(i)
            
            if _save_reminders(user_id, reminders):
                return f"✅ Reminder '{deleted_title}' deleted successfully"
            else:
                return "❌ Failed to save reminder deletion"
    
    return f"❌ Reminder with ID '{reminder_id}' not found"

def mark_reminder_complete(reminder_id: str, user_id: str = None) -> str:
    """
    Mark a reminder as completed.
    
    Args:
        reminder_id: ID of the reminder to mark as complete
        user_id: User ID for user-specific storage
    
    Returns:
        Confirmation message
    """
    reminders = _load_reminders(user_id)
    
    for reminder in reminders:
        if reminder["id"] == reminder_id:
            reminder["completed"] = True
            reminder["completed_at"] = datetime.now().isoformat()
            
            if _save_reminders(user_id, reminders):
                return f"✅ Reminder '{reminder['title']}' marked as completed"
            else:
                return "❌ Failed to save reminder completion"
    
    return f"❌ Reminder with ID '{reminder_id}' not found" 