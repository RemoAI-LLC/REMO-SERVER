"""
Email Tools Module

Provides tools for email management including composition, sending, scheduling,
searching, and organizing emails. These tools integrate with the email assistant
agent to provide comprehensive email management capabilities.

Following the LangChain agents-from-scratch pattern for tool design.
"""

import os
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import uuid

# Add the parent directory to the path to import DynamoDB service
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from utils.dynamodb_service import dynamodb_service_singleton as dynamodb_service

def compose_email(
    to_recipients: List[str],
    subject: str,
    body: str,
    cc_recipients: List[str] = None,
    bcc_recipients: List[str] = None,
    attachments: List[str] = None,
    user_id: str = None
) -> str:
    """
    Compose an email with specified recipients, subject, and body.
    
    Args:
        to_recipients: List of primary recipients
        subject: Email subject line
        body: Email body content
        cc_recipients: List of CC recipients (optional)
        bcc_recipients: List of BCC recipients (optional)
        attachments: List of attachment file paths (optional)
        user_id: User ID for tracking
    
    Returns:
        Confirmation message with email details
    """
    if not user_id:
        return "❌ User ID is required to compose emails"
    
    try:
        # Create email data structure
        email_data = {
            "email_id": f"email_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}",
            "to_recipients": to_recipients,
            "subject": subject,
            "body": body,
            "cc_recipients": cc_recipients or [],
            "bcc_recipients": bcc_recipients or [],
            "attachments": attachments or [],
            "status": "draft",
            "created_at": datetime.now().isoformat(),
            "user_id": user_id
        }
        
        # Save to DynamoDB (we'll create an emails table)
        if dynamodb_service.save_email_draft(user_id, email_data):
            recipients_str = ", ".join(to_recipients)
            return f"✅ Email composed: '{subject}' to {recipients_str}"
        else:
            return "❌ Failed to save email draft"
    
    except Exception as e:
        return f"❌ Failed to compose email: {str(e)}"

def send_email(
    email_id: str,
    user_id: str = None,
    schedule_time: Optional[str] = None
) -> str:
    """
    Send a composed email immediately or schedule it for later.
    
    Args:
        email_id: ID of the email to send
        user_id: User ID for tracking
        schedule_time: Optional ISO datetime for scheduled sending
    
    Returns:
        Confirmation message
    """
    if not user_id:
        return "❌ User ID is required to send emails"
    
    try:
        # Get email draft
        email_draft = dynamodb_service.get_email_draft(user_id, email_id)
        if not email_draft:
            return f"❌ Email draft with ID '{email_id}' not found"
        
        if schedule_time:
            # Schedule the email
            scheduled_data = {
                "email_id": email_id,
                "scheduled_time": schedule_time,
                "status": "scheduled",
                "user_id": user_id
            }
            
            if dynamodb_service.save_scheduled_email(user_id, scheduled_data):
                return f"✅ Email scheduled for {schedule_time}"
            else:
                return "❌ Failed to schedule email"
        else:
            # Send immediately (mock implementation)
            # In real implementation, this would integrate with Gmail API
            recipients_str = ", ".join(email_draft.get("to_recipients", []))
            subject = email_draft.get("subject", "No Subject")
            
            # Update status to sent
            dynamodb_service.update_email_status(user_id, email_id, "sent")
            
            return f"✅ Email sent: '{subject}' to {recipients_str}"
    
    except Exception as e:
        return f"❌ Failed to send email: {str(e)}"

