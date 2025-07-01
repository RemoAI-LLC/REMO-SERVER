"""
Human-in-the-Loop Feedback System

This module provides human-in-the-loop capabilities for improving the email assistant agent
based on human feedback and evaluation results.

Following the LangChain agents-from-scratch pattern.
"""

from .feedback_collector import FeedbackCollector, FeedbackItem
from .feedback_analyzer import FeedbackAnalyzer
from .agent_improver import AgentImprover
from .feedback_database import FeedbackDatabase

__all__ = [
    "FeedbackCollector",
    "FeedbackItem", 
    "FeedbackAnalyzer",
    "AgentImprover",
    "FeedbackDatabase"
] 