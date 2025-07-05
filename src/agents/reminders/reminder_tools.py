"""
Reminder Tools
Provides functions for creating, managing, and tracking reminders.
Uses enhanced DynamoDB service with proper table structure.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import os
import sys

# Add the parent directory to the path to import DynamoDB service
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from utils.dynamodb_service import DynamoDBService
from src.utils.dynamodb_service import dynamodb_service_singleton as dynamodb_service

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
    if not user_id:
        return "❌ User ID is required to set reminders"
    
    try:
        # Parse datetime (enhanced implementation)
        reminder_time = _parse_datetime(datetime_str)
        if not reminder_time:
            return f"❌ Could not parse datetime: {datetime_str}. Please use a clear format like 'tomorrow 10am' or '2024-01-15 14:30'"
        
        # Create reminder data with new structure
        reminder_data = {
            "reminder_id": f"rem_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id[-8:]}",
            "title": title,
            "description": description,
            "reminding_time": reminder_time.isoformat(),
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        # Save to DynamoDB using new structure
        if dynamodb_service.save_reminder(user_id, reminder_data):
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
    if not user_id:
        return "❌ User ID is required to list reminders"
    
    try:
        # Get reminders from DynamoDB using new structure
        if show_completed:
            reminders = dynamodb_service.get_reminders(user_id)
        else:
            reminders = dynamodb_service.get_reminders(user_id, status="pending")
        
        if not reminders:
            return "📝 No reminders found." if show_completed else "📝 No active reminders found."
        
        # Sort by reminding time
        reminders.sort(key=lambda x: x.get('reminding_time', ''))
        
        result = "📋 Your Reminders:\n\n"
        for reminder in reminders:
            status = "✅" if reminder.get("status") == "done" else "⏰"
            reminder_time = datetime.fromisoformat(reminder["reminding_time"])
            result += f"{status} {reminder['title']}\n"
            result += f"   📅 {reminder_time.strftime('%Y-%m-%d %H:%M')}\n"
            if reminder.get("description"):
                result += f"   📝 {reminder['description']}\n"
            result += f"   🆔 {reminder['reminder_id']}\n"
            result += "\n"
        
        return result
    
    except Exception as e:
        return f"❌ Error listing reminders: {str(e)}"

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
    if not user_id:
        return "❌ User ID is required to update reminders"
    
    try:
        # Get all reminders for the user
        reminders = dynamodb_service.get_reminders(user_id)
        
        # Find the specific reminder
        target_reminder = None
        for reminder in reminders:
            if reminder["reminder_id"] == reminder_id:
                target_reminder = reminder
                break
        
        if not target_reminder:
            return f"❌ Reminder with ID '{reminder_id}' not found"
        
        # Update fields
        updated_data = target_reminder.copy()
        if title:
            updated_data["title"] = title
        if datetime_str:
            parsed_time = _parse_datetime(datetime_str)
            if parsed_time:
                updated_data["reminding_time"] = parsed_time.isoformat()
            else:
                return f"❌ Invalid datetime format: {datetime_str}"
        if description is not None:
            updated_data["description"] = description
        
        # Save updated reminder
        if dynamodb_service.save_reminder(user_id, updated_data):
            return f"✅ Reminder '{updated_data['title']}' updated successfully"
        else:
            return "❌ Failed to save updated reminder"
    
    except Exception as e:
        return f"❌ Error updating reminder: {str(e)}"

def delete_reminder(reminder_id: str, user_id: str = None) -> str:
    """
    Delete a reminder by ID.
    
    Args:
        reminder_id: ID of the reminder to delete
        user_id: User ID for user-specific storage
    
    Returns:
        Confirmation message
    """
    if not user_id:
        return "❌ User ID is required to delete reminders"
    
    try:
        # Get all reminders for the user
        reminders = dynamodb_service.get_reminders(user_id)
        
        # Find the specific reminder
        target_reminder = None
        for reminder in reminders:
            if reminder["reminder_id"] == reminder_id:
                target_reminder = reminder
                break
        
        if not target_reminder:
            return f"❌ Reminder with ID '{reminder_id}' not found"
        
        # Delete the reminder
        if dynamodb_service.delete_reminder(user_id, reminder_id):
            return f"✅ Reminder '{target_reminder['title']}' deleted successfully"
        else:
            return "❌ Failed to delete reminder"
    
    except Exception as e:
        return f"❌ Error deleting reminder: {str(e)}"

def mark_reminder_complete(reminder_id: str, user_id: str = None) -> str:
    """
    Mark a reminder as completed.
    
    Args:
        reminder_id: ID of the reminder to mark as complete
        user_id: User ID for user-specific storage
    
    Returns:
        Confirmation message
    """
    if not user_id:
        return "❌ User ID is required to mark reminders complete"
    
    try:
        # Update reminder status
        if dynamodb_service.update_reminder_status(user_id, reminder_id, "done"):
            return f"✅ Reminder marked as completed"
        else:
            return "❌ Failed to mark reminder as complete"
    
    except Exception as e:
        return f"❌ Error marking reminder complete: {str(e)}"

def _parse_datetime(datetime_str: str) -> Optional[datetime]:
    """
    Parse datetime string into datetime object.
    Supports natural language and ISO format.
    
    Args:
        datetime_str: Datetime string to parse
    
    Returns:
        Parsed datetime object or None if parsing fails
    """
    try:
        # Handle natural language
        datetime_str_lower = datetime_str.lower().strip()
        
        if "tomorrow" in datetime_str_lower:
            base_date = datetime.now() + timedelta(days=1)
        elif "today" in datetime_str_lower:
            base_date = datetime.now()
        elif "next week" in datetime_str_lower:
            base_date = datetime.now() + timedelta(weeks=1)
        else:
            base_date = datetime.now()
        
        # Extract time if present
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(am|pm)?',
            r'(\d{1,2})\s*(am|pm)',
            r'(\d{1,2})\.(\d{2})\s*(am|pm)?'
        ]
        
        import re
        for pattern in time_patterns:
            match = re.search(pattern, datetime_str_lower)
            if match:
                if len(match.groups()) == 3:  # HH:MM AM/PM
                    hour = int(match.group(1))
                    minute = int(match.group(2))
                    ampm = match.group(3)
                elif len(match.groups()) == 2:  # HH AM/PM
                    hour = int(match.group(1))
                    minute = 0
                    ampm = match.group(2)
                else:  # HH:MM
                    hour = int(match.group(1))
                    minute = int(match.group(2))
                    ampm = None
                
                # Handle AM/PM
                if ampm:
                    if ampm == 'pm' and hour != 12:
                        hour += 12
                    elif ampm == 'am' and hour == 12:
                        hour = 0
                
                # Set time
                base_date = base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                break
        
        # Try ISO format if no natural language patterns found
        if base_date == datetime.now():
            try:
                return datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
            except:
                pass
        
        return base_date
    
    except Exception as e:
        print(f"Error parsing datetime '{datetime_str}': {e}")
        return None 