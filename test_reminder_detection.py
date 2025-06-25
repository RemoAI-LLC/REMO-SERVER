#!/usr/bin/env python3
"""
Test script for reminder detection
"""

import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(__file__))

from src.memory.memory_utils import MemoryUtils

def test_reminder_detection():
    """Test reminder detection with various messages."""
    
    test_messages = [
        "Hello can you add the reminder to read the book for tomorrow 9:00 am",
        "Set a reminder for tomorrow at 10am",
        "Can you remind me to call mom tomorrow morning",
        "I need a reminder for my meeting at 2pm today",
        "Add a todo to buy groceries",
        "What's the weather like?",
        "Remind me to take my medicine at 8pm",
        "Set an alarm for 6am tomorrow",
        "Create a reminder for the dentist appointment next week",
        "I want to be reminded about the party on Saturday"
    ]
    
    print("🧪 Testing Reminder Detection")
    print("=" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Message: {message}")
        
        # Test reminder detection
        is_reminder, details = MemoryUtils.detect_reminder_intent(message)
        
        if is_reminder:
            print(f"   ✅ Detected as REMINDER")
            print(f"   📅 Time: {details.get('time', 'Not specified')}")
            print(f"   📝 Description: {details.get('description', 'Not specified')}")
            print(f"   🎯 Confidence: {details.get('confidence', 'Unknown')}")
        else:
            print(f"   ❌ Not detected as reminder")
        
        # Test time extraction
        time_extracted = MemoryUtils.extract_time_from_message(message)
        if time_extracted:
            print(f"   ⏰ Time extracted: {time_extracted}")

if __name__ == "__main__":
    test_reminder_detection() 