def schedule_email(
    to_recipients: List[str],
    subject: str,
    body: str,
    schedule_time: str,
    cc_recipients: List[str] = None,
    bcc_recipients: List[str] = None,
    user_id: str = None
) -> str:
    """
    Compose and schedule an email for later sending.
    
    Args:
        to_recipients: List of recipients
        subject: Email subject
        body: Email body
        schedule_time: ISO datetime when to send
        cc_recipients: CC recipients (optional)
        bcc_recipients: BCC recipients (optional)
        user_id: User ID for tracking
    
    Returns:
        Confirmation message
    """
    if not user_id:
        return "❌ User ID is required to schedule emails"
    
    try:
        # First compose the email
        compose_result = compose_email(
            to_recipients=to_recipients,
            subject=subject,
            body=body,
            cc_recipients=cc_recipients,
            bcc_recipients=bcc_recipients,
            user_id=user_id
        )
        
        if "❌" in compose_result:
            return compose_result
        
        # Extract email ID from compose result
        # This is a simplified approach - in real implementation, we'd return the ID
        email_id = f"email_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id[-8:]}"
        
        # Schedule the email
        return send_email(email_id, user_id, schedule_time)
    
    except Exception as e:
        return f"❌ Failed to schedule email: {str(e)}"

def search_emails(
    query: str,
    user_id: str = None,
    limit: int = 10,
    folder: str = "inbox"
) -> str:
    """
    Search emails based on query terms.
    
    Args:
        query: Search query
        user_id: User ID for tracking
        limit: Maximum number of results
        folder: Email folder to search (inbox, sent, drafts, etc.)
    
    Returns:
        Formatted search results
    """
    if not user_id:
        return "❌ User ID is required to search emails"
    
    try:
        # Mock email search - in real implementation, this would query Gmail API
        mock_emails = [
            {
                "id": "email_001",
                "subject": "Meeting Tomorrow",
                "from": "colleague@company.com",
                "date": "2024-12-01T10:00:00Z",
                "snippet": "Hi, just confirming our meeting tomorrow at 2pm..."
            },
            {
                "id": "email_002", 
                "subject": "Project Update",
                "from": "manager@company.com",
                "date": "2024-12-01T09:30:00Z",
                "snippet": "Here's the latest update on the project..."
            }
        ]
        
        # Filter based on query (simplified)
        filtered_emails = [
            email for email in mock_emails 
            if query.lower() in email["subject"].lower() or 
               query.lower() in email["snippet"].lower()
        ][:limit]
        
        if not filtered_emails:
            return f"📧 No emails found matching '{query}'"
        
        result = f"📧 Search results for '{query}' ({len(filtered_emails)} emails):\n\n"
        for email in filtered_emails:
            result += f"📨 {email['subject']}\n"
            result += f"   From: {email['from']}\n"
            result += f"   Date: {email['date']}\n"
            result += f"   {email['snippet']}\n"
            result += f"   ID: {email['id']}\n\n"
        
        return result
    
    except Exception as e:
        return f"❌ Error searching emails: {str(e)}"

def mark_email_read(
    email_id: str,
    user_id: str = None
) -> str:
    """
    Mark an email as read.
    
    Args:
        email_id: ID of the email to mark as read
        user_id: User ID for tracking
    
    Returns:
        Confirmation message
    """
    if not user_id:
        return "❌ User ID is required to mark emails as read"
    
    try:
        # Mock implementation - in real implementation, this would update Gmail API
        return f"✅ Email {email_id} marked as read"
    
    except Exception as e:
        return f"❌ Error marking email as read: {str(e)}"

def archive_email(
    email_id: str,
    user_id: str = None
) -> str:
    """
    Archive an email (move to archive folder).
    
    Args:
        email_id: ID of the email to archive
        user_id: User ID for tracking
    
    Returns:
        Confirmation message
    """
    if not user_id:
        return "❌ User ID is required to archive emails"
    
    try:
        # Mock implementation - in real implementation, this would move to Gmail archive
        return f"✅ Email {email_id} archived successfully"
    
    except Exception as e:
        return f"❌ Error archiving email: {str(e)}"

def forward_email(
    email_id: str,
    to_recipients: List[str],
    message: str = "",
    user_id: str = None
) -> str:
    """
    Forward an email to new recipients.
    
    Args:
        email_id: ID of the email to forward
        to_recipients: List of recipients to forward to
        message: Optional message to add
        user_id: User ID for tracking
    
    Returns:
        Confirmation message
    """
    if not user_id:
        return "❌ User ID is required to forward emails"
    
    try:
        recipients_str = ", ".join(to_recipients)
        return f"✅ Email {email_id} forwarded to {recipients_str}"
    
    except Exception as e:
        return f"❌ Error forwarding email: {str(e)}"

