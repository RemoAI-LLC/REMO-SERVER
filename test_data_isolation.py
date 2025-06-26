#!/usr/bin/env python3
"""
Test script to verify that todo and reminder data are properly isolated
"""

import requests
import json
from datetime import datetime

def test_data_isolation():
    """Test that todos and reminders are properly isolated"""
    
    base_url = "http://localhost:8000"
    user_id = "test_user_isolation"
    
    print("=== Testing Data Isolation ===\n")
    
    # Step 1: Add some todos
    print("1. Adding todos...")
    todo_messages = [
        "add buy groceries to my to do's",
        "add call mom to my to do's",
        "add finish project to my to do's"
    ]
    
    for message in todo_messages:
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
                print(f"   ✅ {message}: {result['response'][:50]}...")
            else:
                print(f"   ❌ {message}: Error {response.status_code}")
        except Exception as e:
            print(f"   ❌ {message}: Exception {str(e)}")
    
    print("\n2. Adding reminders...")
    reminder_messages = [
        "remind me to take medicine at 8am",
        "remind me to call dentist tomorrow at 2pm",
        "set a reminder for team meeting at 10am"
    ]
    
    for message in reminder_messages:
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
                print(f"   ✅ {message}: {result['response'][:50]}...")
            else:
                print(f"   ❌ {message}: Error {response.status_code}")
        except Exception as e:
            print(f"   ❌ {message}: Exception {str(e)}")
    
    print("\n3. Testing todo listing...")
    try:
        response = requests.post(
            f"{base_url}/chat",
            json={
                "message": "show me all my to do's",
                "user_id": user_id,
                "conversation_history": []
            },
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   Todo Response: {result['response'][:200]}...")
            
            # Check if response contains todo-specific content
            if "todo" in result['response'].lower() and "reminder" not in result['response'].lower():
                print("   ✅ Todo listing appears to be correct (contains 'todo', no 'reminder')")
            else:
                print("   ⚠️  Todo listing may be mixed with reminders")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    print("\n4. Testing reminder listing...")
    try:
        response = requests.post(
            f"{base_url}/chat",
            json={
                "message": "show me all my reminders",
                "user_id": user_id,
                "conversation_history": []
            },
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   Reminder Response: {result['response'][:200]}...")
            
            # Check if response contains reminder-specific content
            if "reminder" in result['response'].lower() and "todo" not in result['response'].lower():
                print("   ✅ Reminder listing appears to be correct (contains 'reminder', no 'todo')")
            else:
                print("   ⚠️  Reminder listing may be mixed with todos")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    print("\n5. Testing user data summary...")
    try:
        response = requests.get(f"{base_url}/user/{user_id}/data")
        if response.status_code == 200:
            data = response.json()
            print(f"   User Data Summary: {json.dumps(data, indent=2)}")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_data_isolation() 