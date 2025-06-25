#!/usr/bin/env python3
"""
Test script to verify todo functionality with improved intent detection
"""

import requests
import json
from datetime import datetime

def test_todo_functionality():
    """Test the todo functionality with various user messages"""
    
    base_url = "http://localhost:8000"
    user_id = "test_user_123"
    
    # Test messages that should be detected as todos
    todo_test_messages = [
        "can you add going to groceries to my to do's",
        "add going to groceries to my to do's",
        "please add going to groceries to my to do's",
        "add going to groceries to my todos",
        "add going to groceries to my todo list",
        "add going to groceries to my task list",
        "add groceries to my to do's",
        "create a todo for groceries"
    ]
    
    # Test messages that should be detected as reminders
    reminder_test_messages = [
        "remind me to go to groceries at 6pm",
        "set a reminder for groceries at 6pm",
        "remind me to call mom tomorrow at 2pm",
        "set an alarm for 7am tomorrow"
    ]
    
    print("=== Testing Todo Functionality ===\n")
    
    # Test todo messages
    print("Testing Todo Detection:")
    for i, message in enumerate(todo_test_messages, 1):
        print(f"\n{i}. Testing: '{message}'")
        
        try:
            response = requests.post(
                f"{base_url}/chat",
                json={
                    "message": message,
                    "user_id": user_id,
                    "conversation_history": []
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   Response: {result['response'][:100]}...")
                
                # Check if the response indicates todo functionality
                if any(keyword in result['response'].lower() for keyword in ['todo', 'task', 'added', 'created', 'groceries']):
                    print("   ✅ Correctly handled as todo")
                else:
                    print("   ❌ May not have been handled as todo")
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
    
    print("\n" + "="*50)
    print("Testing Reminder Detection:")
    
    # Test reminder messages
    for i, message in enumerate(reminder_test_messages, 1):
        print(f"\n{i}. Testing: '{message}'")
        
        try:
            response = requests.post(
                f"{base_url}/chat",
                json={
                    "message": message,
                    "user_id": user_id,
                    "conversation_history": []
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   Response: {result['response'][:100]}...")
                
                # Check if the response indicates reminder functionality
                if any(keyword in result['response'].lower() for keyword in ['reminder', 'remind', 'alarm', 'time', 'schedule']):
                    print("   ✅ Correctly handled as reminder")
                else:
                    print("   ❌ May not have been handled as reminder")
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
    
    print("\n" + "="*50)
    print("Testing User Data Retrieval:")
    
    # Test retrieving user data
    try:
        response = requests.get(f"{base_url}/user/{user_id}/data")
        if response.status_code == 200:
            data = response.json()
            print(f"User data summary: {json.dumps(data, indent=2)}")
        else:
            print(f"Error retrieving user data: {response.status_code}")
    except Exception as e:
        print(f"Exception retrieving user data: {str(e)}")

if __name__ == "__main__":
    test_todo_functionality() 