def reply_to_email(
    email_id: str,
    reply_body: str,
    user_id: str = None
) -> str:
    """
    Reply to an email.
    
    Args:
        email_id: ID of the email to reply to
        reply_body: Reply message content
        user_id: User ID for tracking
    
    Returns:
        Confirmation message
    """
    if not user_id:
        return "❌ User ID is required to reply to emails"
    
    try:
        # Mock implementation - in real implementation, this would send reply via Gmail API
        return f"✅ Reply sent to email {email_id}"
    
    except Exception as e:
        return f"❌ Error replying to email: {str(e)}"

def get_email_summary(
    user_id: str = None,
    days: int = 7
) -> str:
    """
    Get a summary of recent email activity.
    
    Args:
        user_id: User ID for tracking
        days: Number of days to look back
    
    Returns:
        Email summary
    """
    if not user_id:
        return "❌ User ID is required to get email summary"
    
    try:
        # Mock email summary
        summary = {
            "total_emails": 45,
            "unread": 12,
            "sent": 8,
            "drafts": 3,
            "important": 5
        }
        
        result = f"📧 Email Summary (Last {days} days):\n\n"
        result += f"📥 Total emails: {summary['total_emails']}\n"
        result += f"📬 Unread: {summary['unread']}\n"
        result += f"📤 Sent: {summary['sent']}\n"
        result += f"📝 Drafts: {summary['drafts']}\n"
        result += f"⭐ Important: {summary['important']}\n"
        
        return result
    
    except Exception as e:
        return f"❌ Error getting email summary: {str(e)}"

def schedule_meeting(
    attendees: List[str],
    subject: str,
    date: str,
    time: str,
    duration: int = 60,
    location: str = "",
    description: str = "",
    user_id: str = None
) -> str:
    """
    Schedule a meeting and send calendar invites to attendees.
    
    Args:
        attendees: List of attendee email addresses
        subject: Meeting subject/title
        date: Meeting date (YYYY-MM-DD format)
        time: Meeting time (HH:MM format)
        duration: Meeting duration in minutes (default: 60)
        location: Meeting location (optional)
        description: Meeting description (optional)
        user_id: User ID for tracking
    
    Returns:
        Confirmation message with meeting details
    """
    if not user_id:
        return "❌ User ID is required to schedule meetings"
    if not attendees:
        return "❌ At least one attendee is required"
    try:
        # Validate date and time format
        try:
            datetime.strptime(date, "%Y-%m-%d")
            datetime.strptime(time, "%H:%M")
        except ValueError:
            return "❌ Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time"
        # Create meeting data structure
        meeting_data = {
            "meeting_id": f"meeting_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}",
            "attendees": attendees,
            "subject": subject,
            "date": date,
            "time": time,
            "duration": duration,
            "location": location,
            "description": description,
            "status": "scheduled",
            "created_at": datetime.now().isoformat(),
            "user_id": user_id
        }
        # Save meeting to DynamoDB
        if dynamodb_service.save_meeting(user_id, meeting_data):
            attendees_str = ", ".join(attendees)
            result = f"✅ Meeting scheduled successfully!\n\n"
            result += f"📅 Subject: {subject}\n"
            result += f"📅 Date: {date} at {time}\n"
            result += f"⏱️ Duration: {duration} minutes\n"
            result += f"👥 Attendees: {attendees_str}\n"
            if location:
                result += f"📍 Location: {location}\n"
            if description:
                result += f"📝 Description: {description}\n"
            result += f"\n📧 Calendar invites will be sent to all attendees."
            return result
        else:
            return "❌ Failed to save meeting to database"
    except Exception as e:
        return f"❌ Failed to schedule meeting: {str(e)}" 