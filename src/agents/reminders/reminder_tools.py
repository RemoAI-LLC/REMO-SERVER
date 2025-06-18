"""
Reminder Tools
Provides functions for creating, managing, and tracking reminders.
Uses simple in-memory storage for demonstration purposes.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import os

# In-memory storage for reminders (in production, use a proper database)
REMINDERS_STORAGE_FILE = "reminders.json"

def _load_reminders() -> Dict[str, List[Dict]]:
    """Load reminders from storage file"""
    if os.path.exists(REMINDERS_STORAGE_FILE):
        try:
            with open(REMINDERS_STORAGE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"reminders": []}
    return {"reminders": []}

def _save_reminders(reminders: Dict[str, List[Dict]]):
    """Save reminders to storage file"""
    with open(REMINDERS_STORAGE_FILE, 'w') as f:
        json.dump(reminders, f, indent=2)

def set_reminder(title: str, datetime_str: str, description: str = "") -> str:
    """
    Set a new reminder with title, datetime, and optional description.
    
    Args:
        title: The title/name of the reminder
        datetime_str: When the reminder should trigger (ISO format or natural language)
        description: Optional description of the reminder
    
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
        
        reminder = {
            "id": f"rem_{len(_load_reminders()['reminders']) + 1}",
            "title": title,
            "datetime": reminder_time.isoformat(),
            "description": description,
            "created": datetime.now().isoformat(),
            "completed": False
        }
        
        reminders_data = _load_reminders()
        reminders_data["reminders"].append(reminder)
        _save_reminders(reminders_data)
        
        return f"✅ Reminder set: '{title}' for {reminder_time.strftime('%Y-%m-%d %H:%M')}"
    
    except Exception as e:
        return f"❌ Failed to set reminder: {str(e)}"

def list_reminders(show_completed: bool = False) -> str:
    """
    List all reminders, optionally including completed ones.
    
    Args:
        show_completed: Whether to include completed reminders
    
    Returns:
        Formatted list of reminders
    """
    reminders_data = _load_reminders()
    reminders = reminders_data["reminders"]
    
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

def update_reminder(reminder_id: str, title: str = None, datetime_str: str = None, description: str = None) -> str:
    """
    Update an existing reminder's details.
    
    Args:
        reminder_id: ID of the reminder to update
        title: New title (optional)
        datetime_str: New datetime (optional)
        description: New description (optional)
    
    Returns:
        Confirmation message
    """
    reminders_data = _load_reminders()
    
    for reminder in reminders_data["reminders"]:
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
            
            _save_reminders(reminders_data)
            return f"✅ Reminder '{reminder['title']}' updated successfully"
    
    return f"❌ Reminder with ID '{reminder_id}' not found"

def delete_reminder(reminder_id: str) -> str:
    """
    Delete a reminder by ID.
    
    Args:
        reminder_id: ID of the reminder to delete
    
    Returns:
        Confirmation message
    """
    reminders_data = _load_reminders()
    
    for i, reminder in enumerate(reminders_data["reminders"]):
        if reminder["id"] == reminder_id:
            deleted_title = reminder["title"]
            reminders_data["reminders"].pop(i)
            _save_reminders(reminders_data)
            return f"✅ Reminder '{deleted_title}' deleted successfully"
    
    return f"❌ Reminder with ID '{reminder_id}' not found"

def mark_reminder_complete(reminder_id: str) -> str:
    """
    Mark a reminder as completed.
    
    Args:
        reminder_id: ID of the reminder to mark as complete
    
    Returns:
        Confirmation message
    """
    reminders_data = _load_reminders()
    
    for reminder in reminders_data["reminders"]:
        if reminder["id"] == reminder_id:
            reminder["completed"] = True
            reminder["completed_at"] = datetime.now().isoformat()
            _save_reminders(reminders_data)
            return f"✅ Reminder '{reminder['title']}' marked as completed"
    
    return f"❌ Reminder with ID '{reminder_id}' not found" 