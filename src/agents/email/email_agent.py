"""
Email Assistant Agent

This agent provides comprehensive email management capabilities including:
- Email triage and classification
- Email composition and response
- Email scheduling and follow-ups
- Integration with existing Remo orchestration

Following the LangChain agents-from-scratch pattern for agent design.
"""

import os
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

# Add the parent directory to the path to import required modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from utils.dynamodb_service import DynamoDBService
from .email_tools import (
    compose_email,
    send_email,
    schedule_email,
    search_emails,
    mark_email_read,
    archive_email,
    forward_email,
    reply_to_email,
    get_email_summary
)

class EmailAgent:
    """
    Email Assistant Agent for managing emails.
    
    This agent follows the LangChain agents-from-scratch pattern and integrates
    with the existing Remo orchestration system.
    """
    
    def __init__(self, user_id: str = None):
        """
        Initialize the Email Agent with tools and persona.
        
        Args:
            user_id: User ID for user-specific functionality
        """
        self.name = "email_agent"  # Add name attribute for supervisor
        self.user_id = user_id
        self.dynamodb_service = DynamoDBService()
        self.persona = self._get_persona()
        self.tools = self._get_tools()
        
    def _get_persona(self) -> str:
        """Get the agent's persona for email management."""
        return """You are Remo's Email Assistant, a helpful and efficient email management agent. 

Your capabilities include:
- Composing and sending emails
- Scheduling emails for later
- Searching and organizing emails
- Marking emails as read/unread
- Archiving and forwarding emails
- Replying to emails
- Providing email summaries

You always:
- Ask for clarification when email details are unclear
- Confirm before sending important emails
- Provide helpful suggestions for email composition
- Maintain professional and courteous communication
- Respect user privacy and data security
- Use the available tools to perform email operations

When composing emails:
- Ensure proper grammar and professional tone
- Include appropriate greetings and closings
- Structure content clearly and concisely
- Ask for confirmation before sending

When searching emails:
- Provide relevant and organized results
- Include key information like sender, subject, and date
- Help users find what they're looking for efficiently

Remember: You are here to make email management easier and more efficient for the user."""

    def _get_tools(self) -> Dict[str, Any]:
        """Get the available email tools with user_id binding."""
        return {
            "compose_email": lambda **kwargs: compose_email(**kwargs, user_id=self.user_id),
            "send_email": lambda **kwargs: send_email(**kwargs, user_id=self.user_id),
            "schedule_email": lambda **kwargs: schedule_email(**kwargs, user_id=self.user_id),
            "search_emails": lambda **kwargs: search_emails(**kwargs, user_id=self.user_id),
            "mark_email_read": lambda **kwargs: mark_email_read(**kwargs, user_id=self.user_id),
            "archive_email": lambda **kwargs: archive_email(**kwargs, user_id=self.user_id),
            "forward_email": lambda **kwargs: forward_email(**kwargs, user_id=self.user_id),
            "reply_to_email": lambda **kwargs: reply_to_email(**kwargs, user_id=self.user_id),
            "get_email_summary": lambda **kwargs: get_email_summary(**kwargs, user_id=self.user_id)
        }

    def process(self, user_message: str, conversation_history: List[Dict] = None) -> str:
        """
        Process user message and generate appropriate response.
        
        Args:
            user_message: User's input message
            conversation_history: Previous conversation context
            
        Returns:
            Agent's response
        """
        if not self.user_id:
            return "❌ User ID is required for email operations"
        
        # Analyze user intent
        intent = self._analyze_intent(user_message)
        
        # Route to appropriate handler
        if intent == "compose_email":
            return self._handle_compose_email(user_message)
        elif intent == "send_email":
            return self._handle_send_email(user_message)
        elif intent == "schedule_email":
            return self._handle_schedule_email(user_message)
        elif intent == "search_emails":
            return self._handle_search_emails(user_message)
        elif intent == "email_summary":
            return self._handle_email_summary(user_message)
        elif intent == "manage_email":
            return self._handle_manage_email(user_message)
        else:
            return self._handle_general_email_help(user_message)

    def _analyze_intent(self, message: str) -> str:
        """Analyze user message to determine email-related intent."""
        message_lower = message.lower()
        
        # Compose email intent
        if any(word in message_lower for word in ["compose", "write", "draft", "create email"]):
            return "compose_email"
        
        # Send email intent
        if any(word in message_lower for word in ["send", "send email", "mail"]):
            return "send_email"
        
        # Schedule email intent
        if any(word in message_lower for word in ["schedule", "later", "tomorrow", "next week"]):
            return "schedule_email"
        
        # Search emails intent
        if any(word in message_lower for word in ["search", "find", "look for", "show emails"]):
            return "search_emails"
        
        # Email summary intent
        if any(word in message_lower for word in ["summary", "overview", "how many emails"]):
            return "email_summary"
        
        # Manage email intent (read, archive, forward, reply)
        if any(word in message_lower for word in ["mark read", "archive", "forward", "reply"]):
            return "manage_email"
        
        return "general_help"

    def _handle_compose_email(self, message: str) -> str:
        """Handle email composition requests."""
        # Extract email details from message (simplified)
        # In real implementation, this would use more sophisticated NLP
        
        if "compose" in message.lower() or "write" in message.lower():
            return """📧 I can help you compose an email! 

To compose an email, please provide:
- Recipients (To: field)
- Subject line
- Email body content

You can also include:
- CC recipients
- BCC recipients
- Attachments

Example: "Compose an email to john@example.com with subject 'Meeting Tomorrow' and body 'Hi John, let's meet tomorrow at 2pm to discuss the project.'"

What would you like to include in your email?"""
        
        return "I'm ready to help you compose an email. What would you like to write?"

    def _handle_send_email(self, message: str) -> str:
        """Handle email sending requests."""
        return """📤 I can help you send emails!

To send an email, you can:
1. Compose a new email and send it immediately
2. Send a previously composed draft

Would you like to:
- Compose and send a new email?
- Send an existing draft?
- Schedule an email for later?

Just let me know what you'd like to do!"""

    def _handle_schedule_email(self, message: str) -> str:
        """Handle email scheduling requests."""
        return """⏰ I can help you schedule emails!

To schedule an email, please provide:
- Recipients
- Subject
- Email body
- When you want it sent (date and time)

Example: "Schedule an email to team@company.com with subject 'Weekly Update' and body 'Here's this week's update' for tomorrow at 9am"

When would you like to schedule your email for?"""

    def _handle_search_emails(self, message: str) -> str:
        """Handle email search requests."""
        # Extract search query
        search_terms = message.lower().replace("search", "").replace("find", "").replace("emails", "").strip()
        
        if search_terms:
            return self.tools["search_emails"](query=search_terms)
        else:
            return """🔍 I can help you search your emails!

What would you like to search for? You can search by:
- Sender name or email
- Subject line
- Content keywords
- Date range

Just tell me what you're looking for!"""

    def _handle_email_summary(self, message: str) -> str:
        """Handle email summary requests."""
        return self.tools["get_email_summary"](days=7)

    def _handle_manage_email(self, message: str) -> str:
        """Handle email management requests (read, archive, forward, reply)."""
        message_lower = message.lower()
        
        if "mark read" in message_lower or "read" in message_lower:
            return """📬 I can help you mark emails as read!

To mark an email as read, I need the email ID. You can:
1. Search for the email first to get its ID
2. Then ask me to mark it as read

Would you like me to search for emails first?"""
        
        elif "archive" in message_lower:
            return """📁 I can help you archive emails!

To archive an email, I need the email ID. You can:
1. Search for the email first to get its ID
2. Then ask me to archive it

Would you like me to search for emails first?"""
        
        elif "forward" in message_lower:
            return """↪️ I can help you forward emails!

To forward an email, I need:
- The email ID
- The recipients to forward to
- Optional message to add

Would you like me to search for emails first?"""
        
        elif "reply" in message_lower:
            return """↩️ I can help you reply to emails!

To reply to an email, I need:
- The email ID
- Your reply message

Would you like me to search for emails first?"""
        
        return "I can help you manage your emails! What would you like to do?"

    def _handle_general_email_help(self, message: str) -> str:
        """Handle general email help requests."""
        return """📧 Welcome to Remo's Email Assistant! 

I can help you with:

📝 **Composing Emails**
- Write new emails
- Add recipients, subject, and body
- Include CC/BCC and attachments

📤 **Sending Emails**
- Send emails immediately
- Schedule emails for later
- Send drafts

🔍 **Searching Emails**
- Find emails by sender, subject, or content
- Search in different folders
- Get organized results

📊 **Email Management**
- Mark emails as read/unread
- Archive emails
- Forward emails to others
- Reply to emails
- Get email summaries

Just tell me what you'd like to do with your emails!"""

    def list_emails(self, user_id: str = None) -> str:
        """List user's emails (wrapper for search)."""
        return self.tools["search_emails"](query="", limit=10)

    def compose_and_send(
        self,
        to_recipients: List[str],
        subject: str,
        body: str,
        cc_recipients: List[str] = None,
        bcc_recipients: List[str] = None
    ) -> str:
        """Compose and send an email in one operation."""
        # First compose the email
        compose_result = self.tools["compose_email"](
            to_recipients=to_recipients,
            subject=subject,
            body=body,
            cc_recipients=cc_recipients,
            bcc_recipients=bcc_recipients
        )
        
        if "❌" in compose_result:
            return compose_result
        
        # Extract email ID and send
        # This is simplified - in real implementation, we'd parse the ID from compose_result
        email_id = f"email_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.user_id[-8:]}"
        return self.tools["send_email"](email_id=email_id)
    
    def get_agent(self):
        """
        Get the agent for use with LangGraph supervisor.
        
        Returns:
            Agent configuration for supervisor
        """
        # For now, return a simple agent configuration
        # In a full implementation, this would create a proper LangGraph agent
        return {
            "name": "email_agent",
            "description": "Email management and composition",
            "tools": list(self.tools.keys()),
            "process": self.process
        }
    
    def get_description(self) -> str:
        """
        Get a description of the email agent's capabilities.
        
        Returns:
            Description string
        """
        return """Email Assistant Agent: Manages email composition, sending, searching, and organization. 
        Can compose emails, schedule them for later, search through emails, mark them as read/unread, 
        archive emails, forward emails, and reply to emails. Provides email summaries and helps with 
        email workflow management.""" 