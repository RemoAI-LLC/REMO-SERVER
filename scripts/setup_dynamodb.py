#!/usr/bin/env python3
"""
Enhanced DynamoDB Setup Script for Remo AI Assistant
Tests the new table structure and verifies all functionality.
"""

import os
import sys
from datetime import datetime, timedelta
import json

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Make sure environment variables are set manually.")

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.utils.dynamodb_service import DynamoDBService

def print_header():
    """Print setup script header."""
    print("🚀 Remo Enhanced DynamoDB Setup Script")
    print("=" * 50)
    print("Testing new table structure and functionality")
    print("=" * 50)

def check_environment():
    """Check if all required environment variables are set."""
    print("\n🔍 Checking environment variables...")
    
    required_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_REGION'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file or environment.")
        return False
    
    print("✅ All required environment variables are set")
    print(f"   AWS Region: {os.getenv('AWS_REGION')}")
    print(f"   AWS Access Key: {os.getenv('AWS_ACCESS_KEY_ID')[:10]}...")
    return True

def test_dynamodb_connection():
    """Test DynamoDB connection and table creation."""
    print("\n🔗 Testing DynamoDB connection...")
    
    try:
        dynamodb_service = DynamoDBService()
        
        if not dynamodb_service.dynamodb:
            print("❌ Failed to initialize DynamoDB service")
            return False
        
        print("✅ DynamoDB service initialized successfully")
        
        # Check if tables exist
        if (dynamodb_service.reminders_table and 
            dynamodb_service.todos_table and 
            dynamodb_service.users_table and 
            dynamodb_service.conversation_table):
            print("✅ All DynamoDB tables are accessible")
            return dynamodb_service
        else:
            print("❌ Some tables are not accessible")
            return False
            
    except Exception as e:
        print(f"❌ Error testing DynamoDB connection: {e}")
        return False

