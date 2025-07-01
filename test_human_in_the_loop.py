#!/usr/bin/env python3
"""
Test script for Human-in-the-Loop Feedback System

This script tests the human-in-the-loop capabilities for the email assistant agent,
including feedback collection, analysis, and agent improvement.

Following the LangChain agents-from-scratch human-in-the-loop pattern.
"""

import os
import sys
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.feedback.feedback_collector import (
    FeedbackCollector, FeedbackItem, FeedbackType, FeedbackRating
)
from src.feedback.feedback_analyzer import FeedbackAnalyzer
from src.feedback.agent_improver import AgentImprover, ImprovementAction
from src.feedback.feedback_database import FeedbackDatabase

def test_feedback_collector():
    """Test the feedback collector functionality."""
    print("🧪 Testing Feedback Collector")
    print("="*50)
    
    try:
        # Initialize collector
        collector = FeedbackCollector(user_id="test_user")
        print(f"✅ Feedback collector initialized")
        print(f"   User ID: {collector.user_id}")
        print(f"   Session ID: {collector.session_id}")
        
        # Test automatic feedback collection
        user_message = "compose an email to john@example.com"
        agent_response = "I'll help you compose an email to john@example.com. Please provide the subject and body content."
        
        feedback_item = collector.collect_response_feedback(
            user_message=user_message,
            agent_response=agent_response,
            expected_intent="email",
            actual_intent="email",
            expected_action="compose_email",
            actual_action="compose_email"
        )
        
        print(f"✅ Automatic feedback collected")
        print(f"   Feedback ID: {feedback_item.id}")
        print(f"   Rating: {feedback_item.rating.name}")
        print(f"   Comments: {feedback_item.comments[:100]}...")
        print(f"   Suggestions: {len(feedback_item.improvement_suggestions)} suggestions")
        
        # Test explicit feedback collection
        explicit_feedback = collector.collect_explicit_feedback(
            feedback_type=FeedbackType.HELPFULNESS,
            rating=FeedbackRating.GOOD,
            user_message="send email to team",
            agent_response="I'll help you send an email to the team. What would you like to include?",
            comments="Response was helpful but could be more specific about team members."
        )
        
        print(f"✅ Explicit feedback collected")
        print(f"   Feedback ID: {explicit_feedback.id}")
        print(f"   Type: {explicit_feedback.feedback_type.value}")
        print(f"   Rating: {explicit_feedback.rating.name}")
        
        # Test feedback summary
        summary = collector.get_feedback_summary()
        print(f"✅ Feedback summary generated")
        print(f"   Total Feedback: {summary['total_feedback']}")
        print(f"   Average Rating: {summary['average_rating']:.2f}")
        print(f"   Feedback Types: {summary['feedback_types']}")
        
        # Test feedback export
        json_export = collector.export_feedback(format="json")
        print(f"✅ Feedback exported to JSON ({len(json_export)} characters)")
        
        return True
        
    except Exception as e:
        print(f"❌ Feedback collector test failed: {e}")
        return False

def test_feedback_analyzer():
    """Test the feedback analyzer functionality."""
    print("\n🧪 Testing Feedback Analyzer")
    print("="*50)
    
    try:
        # Initialize analyzer
        analyzer = FeedbackAnalyzer()
        print(f"✅ Feedback analyzer initialized")
        
        # Create sample feedback items
        feedback_items = [
            FeedbackItem(
                id="test_001",
                user_id="test_user",
                session_id="session_123",
                timestamp=datetime.now(),
                feedback_type=FeedbackType.RESPONSE_QUALITY,
                rating=FeedbackRating.GOOD,
                user_message="compose email to john",
                agent_response="I'll help you compose an email to john. Please provide the subject and content.",
                expected_intent="email",
                actual_intent="email",
                expected_action="compose_email",
                actual_action="compose_email"
            ),
            FeedbackItem(
                id="test_002",
                user_id="test_user",
                session_id="session_123",
                timestamp=datetime.now(),
                feedback_type=FeedbackType.RESPONSE_QUALITY,
                rating=FeedbackRating.POOR,
                user_message="search emails",
                agent_response="I can help with that.",
                expected_intent="email",
                actual_intent="email",
                expected_action="search_emails",
                actual_action="general_response"
            ),
            FeedbackItem(
                id="test_003",
                user_id="test_user",
                session_id="session_123",
                timestamp=datetime.now(),
                feedback_type=FeedbackType.HELPFULNESS,
                rating=FeedbackRating.EXCELLENT,
                user_message="email summary",
                agent_response="You have 15 unread emails, 3 urgent, and 2 from your boss. Would you like me to show you the details?",
                expected_intent="email",
                actual_intent="email",
                expected_action="email_summary",
                actual_action="email_summary"
            )
        ]
        
        # Analyze feedback patterns
        analysis = analyzer.analyze_feedback_patterns(feedback_items)
        print(f"✅ Feedback analysis completed")
        print(f"   Total Items: {analysis['total_items']}")
        print(f"   Average Rating: {analysis['average_rating']:.2f}")
        print(f"   Rating Distribution: {analysis['rating_distribution']}")
        print(f"   Insights: {len(analysis['insights'])} insights")
        print(f"   Recommendations: {len(analysis['recommendations'])} recommendations")
        
        # Test improvement report generation
        report = analyzer.generate_improvement_report(feedback_items)
        print(f"✅ Improvement report generated")
        print(f"   Executive Summary: {report['report']['executive_summary'][:100]}...")
        print(f"   Key Findings: {len(report['report']['key_findings'])} findings")
        print(f"   Priority Areas: {len(report['report']['priority_areas'])} areas")
        print(f"   Action Items: {len(report['report']['action_items'])} items")
        
        return True
        
    except Exception as e:
        print(f"❌ Feedback analyzer test failed: {e}")
        return False

