#!/usr/bin/env python3
"""
Test script for Email Assistant Evaluation System

This script tests the evaluation framework for the email assistant agent,
including dataset creation, evaluator functionality, and result analysis.

Following the LangChain agents-from-scratch evaluation pattern.
"""

import os
import sys
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from evaluation_data.email_dataset import (
    get_email_dataset, get_test_cases, get_composition_tests,
    get_search_tests, get_management_tests, get_easy_tests
)
from evaluation_data.email_evaluator import (
    EmailEvaluator, run_email_evaluation, run_category_evaluation,
    EvaluationResult, EvaluationSummary
)

def test_dataset_creation():
    """Test the email evaluation dataset creation."""
    print("🧪 Testing Email Evaluation Dataset Creation")
    print("="*50)
    
    try:
        # Get dataset
        dataset = get_email_dataset()
        print(f"✅ Dataset created successfully")
        
        # Get statistics
        stats = dataset.get_statistics()
        print(f"📊 Dataset Statistics:")
        print(f"   Total Test Cases: {stats['total_test_cases']}")
        print(f"   Categories: {stats['categories']}")
        print(f"   Difficulties: {stats['difficulties']}")
        print(f"   Intents: {stats['intents']}")
        
        # Test category filtering
        composition_tests = get_composition_tests()
        search_tests = get_search_tests()
        management_tests = get_management_tests()
        
        print(f"\n📂 Category Breakdown:")
        print(f"   Composition Tests: {len(composition_tests)}")
        print(f"   Search Tests: {len(search_tests)}")
        print(f"   Management Tests: {len(management_tests)}")
        
        # Test difficulty filtering
        easy_tests = get_easy_tests()
        print(f"   Easy Tests: {len(easy_tests)}")
        
        # Test individual test case access
        test_case = dataset.get_test_case_by_id("compose_001")
        print(f"\n📝 Sample Test Case:")
        print(f"   ID: {test_case.id}")
        print(f"   Message: {test_case.user_message}")
        print(f"   Expected Intent: {test_case.expected_intent}")
        print(f"   Expected Action: {test_case.expected_action}")
        print(f"   Category: {test_case.category}")
        print(f"   Difficulty: {test_case.difficulty}")
        
        return True
        
    except Exception as e:
        print(f"❌ Dataset creation failed: {e}")
        return False

def test_evaluator_initialization():
    """Test the email evaluator initialization."""
    print("\n🧪 Testing Email Evaluator Initialization")
    print("="*50)
    
    try:
        # Initialize evaluator
        evaluator = EmailEvaluator(user_id="test_user")
        print(f"✅ Evaluator initialized successfully")
        print(f"   User ID: {evaluator.user_id}")
        print(f"   Dataset loaded: {len(evaluator.dataset.get_all_test_cases())} test cases")
        print(f"   LangSmith enabled: {evaluator.use_langsmith}")
        
        return True
        
    except Exception as e:
        print(f"❌ Evaluator initialization failed: {e}")
        return False

def test_single_evaluation():
    """Test single test case evaluation."""
    print("\n🧪 Testing Single Test Case Evaluation")
    print("="*50)
    
    try:
        # Initialize evaluator
        evaluator = EmailEvaluator(user_id="test_user")
        
        # Get a simple test case
        test_case = evaluator.dataset.get_test_case_by_id("compose_001")
        print(f"📝 Evaluating test case: {test_case.id}")
        print(f"   Message: {test_case.user_message}")
        
        # Run evaluation
        result = evaluator.evaluate_single_test_case(test_case)
        
        print(f"\n📊 Evaluation Results:")
        print(f"   Intent Correct: {result.intent_correct}")
        print(f"   Action Correct: {result.action_correct}")
        print(f"   Response Quality Score: {result.response_quality_score:.3f}")
        print(f"   Overall Score: {result.overall_score:.3f}")
        print(f"   Evaluation Time: {result.evaluation_time:.3f}s")
        
        if result.error_message:
            print(f"   Error: {result.error_message}")
        
        return True
        
    except Exception as e:
        print(f"❌ Single evaluation failed: {e}")
        return False

def test_category_evaluation():
    """Test category-based evaluation."""
    print("\n🧪 Testing Category-Based Evaluation")
    print("="*50)
    
    try:
        # Test composition category
        print("📧 Testing Composition Category...")
        results, summary = run_category_evaluation("composition", "test_user")
        
        print(f"✅ Composition evaluation completed")
        print(f"   Total Tests: {summary.total_tests}")
        print(f"   Passed Tests: {summary.passed_tests}")
        print(f"   Overall Accuracy: {summary.overall_accuracy:.2%}")
        
        return True
        
    except Exception as e:
        print(f"❌ Category evaluation failed: {e}")
        return False

