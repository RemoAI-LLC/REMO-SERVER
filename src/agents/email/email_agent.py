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
from typing import Dict, List, Any
from datetime import datetime
import json
import boto3
from langgraph.prebuilt import create_react_agent
try:
    from langchain_aws import ChatBedrock
except ImportError:
    ChatBedrock = None
import re
from langsmith import traceable

# Add the parent directory to the path to import required modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from utils.dynamodb_service import dynamodb_service_singleton as dynamodb_service
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
        self.dynamodb_service = dynamodb_service
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
            "compose_email": traceable(lambda **kwargs: compose_email(**kwargs, user_id=self.user_id)),
            "send_email": traceable(lambda **kwargs: send_email(**kwargs, user_id=self.user_id)),
            "schedule_email": traceable(lambda **kwargs: schedule_email(**kwargs, user_id=self.user_id)),
            "search_emails": traceable(lambda **kwargs: search_emails(**kwargs, user_id=self.user_id)),
            "mark_email_read": traceable(lambda **kwargs: mark_email_read(**kwargs, user_id=self.user_id)),
            "archive_email": traceable(lambda **kwargs: archive_email(**kwargs, user_id=self.user_id)),
            "forward_email": traceable(lambda **kwargs: forward_email(**kwargs, user_id=self.user_id)),
            "reply_to_email": traceable(lambda **kwargs: reply_to_email(**kwargs, user_id=self.user_id)),
            "get_email_summary": traceable(lambda **kwargs: get_email_summary(**kwargs, user_id=self.user_id)),
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

    def _handle_schedule_email(self, message: str, recursion_count: int = 0) -> str:
        """Handle email scheduling requests with slot filling and recursion limit."""
        MAX_RECURSION = 5
        details, missing = self.extract_meeting_details(message)
        if recursion_count > MAX_RECURSION:
            return f"❌ Sorry, I couldn't extract all the meeting details after several tries. Please provide: {', '.join(missing)}."
        if not missing:
            # All details found, schedule the meeting
            return self.tools["schedule_email_tool"](
                attendees=details['attendees'],
                subject=details['subject'],
                date=details['date'],
                time=details['time'],
                duration=details['duration'],
                location='Google Meet',
                description=details['description']
            )
        else:
            # Log missing fields and ask for only those
            return f"To schedule your meeting, I still need: {', '.join(missing)}. Please provide them in your next message!"

    def extract_meeting_details(self, message: str):
        """
        Extract attendees (emails), date, time, duration, subject, and description from the message.
        Returns a dict with found fields and a list of missing fields.
        """
        details = {}
        missing = []
        # Extract emails
        emails = re.findall(r"[\w\.-]+@[\w\.-]+", message)
        if emails:
            details['attendees'] = emails
        else:
            missing.append('attendees (email addresses)')
        # Extract date (very basic, improve as needed)
        date_match = re.search(r"(\d{4}-\d{2}-\d{2}|\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\b \d{1,2}(?:, \d{4})?)", message, re.IGNORECASE)
        if date_match:
            details['date'] = date_match.group(0)
        else:
            missing.append('date')
        # Extract time (basic)
        time_match = re.search(r"(\d{1,2}:\d{2}\s?(?:am|pm)?|\d{1,2}\s?(?:am|pm))", message, re.IGNORECASE)
        if time_match:
            details['time'] = time_match.group(0)
        else:
            missing.append('time')
        # Extract duration
        duration_match = re.search(r"(\d{1,3})\s?(minutes|min|hrs|hours)", message, re.IGNORECASE)
        if duration_match:
            details['duration'] = int(duration_match.group(1))
        else:
            details['duration'] = 60  # Default
        # Extract subject
        subject_match = re.search(r"subject:?\s*([\w\s]+)", message, re.IGNORECASE)
        if subject_match:
            details['subject'] = subject_match.group(1).strip()
        else:
            details['subject'] = 'Meeting'
        # Extract description
        desc_match = re.search(r"about:?\s*([\w\s]+)", message, re.IGNORECASE)
        if desc_match:
            details['description'] = desc_match.group(1).strip()
        else:
            details['description'] = ''
        return details, missing

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
        Get the compiled agent for use with LangGraph supervisor.
        Returns:
            Compiled agent object
        """
        # Bedrock LLM initialization (reuse if already set)
        model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")
        region = os.getenv("AWS_REGION", "us-east-1")
        access_key = os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        temperature = 0.3
        if ChatBedrock:
            llm = ChatBedrock(
                model_id=model_id,
                region_name=region,
                model_kwargs={"temperature": temperature}
            )
        else:
            class BedrockLLM:
                def __init__(self, model_id, region, access_key, secret_key, temperature):
                    self.model_id = model_id
                    self.temperature = temperature
                    self.client = boto3.client(
                        "bedrock-runtime",
                        region_name=region,
                        aws_access_key_id=access_key,
                        aws_secret_access_key=secret_key,
                    )
                def invoke(self, messages):
                    for m in messages:
                        if isinstance(m.get("content"), str):
                            m["content"] = [{"text": m["content"]}]
                        elif isinstance(m.get("content"), list):
                            m["content"] = [c if isinstance(c, dict) else {"text": c} for c in m["content"]]
                    body = {"messages": messages}
                    response = self.client.invoke_model(
                        modelId=self.model_id,
                        body=json.dumps(body),
                        contentType="application/json",
                        accept="application/json"
                    )
                    result = json.loads(response["body"].read())
                    class Result:
                        def __init__(self, content):
                            self.content = content
                    return Result(result.get("completion") or result.get("output", ""))
            llm = BedrockLLM(model_id, region, access_key, secret_key, temperature)

        # Define tool functions with docstrings
        from langchain.tools import tool
        user_id = self.user_id

        @tool
        def compose_email_tool(**kwargs):
            """Compose an email with recipients, subject, body, and optional CC/BCC/attachments."""
            return compose_email(**kwargs, user_id=user_id)

        @tool
        def send_email_tool(**kwargs):
            """Send an email by email ID or send a composed draft."""
            return send_email(**kwargs, user_id=user_id)

        @tool
        def schedule_email_tool(**kwargs):
            """Schedule an email to be sent at a later date/time."""
            return schedule_email(**kwargs, user_id=user_id)

        @tool
        def search_emails_tool(**kwargs):
            """Search emails by sender, subject, content, or date range."""
            return search_emails(**kwargs, user_id=user_id)

        @tool
        def mark_email_read_tool(**kwargs):
            """Mark an email as read by email ID."""
            return mark_email_read(**kwargs, user_id=user_id)

        @tool
        def archive_email_tool(**kwargs):
            """Archive an email by email ID."""
            return archive_email(**kwargs, user_id=user_id)

        @tool
        def forward_email_tool(**kwargs):
            """Forward an email to new recipients with optional message."""
            return forward_email(**kwargs, user_id=user_id)

        @tool
        def reply_to_email_tool(**kwargs):
            """Reply to an email with a message."""
            return reply_to_email(**kwargs, user_id=user_id)

        @tool
        def get_email_summary_tool(**kwargs):
            """Get a summary of recent emails (e.g., last 7 days)."""
            return get_email_summary(**kwargs, user_id=user_id)

        # Compile the agent using create_react_agent
        return create_react_agent(
            model=llm,
            tools=[
                compose_email_tool,
                send_email_tool,
                schedule_email_tool,
                search_emails_tool,
                mark_email_read_tool,
                archive_email_tool,
                forward_email_tool,
                reply_to_email_tool,
                get_email_summary_tool
            ],
            prompt=self.persona,
            name="email_agent"
        )
    
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