def test_agent_improver():
    """Test the agent improver functionality."""
    print("\n🧪 Testing Agent Improver")
    print("="*50)
    
    try:
        # Initialize improver
        improver = AgentImprover(user_id="test_user")
        print(f"✅ Agent improver initialized")
        print(f"   User ID: {improver.user_id}")
        
        # Create sample feedback items
        feedback_items = [
            FeedbackItem(
                id="improve_001",
                user_id="test_user",
                session_id="session_123",
                timestamp=datetime.now(),
                feedback_type=FeedbackType.RESPONSE_QUALITY,
                rating=FeedbackRating.POOR,
                user_message="compose email",
                agent_response="I can help with that.",
                expected_intent="email",
                actual_intent="email",
                expected_action="compose_email",
                actual_action="general_response"
            ),
            FeedbackItem(
                id="improve_002",
                user_id="test_user",
                session_id="session_123",
                timestamp=datetime.now(),
                feedback_type=FeedbackType.INTENT_DETECTION,
                rating=FeedbackRating.FAIR,
                user_message="send email to team about project update",
                agent_response="I'll help you send an email to the team about the project update.",
                expected_intent="email",
                actual_intent="email",
                expected_action="compose_email",
                actual_action="compose_email"
            )
        ]
        
        # Generate improvement actions
        actions = improver.generate_improvement_actions(feedback_items)
        print(f"✅ Improvement actions generated")
        print(f"   Total Actions: {len(actions)}")
        
        for action in actions:
            print(f"   - {action.action_type}: {action.description}")
            print(f"     Priority: {action.priority}, Target: {action.target_component}")
        
        # Test improvement implementation
        if actions:
            test_action = actions[0]
            print(f"\n🧪 Testing improvement implementation for: {test_action.description}")
            
            success = improver.implement_improvement(test_action)
            print(f"   Implementation Success: {success}")
            print(f"   Action Status: {test_action.status}")
        
        # Test improvement summary
        summary = improver.get_improvement_summary()
        print(f"✅ Improvement summary generated")
        print(f"   Total Actions: {summary['total_actions']}")
        print(f"   Completed Actions: {summary['completed_actions']}")
        print(f"   Success Rate: {summary['success_rate']:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent improver test failed: {e}")
        return False

def test_feedback_database():
    """Test the feedback database functionality."""
    print("\n🧪 Testing Feedback Database")
    print("="*50)
    
    try:
        # Initialize database
        db = FeedbackDatabase()
        print(f"✅ Feedback database initialized")
        
        # Create sample feedback item
        feedback_item = FeedbackItem(
            id="db_test_001",
            user_id="test_user",
            session_id="session_123",
            timestamp=datetime.now(),
            feedback_type=FeedbackType.RESPONSE_QUALITY,
            rating=FeedbackRating.GOOD,
            user_message="test message",
            agent_response="test response",
            expected_intent="email",
            actual_intent="email"
        )
        
        # Test saving feedback item
        save_success = db.save_feedback_item(feedback_item)
        print(f"✅ Feedback item saved: {save_success}")
        
        # Test retrieving user feedback
        user_feedback = db.get_user_feedback("test_user", limit=10)
        print(f"✅ User feedback retrieved: {len(user_feedback)} items")
        
        # Test feedback summary
        summary = db.get_feedback_summary("test_user")
        print(f"✅ Database feedback summary")
        print(f"   Total Feedback: {summary['total_feedback']}")
        print(f"   Average Rating: {summary['average_rating']:.2f}")
        
        # Test improvement action storage
        action = ImprovementAction(
            id="db_action_001",
            action_type="test_improvement",
            description="Test improvement action",
            priority="medium",
            target_component="test_component",
            implementation_details={"test": "data"},
            expected_impact="Test impact",
            created_at=datetime.now()
        )
        
        action_save_success = db.save_improvement_action(action)
        print(f"✅ Improvement action saved: {action_save_success}")
        
        # Test retrieving improvement actions
        actions = db.get_improvement_actions(user_id="test_user")
        print(f"✅ Improvement actions retrieved: {len(actions)} items")
        
        return True
        
    except Exception as e:
        print(f"❌ Feedback database test failed: {e}")
        return False

