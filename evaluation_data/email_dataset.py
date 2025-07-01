"""
Email Assistant Evaluation Dataset

This module provides a comprehensive dataset for evaluating the email assistant agent.
The dataset includes various email-related scenarios and expected responses.

Following the LangChain agents-from-scratch evaluation pattern.
"""

from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class EmailTestCase:
    """Represents a single email test case."""
    id: str
    user_message: str
    expected_intent: str
    expected_action: str
    expected_response_contains: List[str]
    expected_response_not_contains: List[str] = None
    context: Dict[str, Any] = None
    difficulty: str = "medium"  # easy, medium, hard
    category: str = "general"  # composition, search, management, triage

class EmailEvaluationDataset:
    """Comprehensive dataset for email assistant evaluation."""
    
    def __init__(self):
        self.test_cases = self._create_test_cases()
    
    def _create_test_cases(self) -> List[EmailTestCase]:
        """Create comprehensive test cases for email assistant evaluation."""
        return [
            # ===== EMAIL COMPOSITION TESTS =====
            EmailTestCase(
                id="compose_001",
                user_message="compose an email to john@example.com",
                expected_intent="email",
                expected_action="compose_email",
                expected_response_contains=["compose", "email", "recipients", "subject", "body"],
                difficulty="easy",
                category="composition"
            ),
            EmailTestCase(
                id="compose_002",
                user_message="write an email to the team about the project update",
                expected_intent="email",
                expected_action="compose_email",
                expected_response_contains=["compose", "email", "recipients", "subject", "body"],
                difficulty="medium",
                category="composition"
            ),
            EmailTestCase(
                id="compose_003",
                user_message="send an email to john@example.com with subject 'Meeting Tomorrow' and body 'Hi John, let's meet tomorrow at 2pm to discuss the project.'",
                expected_intent="email",
                expected_action="compose_email",
                expected_response_contains=["compose", "email", "john@example.com", "Meeting Tomorrow"],
                difficulty="hard",
                category="composition"
            ),
            
            # ===== EMAIL SEARCH TESTS =====
            EmailTestCase(
                id="search_001",
                user_message="search for emails from boss",
                expected_intent="email",
                expected_action="search_emails",
                expected_response_contains=["search", "emails", "boss"],
                difficulty="easy",
                category="search"
            ),
            EmailTestCase(
                id="search_002",
                user_message="find emails about the project deadline",
                expected_intent="email",
                expected_action="search_emails",
                expected_response_contains=["search", "emails", "project", "deadline"],
                difficulty="medium",
                category="search"
            ),
            EmailTestCase(
                id="search_003",
                user_message="show me all emails from last week",
                expected_intent="email",
                expected_action="list_emails",
                expected_response_contains=["emails", "last week"],
                difficulty="medium",
                category="search"
            ),
            
            # ===== EMAIL SUMMARY TESTS =====
            EmailTestCase(
                id="summary_001",
                user_message="email summary",
                expected_intent="email",
                expected_action="email_summary",
                expected_response_contains=["email summary", "total emails", "unread"],
                difficulty="easy",
                category="summary"
            ),
            EmailTestCase(
                id="summary_002",
                user_message="how many emails do I have",
                expected_intent="email",
                expected_action="email_summary",
                expected_response_contains=["email", "total", "count"],
                difficulty="easy",
                category="summary"
            ),
            
            # ===== EMAIL SCHEDULING TESTS =====
            EmailTestCase(
                id="schedule_001",
                user_message="schedule an email for tomorrow",
                expected_intent="email",
                expected_action="schedule_email",
                expected_response_contains=["schedule", "email", "tomorrow"],
                difficulty="medium",
                category="scheduling"
            ),
            EmailTestCase(
                id="schedule_002",
                user_message="send an email to the team next week about the quarterly review",
                expected_intent="email",
                expected_action="schedule_email",
                expected_response_contains=["schedule", "email", "next week"],
                difficulty="hard",
                category="scheduling"
            ),
            
            # ===== EMAIL MANAGEMENT TESTS =====
            EmailTestCase(
                id="manage_001",
                user_message="mark email as read",
                expected_intent="email",
                expected_action="manage_email",
                expected_response_contains=["mark", "read", "email"],
                difficulty="easy",
                category="management"
            ),
            EmailTestCase(
                id="manage_002",
                user_message="archive email",
                expected_intent="email",
                expected_action="manage_email",
                expected_response_contains=["archive", "email"],
                difficulty="easy",
                category="management"
            ),
            EmailTestCase(
                id="manage_003",
                user_message="forward email to colleague",
                expected_intent="email",
                expected_action="manage_email",
                expected_response_contains=["forward", "email", "colleague"],
                difficulty="medium",
                category="management"
            ),
            EmailTestCase(
                id="manage_004",
                user_message="reply to email",
                expected_intent="email",
                expected_action="manage_email",
                expected_response_contains=["reply", "email"],
                difficulty="medium",
                category="management"
            ),
            
            # ===== EDGE CASES AND ERROR HANDLING =====
            EmailTestCase(
                id="edge_001",
                user_message="compose an email",
                expected_intent="email",
                expected_action="compose_email",
                expected_response_contains=["compose", "email", "recipients", "subject"],
                expected_response_not_contains=["error", "failed"],
                difficulty="easy",
                category="edge_cases"
            ),
            EmailTestCase(
                id="edge_002",
                user_message="email",
                expected_intent="email",
                expected_action="general_email",
                expected_response_contains=["email", "help"],
                difficulty="easy",
                category="edge_cases"
            ),
            EmailTestCase(
                id="edge_003",
                user_message="send email without recipients",
                expected_intent="email",
                expected_action="compose_email",
                expected_response_contains=["recipients", "need"],
                difficulty="medium",
                category="edge_cases"
            ),
            
            # ===== CONTEXT-AWARE TESTS =====
            EmailTestCase(
                id="context_001",
                user_message="compose an email to john@example.com",
                expected_intent="email",
                expected_action="compose_email",
                expected_response_contains=["compose", "email", "john@example.com"],
                context={"previous_topic": "email", "user_intent": "email_management"},
                difficulty="medium",
                category="context"
            ),
            EmailTestCase(
                id="context_002",
                user_message="to john@example.com",
                expected_intent="email",
                expected_action="compose_email",
                expected_response_contains=["recipients", "john@example.com"],
                context={"previous_topic": "email", "pending_request": "compose_email"},
                difficulty="hard",
                category="context"
            ),
            
            # ===== NEGATIVE TESTS (Should NOT be email intents) =====
            EmailTestCase(
                id="negative_001",
                user_message="add groceries to my todo list",
                expected_intent="todo",
                expected_action="add_todo",
                expected_response_contains=["todo", "task"],
                expected_response_not_contains=["email", "mail"],
                difficulty="easy",
                category="negative"
            ),
            EmailTestCase(
                id="negative_002",
                user_message="remind me to call mom at 6pm",
                expected_intent="reminder",
                expected_action="set_reminder",
                expected_response_contains=["reminder", "call mom"],
                expected_response_not_contains=["email", "mail"],
                difficulty="easy",
                category="negative"
            ),
            EmailTestCase(
                id="negative_003",
                user_message="what's the weather like",
                expected_intent="general",
                expected_action="general_response",
                expected_response_contains=["weather"],
                expected_response_not_contains=["email", "mail"],
                difficulty="easy",
                category="negative"
            ),
        ]
    
    def get_test_cases_by_category(self, category: str) -> List[EmailTestCase]:
        """Get test cases filtered by category."""
        return [tc for tc in self.test_cases if tc.category == category]
    
    def get_test_cases_by_difficulty(self, difficulty: str) -> List[EmailTestCase]:
        """Get test cases filtered by difficulty."""
        return [tc for tc in self.test_cases if tc.difficulty == difficulty]
    
    def get_test_cases_by_intent(self, intent: str) -> List[EmailTestCase]:
        """Get test cases filtered by expected intent."""
        return [tc for tc in self.test_cases if tc.expected_intent == intent]
    
    def get_all_test_cases(self) -> List[EmailTestCase]:
        """Get all test cases."""
        return self.test_cases
    
    def get_test_case_by_id(self, test_id: str) -> EmailTestCase:
        """Get a specific test case by ID."""
        for tc in self.test_cases:
            if tc.id == test_id:
                return tc
        raise ValueError(f"Test case with ID '{test_id}' not found")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get dataset statistics."""
        total_cases = len(self.test_cases)
        categories = {}
        difficulties = {}
        intents = {}
        
        for tc in self.test_cases:
            # Count categories
            categories[tc.category] = categories.get(tc.category, 0) + 1
            
            # Count difficulties
            difficulties[tc.difficulty] = difficulties.get(tc.difficulty, 0) + 1
            
            # Count intents
            intents[tc.expected_intent] = intents.get(tc.expected_intent, 0) + 1
        
        return {
            "total_test_cases": total_cases,
            "categories": categories,
            "difficulties": difficulties,
            "intents": intents,
            "categories_count": len(categories),
            "difficulties_count": len(difficulties),
            "intents_count": len(intents)
        }

# Convenience functions for easy access
def get_email_dataset() -> EmailEvaluationDataset:
    """Get the email evaluation dataset."""
    return EmailEvaluationDataset()

def get_test_cases() -> List[EmailTestCase]:
    """Get all test cases."""
    return get_email_dataset().get_all_test_cases()

def get_composition_tests() -> List[EmailTestCase]:
    """Get email composition test cases."""
    return get_email_dataset().get_test_cases_by_category("composition")

def get_search_tests() -> List[EmailTestCase]:
    """Get email search test cases."""
    return get_email_dataset().get_test_cases_by_category("search")

def get_management_tests() -> List[EmailTestCase]:
    """Get email management test cases."""
    return get_email_dataset().get_test_cases_by_category("management")

def get_easy_tests() -> List[EmailTestCase]:
    """Get easy difficulty test cases."""
    return get_email_dataset().get_test_cases_by_difficulty("easy")

def get_medium_tests() -> List[EmailTestCase]:
    """Get medium difficulty test cases."""
    return get_email_dataset().get_test_cases_by_difficulty("medium")

def get_hard_tests() -> List[EmailTestCase]:
    """Get hard difficulty test cases."""
    return get_email_dataset().get_test_cases_by_difficulty("hard") 