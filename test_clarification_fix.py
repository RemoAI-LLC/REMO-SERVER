#!/usr/bin/env python3
"""
Test script to verify that clarification messages are handled correctly
"""

import requests
import json
from datetime import datetime

def test_clarification_scenario():
    """Test the specific scenario where user clarifies they want a todo, not a reminder"""
    
    base_url = "http://localhost:8000"
    user_id = "test_user_clarification"
    
    # Simulate the exact conversation flow from the user's issue
    conversation_flow = [
        "can you add the going to groceries to my to do's",
        "it is tomorrow time is 9:00 am",
        "i asked you to add the to do"
    ]
    
    print("=== Testing Clarification Scenario ===\n")
    print("Simulating the user's conversation flow:\n")
    
    conversation_history = []
    
    for i, message in enumerate(conversation_flow, 1):
        print(f"{i}. User: '{message}'")
        
        try:
            response = requests.post(
                f"{base_url}/chat",
                json={
                    "message": message,
                    "user_id": user_id,
                    "conversation_history": conversation_history
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                assistant_response = result['response']
                print(f"   Assistant: {assistant_response[:150]}...")
                
                # Add to conversation history for next iteration
                conversation_history.append({"role": "user", "content": message})
                conversation_history.append({"role": "assistant", "content": assistant_response})
                
                # Check if the response indicates the correct intent
                if i == 1:  # First message should be handled as todo
                    if any(keyword in assistant_response.lower() for keyword in ['todo', 'task', 'added', 'created', 'groceries']):
                        print("   ✅ Correctly handled as todo")
                    else:
                        print("   ❌ May not have been handled as todo")
                
                elif i == 2:  # Second message should be handled as todo with time
                    if any(keyword in assistant_response.lower() for keyword in ['todo', 'task', '9:00', '9am', 'tomorrow']):
                        print("   ✅ Correctly handled as todo with time")
                    else:
                        print("   ❌ May not have been handled as todo with time")
                
                elif i == 3:  # Third message should be handled as todo clarification
                    if any(keyword in assistant_response.lower() for keyword in ['todo', 'task', 'added', 'created', 'groceries']):
                        print("   ✅ Correctly handled as todo clarification")
                    elif any(keyword in assistant_response.lower() for keyword in ['reminder', 'remind', 'alarm']):
                        print("   ❌ Incorrectly handled as reminder")
                    else:
                        print("   ⚠️  Response unclear")
                
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
        
        print()
    
    print("="*50)
    print("Testing User Data Retrieval:")
    
    # Test retrieving user data to see what was actually stored
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
    test_clarification_scenario() 