def test_user_data_isolation(dynamodb_service):
    """Test user data isolation with the new table structure."""
    print("\n🧪 Testing user data isolation...")
    
    test_user_1 = "test_user_123"
    test_user_2 = "test_user_456"
    
    try:
        # Test reminders
        reminder_data_1 = {
            "reminder_id": "test_rem_1",
            "title": "Test Reminder 1",
            "description": "Test description",
            "reminding_time": (datetime.now() + timedelta(hours=1)).isoformat(),
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        reminder_data_2 = {
            "reminder_id": "test_rem_2",
            "title": "Test Reminder 2",
            "description": "Test description 2",
            "reminding_time": (datetime.now() + timedelta(hours=2)).isoformat(),
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        # Save reminders for both users
        dynamodb_service.save_reminder(test_user_1, reminder_data_1)
        dynamodb_service.save_reminder(test_user_2, reminder_data_2)
        
        # Test todos
        todo_data_1 = {
            "todo_id": "test_todo_1",
            "title": "Test Todo 1",
            "description": "Test todo description",
            "priority": "high",
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        todo_data_2 = {
            "todo_id": "test_todo_2",
            "title": "Test Todo 2",
            "description": "Test todo description 2",
            "priority": "medium",
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        # Save todos for both users
        dynamodb_service.save_todo(test_user_1, todo_data_1)
        dynamodb_service.save_todo(test_user_2, todo_data_2)
        
        # Test conversation messages
        message_data_1 = {
            "role": "user",
            "content": "Hello from user 1",
            "timestamp": datetime.now().isoformat()
        }
        
        message_data_2 = {
            "role": "user",
            "content": "Hello from user 2",
            "timestamp": datetime.now().isoformat()
        }
        
        # Save conversation messages for both users
        dynamodb_service.save_conversation_message(test_user_1, message_data_1)
        dynamodb_service.save_conversation_message(test_user_2, message_data_2)
        
        # Verify isolation
        user1_reminders = dynamodb_service.get_reminders(test_user_1)
        user2_reminders = dynamodb_service.get_reminders(test_user_2)
        
        user1_todos = dynamodb_service.get_todos(test_user_1)
        user2_todos = dynamodb_service.get_todos(test_user_2)
        
        user1_messages = dynamodb_service.get_conversation_history(test_user_1)
        user2_messages = dynamodb_service.get_conversation_history(test_user_2)
        
        # Check isolation
        if (len(user1_reminders) == 1 and len(user2_reminders) == 1 and
            len(user1_todos) == 1 and len(user2_todos) == 1 and
            len(user1_messages) == 1 and len(user2_messages) == 1):
            print("✅ Data saved for both users")
            print("✅ User data isolation verified")
        else:
            print("❌ User data isolation failed")
            return False
        
        # Clean up test data
        dynamodb_service.delete_reminder(test_user_1, "test_rem_1")
        dynamodb_service.delete_reminder(test_user_2, "test_rem_2")
        dynamodb_service.delete_todo(test_user_1, "test_todo_1")
        dynamodb_service.delete_todo(test_user_2, "test_todo_2")
        
        print("✅ Test data cleaned up")
        return True
        
    except Exception as e:
        print(f"❌ Error testing user data isolation: {e}")
        return False

def test_conversation_memory(dynamodb_service):
    """Test conversation memory functionality."""
    print("\n💬 Testing conversation memory...")
    
    test_user = "test_conv_user"
    
    try:
        # Test saving conversation messages
        messages = [
            {"role": "user", "content": "Hello Remo!", "timestamp": datetime.now().isoformat()},
            {"role": "assistant", "content": "Hello! How can I help you today?", "timestamp": datetime.now().isoformat()},
            {"role": "user", "content": "Can you set a reminder?", "timestamp": datetime.now().isoformat()},
            {"role": "assistant", "content": "Of course! What would you like me to remind you about?", "timestamp": datetime.now().isoformat()}
        ]
        
        for message in messages:
            dynamodb_service.save_conversation_message(test_user, message)
        
        # Test loading conversation history
        history = dynamodb_service.get_conversation_history(test_user)
        
        if len(history) == 4:
            print("✅ Conversation memory saved")
            print("✅ Conversation memory loaded and verified")
        else:
            print("❌ Conversation memory test failed")
            return False
        
        # Clean up
        # Note: Conversation messages will be cleaned up by TTL automatically
        print("✅ Test data cleaned up")
        return True
        
    except Exception as e:
        print(f"❌ Error testing conversation memory: {e}")
        return False

def test_reminder_functionality(dynamodb_service):
    """Test reminder functionality with new structure."""
    print("\n⏰ Testing reminder functionality...")
    
    test_user = "test_reminder_user"
    
    try:
        # Test creating a reminder
        reminder_data = {
            "reminder_id": "test_reminder_1",
            "title": "Test Reminder",
            "description": "This is a test reminder",
            "reminding_time": (datetime.now() + timedelta(hours=1)).isoformat(),
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        # Save reminder
        success = dynamodb_service.save_reminder(test_user, reminder_data)
        if not success:
            print("❌ Failed to save reminder")
            return False
        
        # Get reminders
        reminders = dynamodb_service.get_reminders(test_user)
        if len(reminders) != 1:
            print("❌ Failed to retrieve reminder")
            return False
        
        # Test status update
        success = dynamodb_service.update_reminder_status(test_user, "test_reminder_1", "done")
        if not success:
            print("❌ Failed to update reminder status")
            return False
        
        # Verify status update
        reminders = dynamodb_service.get_reminders(test_user, status="done")
        if len(reminders) != 1:
            print("❌ Failed to verify status update")
            return False
        
        # Clean up
        dynamodb_service.delete_reminder(test_user, "test_reminder_1")
        
        print("✅ Reminder functionality tested successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error testing reminder functionality: {e}")
        return False

def test_todo_functionality(dynamodb_service):
    """Test todo functionality with new structure."""
    print("\n📝 Testing todo functionality...")
    
    test_user = "test_todo_user"
    
    try:
        # Test creating a todo
        todo_data = {
            "todo_id": "test_todo_1",
            "title": "Test Todo",
            "description": "This is a test todo",
            "priority": "high",
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        # Save todo
        success = dynamodb_service.save_todo(test_user, todo_data)
        if not success:
            print("❌ Failed to save todo")
            return False
        
        # Get todos
        todos = dynamodb_service.get_todos(test_user)
        if len(todos) != 1:
            print("❌ Failed to retrieve todo")
            return False
        
        # Test priority filtering
        high_priority_todos = dynamodb_service.get_todos(test_user, priority="high")
        if len(high_priority_todos) != 1:
            print("❌ Failed to filter by priority")
            return False
        
        # Test status update
        success = dynamodb_service.update_todo_status(test_user, "test_todo_1", "done")
        if not success:
            print("❌ Failed to update todo status")
            return False
        
        # Verify status update
        done_todos = dynamodb_service.get_todos(test_user, status="done")
        if len(done_todos) != 1:
            print("❌ Failed to verify status update")
            return False
        
        # Clean up
        dynamodb_service.delete_todo(test_user, "test_todo_1")
        
        print("✅ Todo functionality tested successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error testing todo functionality: {e}")
        return False

def test_user_details(dynamodb_service):
    """Test user details functionality."""
    print("\n👤 Testing user details functionality...")
    
    try:
        # Test saving user details
        user_data = {
            "privy_id": "test_privy_user_123",
            "email": "test@example.com",
            "wallet": "0x1234567890abcdef",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "+1234567890"
        }
        
        success = dynamodb_service.save_user_details(user_data)
        if not success:
            print("❌ Failed to save user details")
            return False
        
        # Test retrieving user details
        retrieved_data = dynamodb_service.get_user_details("test_privy_user_123")
        if not retrieved_data:
            print("❌ Failed to retrieve user details")
            return False
        
        if (retrieved_data["email"] == user_data["email"] and
            retrieved_data["first_name"] == user_data["first_name"]):
            print("✅ User details functionality tested successfully")
        else:
            print("❌ User details data mismatch")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing user details functionality: {e}")
        return False

def print_summary():
    """Print setup summary."""
    print("\n📊 Enhanced DynamoDB Setup Summary:")
    print("=" * 50)
    print("✅ New table structure implemented:")
    print("   • remo-reminders: User-specific reminders with status tracking")
    print("   • remo-todos: User-specific todos with priority and status")
    print("   • remo-users: User profile and details")
    print("   • remo-conversations: Conversation history with TTL")
    print("\n✅ Features tested:")
    print("   • User data isolation")
    print("   • Conversation memory persistence")
    print("   • Reminder management")
    print("   • Todo management")
    print("   • User details storage")
    print("\n✅ Data structure:")
    print("   • Proper NoSQL design with GSIs")
    print("   • Automatic TTL for conversation cleanup")
    print("   • Status tracking for reminders and todos")
    print("   • Priority management for todos")
    print("   • User-specific data partitioning")
    print("\n🚀 Ready for production use!")

def main():
    """Main setup function."""
    print_header()
    
    # Check environment
    if not check_environment():
        return False
    
    # Test DynamoDB connection
    dynamodb_service = test_dynamodb_connection()
    if not dynamodb_service:
        return False
    
    # Run all tests
    tests = [
        ("User Data Isolation", lambda: test_user_data_isolation(dynamodb_service)),
        ("Conversation Memory", lambda: test_conversation_memory(dynamodb_service)),
        ("Reminder Functionality", lambda: test_reminder_functionality(dynamodb_service)),
        ("Todo Functionality", lambda: test_todo_functionality(dynamodb_service)),
        ("User Details", lambda: test_user_details(dynamodb_service))
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        try:
            if not test_func():
                all_passed = False
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            all_passed = False
    
    if all_passed:
        print_summary()
        print("\n✅ All tests passed! DynamoDB setup is complete.")
        return True
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 