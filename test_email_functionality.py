"""
Test Email Assistant Functionality

This script tests the email assistant agent implementation including:
- Email intent detection
- Email agent processing
- Email tools functionality
- Integration with DynamoDB
"""

import os
import sys
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.email.email_agent import EmailAgent
from src.agents.email.email_triage import EmailTriage
from src.memory.memory_utils import MemoryUtils
from src.utils.dynamodb_service import DynamoDBService

def test_email_intent_detection():
    """Test email intent detection functionality."""
    print("🧪 Testing Email Intent Detection")
    print("=" * 50)
    
    test_messages = [
        "compose an email to john@example.com",
        "send email to team@company.com",
        "search for emails from boss",
        "email summary",
        "schedule email for tomorrow",
        "mark email as read",
        "archive email",
        "forward email to colleague",
        "reply to email",
        "show all my emails",
        "how many emails do I have"
    ]
    
    for message in test_messages:
        is_email_intent, details = MemoryUtils.detect_email_intent(message)
        print(f"Message: '{message}'")
        print(f"  Email Intent: {is_email_intent}")
        print(f"  Details: {details}")
        print()

def test_email_agent():
    """Test email agent functionality."""
    print("🧪 Testing Email Agent")
    print("=" * 50)
    
    # Test with a mock user ID
    user_id = "test_user_123"
    email_agent = EmailAgent(user_id)
    
    test_messages = [
        "compose an email",
        "search emails",
        "email summary",
        "help with emails"
    ]
    
    for message in test_messages:
        print(f"User: {message}")
        response = email_agent.process(message)
        print(f"Agent: {response}")
        print()

def test_email_triage():
    """Test email triage functionality."""
    print("🧪 Testing Email Triage")
    print("=" * 50)
    
    user_id = "test_user_123"
    triage = EmailTriage(user_id)
    
    test_emails = [
        {
            "subject": "Urgent: Meeting Tomorrow",
            "body": "Hi, we have an urgent meeting tomorrow at 2pm. Please prepare the presentation.",
            "from": "boss@company.com"
        },
        {
            "subject": "Weekly Newsletter",
            "body": "Here's this week's newsletter with updates and announcements.",
            "from": "newsletter@company.com"
        },
        {
            "subject": "Project Update",
            "body": "The project is progressing well. Here's the latest update.",
            "from": "manager@company.com"
        }
    ]
    
    for i, email in enumerate(test_emails, 1):
        print(f"Email {i}:")
        print(f"  Subject: {email['subject']}")
        print(f"  From: {email['from']}")
        
        triage_result = triage.triage_email(email)
        print(f"  Priority: {triage_result['priority']}")
        print(f"  Category: {triage_result['category']}")
        print(f"  Urgency Score: {triage_result['urgency_score']}")
        print(f"  Suggestions: {triage_result['suggestions']}")
        print()

def test_email_tools():
    """Test email tools functionality."""
    print("🧪 Testing Email Tools")
    print("=" * 50)
    
    user_id = "test_user_123"
    
    # Test email composition
    print("Testing email composition...")
    from src.agents.email.email_tools import compose_email, search_emails, get_email_summary
    
    compose_result = compose_email(
        to_recipients=["test@example.com"],
        subject="Test Email",
        body="This is a test email",
        user_id=user_id
    )
    print(f"Compose result: {compose_result}")
    
    # Test email search
    print("\nTesting email search...")
    search_result = search_emails("meeting", user_id=user_id)
    print(f"Search result: {search_result}")
    
    # Test email summary
    print("\nTesting email summary...")
    summary_result = get_email_summary(user_id=user_id)
    print(f"Summary result: {summary_result}")
    print()

def test_dynamodb_integration():
    """Test DynamoDB integration for emails."""
    print("🧪 Testing DynamoDB Integration")
    print("=" * 50)
    
    try:
        dynamodb_service = DynamoDBService()
        
        # Test email draft saving
        user_id = "test_user_123"
        email_data = {
            "email_id": f"email_{datetime.now().strftime('%Y%m%d_%H%M%S')}_test",
            "to_recipients": ["test@example.com"],
            "subject": "Test Email",
            "body": "This is a test email body",
            "status": "draft",
            "created_at": datetime.now().isoformat()
        }
        
        save_result = dynamodb_service.save_email_draft(user_id, email_data)
        print(f"Save email draft: {save_result}")
        
        # Test retrieving email draft
        email_draft = dynamodb_service.get_email_draft(user_id, email_data["email_id"])
        print(f"Retrieved email draft: {email_draft is not None}")
        
        # Test getting emails
        emails = dynamodb_service.get_emails(user_id)
        print(f"Total emails for user: {len(emails)}")
        
        # Test updating email status
        if email_draft:
            update_result = dynamodb_service.update_email_status(user_id, email_data["email_id"], "sent")
            print(f"Update email status: {update_result}")
        
        # Test deleting email
        delete_result = dynamodb_service.delete_email(user_id, email_data["email_id"])
        print(f"Delete email: {delete_result}")
        
    except Exception as e:
        print(f"❌ DynamoDB test failed: {e}")
    
    print()

def test_integration():
    """Test full integration of email assistant."""
    print("🧪 Testing Full Integration")
    print("=" * 50)
    
    user_id = "test_user_123"
    
    # Test the complete flow
    print("Testing complete email assistant flow...")
    
    # 1. Detect email intent
    message = "compose an email to john@example.com with subject 'Meeting' and body 'Hi John, let's meet tomorrow.'"
    is_email_intent, details = MemoryUtils.detect_email_intent(message)
    print(f"1. Intent detection: {is_email_intent}, {details}")
    
    # 2. Process with email agent
    email_agent = EmailAgent(user_id)
    response = email_agent.process(message)
    print(f"2. Agent response: {response}")
    
    # 3. Triage email (if it were a real email)
    triage = EmailTriage(user_id)
    mock_email = {
        "subject": "Meeting",
        "body": "Hi John, let's meet tomorrow.",
        "from": "user@example.com"
    }
    triage_result = triage.triage_email(mock_email)
    print(f"3. Triage result: {triage_result['priority']}, {triage_result['category']}")
    
    print()

def main():
    """Run all email assistant tests."""
    print("🚀 Starting Email Assistant Tests")
    print("=" * 60)
    print()
    
    try:
        test_email_intent_detection()
        test_email_agent()
        test_email_triage()
        test_email_tools()
        test_dynamodb_integration()
        test_integration()
        
        print("✅ All email assistant tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 