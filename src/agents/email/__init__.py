"""
Email Assistant Agent Package

This package contains all email-related functionality including:
- Email Agent: Main email management agent
- Email Tools: Core email operations (compose, send, search, etc.)
- Email Triage: Email classification and prioritization
"""

# Core email agent components
from .email_agent import EmailAgent
from .email_tools import (
    compose_email,
    send_email,
    schedule_email,
    search_emails,
    mark_email_read,
    archive_email,
    forward_email,
    reply_to_email,
    get_email_summary,
    schedule_meeting
)
from .email_triage import EmailTriage

__all__ = [
    # Core components
    'EmailAgent',
    'EmailTriage',
    
    # Email tools
    'compose_email',
    'send_email',
    'schedule_email',
    'search_emails',
    'mark_email_read',
    'archive_email',
    'forward_email',
    'reply_to_email',
    'get_email_summary',
    'schedule_meeting',
] 