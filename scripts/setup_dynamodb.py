#!/usr/bin/env python3
"""
DynamoDB Setup Script for Remo
This script helps set up and test the DynamoDB integration.
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.utils.dynamodb_service import DynamoDBService

def check_environment():
    """Check if required environment variables are set."""
    required_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_REGION',
        'DYNAMODB_TABLE_NAME'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file:")
        print("AWS_ACCESS_KEY_ID=your_aws_access_key_id")
        print("AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key")
        print("AWS_REGION=us-east-1")
        print("DYNAMODB_TABLE_NAME=remo-user-data")
        return False
    
    print("✅ All required environment variables are set")
    return True

def test_dynamodb_connection():
    """Test DynamoDB connection and table creation."""
    try:
        print("\n🔗 Testing DynamoDB connection...")
        service = DynamoDBService()
        
        if service.table is None:
            print("❌ Failed to initialize DynamoDB service")
            return False
        
        print("✅ DynamoDB service initialized successfully")
        
        # Test table creation/access
        try:
            service.table.load()
            print("✅ DynamoDB table exists and is accessible")
        except Exception as e:
            if "ResourceNotFoundException" in str(e):
                print("📝 Creating DynamoDB table...")
                service._create_table()
                print("✅ DynamoDB table created successfully")
            else:
                print(f"❌ Error accessing table: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing DynamoDB connection: {e}")
        return False

def test_user_isolation():
    """Test user data isolation functionality."""
    try:
        print("\n🧪 Testing user data isolation...")
        service = DynamoDBService()
        
        # Test user 1 data
        user1_id = "test_user_1"
        user1_data = {
            "reminders": [
                {"id": "rem_1", "title": "User 1 Meeting", "datetime": "2024-12-02T10:00:00"}
            ]
        }
        
        # Test user 2 data
        user2_id = "test_user_2"
        user2_data = {
            "reminders": [
                {"id": "rem_2", "title": "User 2 Appointment", "datetime": "2024-12-02T11:00:00"}
            ]
        }
        
        # Save data for both users
        service.save_reminder_data(user1_id, user1_data)
        service.save_reminder_data(user2_id, user2_data)
        print("✅ Data saved for both users")
        
        # Load and verify isolation
        loaded_user1 = service.load_reminder_data(user1_id)
        loaded_user2 = service.load_reminder_data(user2_id)
        
        if (loaded_user1 and loaded_user2 and 
            loaded_user1["reminders"][0]["title"] == "User 1 Meeting" and
            loaded_user2["reminders"][0]["title"] == "User 2 Appointment"):
            print("✅ User data isolation verified")
        else:
            print("❌ User data isolation test failed")
            return False
        
        # Clean up test data
        service.delete_user_data(user1_id, "reminder_data")
        service.delete_user_data(user2_id, "reminder_data")
        print("✅ Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing user isolation: {e}")
        return False

def test_conversation_memory():
    """Test conversation memory functionality."""
    try:
        print("\n💬 Testing conversation memory...")
        service = DynamoDBService()
        
        user_id = "test_user_memory"
        memory_data = {
            "conversation_id": "conv_test_123",
            "conversation_start_time": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "memory_type": "buffer",
            "messages": [
                {
                    "role": "user",
                    "content": "Hello Remo!",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "role": "assistant",
                    "content": "Hi! How can I help you today?",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
        
        # Save conversation memory
        service.save_conversation_memory(user_id, memory_data)
        print("✅ Conversation memory saved")
        
        # Load and verify
        loaded_memory = service.load_conversation_memory(user_id)
        if (loaded_memory and 
            loaded_memory["conversation_id"] == "conv_test_123" and
            len(loaded_memory["messages"]) == 2):
            print("✅ Conversation memory loaded and verified")
        else:
            print("❌ Conversation memory test failed")
            return False
        
        # Clean up
        service.delete_user_data(user_id, "conversation_memory")
        print("✅ Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing conversation memory: {e}")
        return False

def show_user_data_summary():
    """Show a summary of all user data."""
    try:
        print("\n📊 User Data Summary:")
        service = DynamoDBService()
        
        # This would typically query all users, but for demo purposes
        # we'll just show the structure
        print("Available data types per user:")
        print("  - conversation_memory: User's conversation history")
        print("  - conversation_context: User's conversation context")
        print("  - user_preferences: User's settings and preferences")
        print("  - reminder_data: User's reminders and alerts")
        print("  - todo_data: User's todo items and tasks")
        
        print("\nData structure:")
        print("  - user_id: Privy user ID (partition key)")
        print("  - data_type: Type of data (sort key)")
        print("  - data: The actual data content")
        print("  - timestamp: Last update timestamp")
        print("  - ttl: Time-to-live for automatic cleanup")
        
        return True
        
    except Exception as e:
        print(f"❌ Error showing data summary: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Remo DynamoDB Setup Script")
    print("=" * 40)
    
    # Check environment
    if not check_environment():
        return
    
    # Test DynamoDB connection
    if not test_dynamodb_connection():
        return
    
    # Test user isolation
    if not test_user_isolation():
        return
    
    # Test conversation memory
    if not test_conversation_memory():
        return
    
    # Show data summary
    show_user_data_summary()
    
    print("\n" + "=" * 40)
    print("✅ DynamoDB setup completed successfully!")
    print("\nNext steps:")
    print("1. Start your Remo server")
    print("2. Test with different user IDs")
    print("3. Monitor DynamoDB usage in AWS Console")
    print("4. Set up CloudWatch monitoring if needed")

if __name__ == "__main__":
    main() 