def test_evaluation_summary():
    """Test evaluation summary generation."""
    print("\n🧪 Testing Evaluation Summary Generation")
    print("="*50)
    
    try:
        # Initialize evaluator
        evaluator = EmailEvaluator(user_id="test_user")
        
        # Get a few test cases
        test_cases = evaluator.dataset.get_test_cases_by_category("composition")[:3]
        print(f"📝 Evaluating {len(test_cases)} test cases...")
        
        # Run evaluations
        results = []
        for test_case in test_cases:
            result = evaluator.evaluate_single_test_case(test_case)
            results.append(result)
        
        # Generate summary
        summary = evaluator.generate_evaluation_summary(results)
        
        print(f"✅ Summary generated successfully")
        print(f"   Total Tests: {summary.total_tests}")
        print(f"   Passed Tests: {summary.passed_tests}")
        print(f"   Intent Accuracy: {summary.intent_accuracy:.2%}")
        print(f"   Action Accuracy: {summary.action_accuracy:.2%}")
        print(f"   Response Quality Avg: {summary.response_quality_avg:.3f}")
        print(f"   Overall Accuracy: {summary.overall_accuracy:.2%}")
        
        # Print detailed summary
        evaluator.print_evaluation_summary(summary)
        
        return True
        
    except Exception as e:
        print(f"❌ Summary generation failed: {e}")
        return False

def test_result_saving():
    """Test evaluation result saving."""
    print("\n🧪 Testing Evaluation Result Saving")
    print("="*50)
    
    try:
        # Initialize evaluator
        evaluator = EmailEvaluator(user_id="test_user")
        
        # Get a few test cases
        test_cases = evaluator.dataset.get_test_cases_by_category("composition")[:2]
        
        # Run evaluations
        results = []
        for test_case in test_cases:
            result = evaluator.evaluate_single_test_case(test_case)
            results.append(result)
        
        # Generate summary
        summary = evaluator.generate_evaluation_summary(results)
        
        # Save results
        filename = f"test_evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = evaluator.save_evaluation_results(results, summary, filename)
        
        print(f"✅ Results saved to: {filepath}")
        
        # Verify file exists and is valid JSON
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            print(f"✅ File verification successful")
            print(f"   File size: {os.path.getsize(filepath)} bytes")
            print(f"   Contains summary: {'summary' in data}")
            print(f"   Contains results: {'results' in data}")
            print(f"   Results count: {len(data['results'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Result saving failed: {e}")
        return False

def test_full_evaluation():
    """Test full evaluation with a small subset."""
    print("\n🧪 Testing Full Evaluation (Small Subset)")
    print("="*50)
    
    try:
        # Run evaluation on easy tests only
        print("🚀 Running evaluation on easy test cases...")
        
        evaluator = EmailEvaluator(user_id="test_user")
        easy_test_cases = evaluator.dataset.get_test_cases_by_difficulty("easy")
        
        print(f"📊 Found {len(easy_test_cases)} easy test cases")
        
        # Limit to first 5 for testing
        test_cases = easy_test_cases[:5]
        print(f"🧪 Evaluating {len(test_cases)} test cases...")
        
        results = []
        for i, test_case in enumerate(test_cases, 1):
            print(f"  [{i}/{len(test_cases)}] Evaluating: {test_case.id}")
            result = evaluator.evaluate_single_test_case(test_case)
            results.append(result)
        
        # Generate and print summary
        summary = evaluator.generate_evaluation_summary(results)
        evaluator.print_evaluation_summary(summary)
        
        # Save results
        evaluator.save_evaluation_results(results, summary)
        
        return True
        
    except Exception as e:
        print(f"❌ Full evaluation failed: {e}")
        return False

def main():
    """Run all evaluation tests."""
    print("🚀 EMAIL ASSISTANT EVALUATION SYSTEM TESTS")
    print("="*60)
    print(f"📅 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check environment
    print("🔧 Environment Check:")
    print(f"   OpenAI API Key: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Missing'}")
    print(f"   LangSmith API Key: {'✅ Set' if os.getenv('LANGSMITH_API_KEY') else '❌ Missing (optional)'}")
    print(f"   AWS Access Key: {'✅ Set' if os.getenv('AWS_ACCESS_KEY_ID') else '❌ Missing'}")
    print()
    
    # Run tests
    tests = [
        ("Dataset Creation", test_dataset_creation),
        ("Evaluator Initialization", test_evaluator_initialization),
        ("Single Evaluation", test_single_evaluation),
        ("Category Evaluation", test_category_evaluation),
        ("Summary Generation", test_evaluation_summary),
        ("Result Saving", test_result_saving),
        ("Full Evaluation", test_full_evaluation),
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
        print("\n🎉 All tests passed! Email evaluation system is ready.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
    
    print(f"\n📅 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 