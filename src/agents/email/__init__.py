"""
Email Assistant Agent Module

This module provides email management capabilities including:
- Email triage and classification
- Email composition and response
- Email scheduling and follow-ups
- Integration with Gmail API (future enhancement)

The email assistant follows the LangChain agents-from-scratch pattern:
1. Building an agent
2. Evaluation
3. Human-in-the-loop
4. Memory
5. Deployment
"""

from .email_agent import EmailAgent
from .email_tools import (
    compose_email,
    send_email,
    schedule_email,
    search_emails,
    mark_email_read,
    archive_email,
    forward_email,
    reply_to_email
)

__all__ = [
    'EmailAgent',
    'compose_email',
    'send_email', 
    'schedule_email',
    'search_emails',
    'mark_email_read',
    'archive_email',
    'forward_email',
    'reply_to_email'
] 