"""
State Management
Shared state utilities for the multi-agent system.
Provides consistent state handling across all agents.
"""

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class State(TypedDict):
    """
    Shared state structure for the multi-agent system.
    Contains messages and any additional state needed across agents.
    """
    messages: Annotated[list, add_messages] 