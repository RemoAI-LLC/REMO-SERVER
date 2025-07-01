"""
Feedback Module

This module provides human-in-the-loop feedback capabilities for the Remo AI assistant.
It includes feedback collection, analysis, agent improvement, and persistent storage.

Following the LangChain agents-from-scratch human-in-the-loop pattern.
"""

from .feedback_collector import (
    FeedbackCollector, 
    FeedbackItem, 
    FeedbackType, 
    FeedbackRating
)
from .feedback_analyzer import FeedbackAnalyzer
from .agent_improver import AgentImprover, ImprovementAction, ImprovementResult
from .feedback_database import FeedbackDatabase

__all__ = [
    'FeedbackCollector',
    'FeedbackItem', 
    'FeedbackType',
    'FeedbackRating',
    'FeedbackAnalyzer',
    'AgentImprover',
    'ImprovementAction',
    'ImprovementResult',
    'FeedbackDatabase'
]