def test_integrated_workflow():
    """Test the complete human-in-the-loop workflow."""
    print("\n🧪 Testing Integrated Human-in-the-Loop Workflow")
    print("="*50)
    
    try:
        # Initialize all components
        collector = FeedbackCollector(user_id="workflow_user")
        analyzer = FeedbackAnalyzer()
        improver = AgentImprover(user_id="workflow_user")
        db = FeedbackDatabase()
        
        print(f"✅ All components initialized")
        
        # Step 1: Collect feedback
        print(f"\n📝 Step 1: Collecting feedback...")
        
        feedback_items = []
        test_cases = [
            ("compose email to john", "I'll help you compose an email to john. Please provide the subject and content.", "email", "email"),
            ("search emails from boss", "I can help you search for emails from your boss.", "email", "email"),
            ("email summary", "You have 10 unread emails. Would you like me to show you the details?", "email", "email")
        ]
        
        for i, (user_msg, agent_resp, exp_intent, act_intent) in enumerate(test_cases):
            feedback_item = collector.collect_response_feedback(
                user_message=user_msg,
                agent_response=agent_resp,
                expected_intent=exp_intent,
                actual_intent=act_intent
            )
            feedback_items.append(feedback_item)
            
            # Save to database
            db.save_feedback_item(feedback_item)
            print(f"   ✅ Feedback {i+1} collected and saved")
        
        # Step 2: Analyze feedback
        print(f"\n📊 Step 2: Analyzing feedback...")
        analysis = analyzer.analyze_feedback_patterns(feedback_items)
        print(f"   ✅ Analysis completed")
        print(f"   Average Rating: {analysis['average_rating']:.2f}")
        print(f"   Insights: {len(analysis['insights'])} insights")
        
        # Step 3: Generate improvements
        print(f"\n🔧 Step 3: Generating improvements...")
        actions = improver.generate_improvement_actions(feedback_items)
        print(f"   ✅ {len(actions)} improvement actions generated")
        
        for action in actions:
            db.save_improvement_action(action)
            print(f"   - {action.description}")
        
        # Step 4: Test improvements
        print(f"\n🧪 Step 4: Testing improvements...")
        if actions:
            test_action = actions[0]
            result = improver.test_improvement(test_action, ["test case 1", "test case 2"])
            print(f"   ✅ Improvement test completed")
            print(f"   Success: {result.success}")
            print(f"   Improvement: {result.improvement_percentage:.1f}%")
            
            # Save result
            db.save_improvement_result(result)
        
        # Step 5: Generate final report
        print(f"\n📋 Step 5: Generating final report...")
        report = analyzer.generate_improvement_report(feedback_items)
        print(f"   ✅ Final report generated")
        print(f"   Executive Summary: {report['report']['executive_summary'][:100]}...")
        
        print(f"\n🎉 Integrated workflow completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Integrated workflow test failed: {e}")
        return False

def main():
    """Run all human-in-the-loop tests."""
    print("🚀 HUMAN-IN-THE-LOOP FEEDBACK SYSTEM TESTS")
    print("="*60)
    print(f"📅 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check environment
    print("🔧 Environment Check:")
    print(f"   OpenAI API Key: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Missing'}")
    print(f"   AWS Access Key: {'✅ Set' if os.getenv('AWS_ACCESS_KEY_ID') else '❌ Missing'}")
    print()
    
    # Run tests
    tests = [
        ("Feedback Collector", test_feedback_collector),
        ("Feedback Analyzer", test_feedback_analyzer),
        ("Agent Improver", test_agent_improver),
        ("Feedback Database", test_feedback_database),
        ("Integrated Workflow", test_integrated_workflow),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"🧪 Running: {test_name}")
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
        print()
    
    # Summary
    print("="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"   Total Tests: {total}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {total - passed}")
    print(f"   Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All tests passed! Human-in-the-loop system is ready.")
        print("\n🚀 Next Steps:")
        print("   1. Integrate feedback collection into the main application")
        print("   2. Set up automated improvement workflows")
        print("   3. Monitor improvement metrics over time")
        print("   4. Implement user feedback interface")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
    
    print(f"\n📅 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 