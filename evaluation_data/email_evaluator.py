"""
Email Assistant Evaluator

This module provides evaluation capabilities for the email assistant agent using
LLM-as-a-judge approach and automated metrics.

Following the LangChain agents-from-scratch evaluation pattern.
"""

import os
import json
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict

from langchain_openai import ChatOpenAI
from langsmith import Client

from .email_dataset import EmailTestCase, get_email_dataset
from src.agents.email.email_agent import EmailAgent
from src.memory.memory_utils import MemoryUtils

@dataclass
class EvaluationResult:
    """Represents the result of a single evaluation."""
    test_case_id: str
    user_message: str
    expected_intent: str
    actual_intent: str
    expected_action: str
    actual_action: str
    agent_response: str
    intent_correct: bool
    action_correct: bool
    response_quality_score: float
    response_contains_expected: bool
    response_not_contains_unexpected: bool
    overall_score: float
    evaluation_time: float
    error_message: Optional[str] = None

@dataclass
class EvaluationSummary:
    """Summary of evaluation results."""
    total_tests: int
    passed_tests: int
    failed_tests: int
    intent_accuracy: float
    action_accuracy: float
    response_quality_avg: float
    overall_accuracy: float
    category_breakdown: Dict[str, Dict[str, Any]]
    difficulty_breakdown: Dict[str, Dict[str, Any]]
    error_count: int
    evaluation_duration: float

class EmailEvaluator:
    """Evaluator for email assistant agent."""
    
    def __init__(self, user_id: str = "evaluation_user", use_langsmith: bool = True):
        """
        Initialize the email evaluator.
        
        Args:
            user_id: User ID for testing
            use_langsmith: Whether to use LangSmith for evaluation
        """
        self.user_id = user_id
        self.use_langsmith = use_langsmith
        self.email_agent = EmailAgent(user_id)
        self.dataset = get_email_dataset()
        
        # Initialize LLM for evaluation
        self.evaluation_llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.0,  # Deterministic evaluation
            tags=["remo", "email-evaluation"]
        )
        
        # Initialize LangSmith client if enabled
        self.langsmith_client = None
        if use_langsmith and os.getenv("LANGSMITH_API_KEY"):
            self.langsmith_client = Client()
    
    def evaluate_single_test_case(self, test_case: EmailTestCase) -> EvaluationResult:
        """
        Evaluate a single test case.
        
        Args:
            test_case: The test case to evaluate
            
        Returns:
            Evaluation result
        """
        start_time = time.time()
        
        try:
            # Get agent response
            agent_response = self.email_agent.process(test_case.user_message)
            
            # Detect actual intent
            actual_intent, intent_details = MemoryUtils.detect_email_intent(test_case.user_message)
            actual_action = intent_details.get("action", "unknown") if actual_intent else "none"
            
            # Check intent correctness
            intent_correct = actual_intent == test_case.expected_intent
            
            # Check action correctness
            action_correct = actual_action == test_case.expected_action
            
            # Evaluate response quality using LLM-as-a-judge
            response_quality_score = self._evaluate_response_quality(
                test_case, agent_response, intent_correct, action_correct
            )
            
            # Check response content
            response_contains_expected = self._check_response_content(
                agent_response, test_case.expected_response_contains
            )
            
            response_not_contains_unexpected = True
            if test_case.expected_response_not_contains:
                response_not_contains_unexpected = not self._check_response_content(
                    agent_response, test_case.expected_response_not_contains
                )
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(
                intent_correct, action_correct, response_quality_score,
                response_contains_expected, response_not_contains_unexpected
            )
            
            evaluation_time = time.time() - start_time
            
            return EvaluationResult(
                test_case_id=test_case.id,
                user_message=test_case.user_message,
                expected_intent=test_case.expected_intent,
                actual_intent=actual_intent,
                expected_action=test_case.expected_action,
                actual_action=actual_action,
                agent_response=agent_response,
                intent_correct=intent_correct,
                action_correct=action_correct,
                response_quality_score=response_quality_score,
                response_contains_expected=response_contains_expected,
                response_not_contains_unexpected=response_not_contains_unexpected,
                overall_score=overall_score,
                evaluation_time=evaluation_time
            )
            
        except Exception as e:
            evaluation_time = time.time() - start_time
            return EvaluationResult(
                test_case_id=test_case.id,
                user_message=test_case.user_message,
                expected_intent=test_case.expected_intent,
                actual_intent="error",
                expected_action=test_case.expected_action,
                actual_action="error",
                agent_response="",
                intent_correct=False,
                action_correct=False,
                response_quality_score=0.0,
                response_contains_expected=False,
                response_not_contains_unexpected=False,
                overall_score=0.0,
                evaluation_time=evaluation_time,
                error_message=str(e)
            )
    
    def _evaluate_response_quality(self, test_case: EmailTestCase, response: str, 
                                 intent_correct: bool, action_correct: bool) -> float:
        """
        Evaluate response quality using LLM-as-a-judge.
        
        Args:
            test_case: The test case
            response: The agent's response
            intent_correct: Whether intent detection was correct
            action_correct: Whether action detection was correct
            
        Returns:
            Quality score (0.0 to 1.0)
        """
        try:
            prompt = f"""
You are evaluating an email assistant's response to a user query.

User Query: "{test_case.user_message}"
Expected Intent: {test_case.expected_intent}
Expected Action: {test_case.expected_action}
Agent Response: "{response}"

Evaluation Criteria:
1. **Intent Detection**: Was the correct intent detected? ({intent_correct})
2. **Action Detection**: Was the correct action identified? ({action_correct})
3. **Response Relevance**: Does the response address the user's request?
4. **Response Completeness**: Does the response provide necessary information?
5. **Response Clarity**: Is the response clear and understandable?
6. **Response Helpfulness**: Is the response helpful to the user?

Expected Response Elements: {test_case.expected_response_contains}

Rate the response quality on a scale of 0.0 to 1.0, where:
- 0.0: Completely incorrect or unhelpful
- 0.5: Partially correct but missing key elements
- 1.0: Perfect response that fully addresses the request

Provide only the numerical score (e.g., 0.85):
"""
            
            result = self.evaluation_llm.invoke(prompt)
            score_text = result.content.strip()
            
            # Extract numerical score
            try:
                score = float(score_text)
                return max(0.0, min(1.0, score))  # Clamp between 0 and 1
            except ValueError:
                # Fallback scoring based on correctness
                if intent_correct and action_correct:
                    return 0.8
                elif intent_correct or action_correct:
                    return 0.5
                else:
                    return 0.2
                    
        except Exception as e:
            print(f"Error in response quality evaluation: {e}")
            # Fallback scoring
            if intent_correct and action_correct:
                return 0.8
            elif intent_correct or action_correct:
                return 0.5
            else:
                return 0.2
    
    def _check_response_content(self, response: str, expected_terms: List[str]) -> bool:
        """
        Check if response contains expected terms.
        
        Args:
            response: The agent's response
            expected_terms: List of terms that should be present
            
        Returns:
            True if all expected terms are found
        """
        response_lower = response.lower()
        return all(term.lower() in response_lower for term in expected_terms)
    
    def _calculate_overall_score(self, intent_correct: bool, action_correct: bool,
                               response_quality: float, contains_expected: bool,
                               not_contains_unexpected: bool) -> float:
        """
        Calculate overall evaluation score.
        
        Args:
            intent_correct: Whether intent detection was correct
            action_correct: Whether action detection was correct
            response_quality: Response quality score
            contains_expected: Whether response contains expected terms
            not_contains_unexpected: Whether response doesn't contain unexpected terms
            
        Returns:
            Overall score (0.0 to 1.0)
        """
        # Weighted scoring
        intent_weight = 0.3
        action_weight = 0.3
        quality_weight = 0.2
        content_weight = 0.2
        
        intent_score = 1.0 if intent_correct else 0.0
        action_score = 1.0 if action_correct else 0.0
        content_score = 1.0 if (contains_expected and not_contains_unexpected) else 0.0
        
        overall_score = (
            intent_score * intent_weight +
            action_score * action_weight +
            response_quality * quality_weight +
            content_score * content_weight
        )
        
        return overall_score
    
    def evaluate_all_test_cases(self) -> List[EvaluationResult]:
        """
        Evaluate all test cases in the dataset.
        
        Returns:
            List of evaluation results
        """
        results = []
        test_cases = self.dataset.get_all_test_cases()
        
        print(f"🧪 Evaluating {len(test_cases)} test cases...")
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"  [{i}/{len(test_cases)}] Evaluating: {test_case.id}")
            result = self.evaluate_single_test_case(test_case)
            results.append(result)
            
            # Small delay to avoid rate limiting
            time.sleep(0.1)
        
        return results
    
    def evaluate_by_category(self, category: str) -> List[EvaluationResult]:
        """
        Evaluate test cases by category.
        
        Args:
            category: Category to evaluate
            
        Returns:
            List of evaluation results
        """
        test_cases = self.dataset.get_test_cases_by_category(category)
        results = []
        
        print(f"🧪 Evaluating {len(test_cases)} {category} test cases...")
        
        for test_case in test_cases:
            result = self.evaluate_single_test_case(test_case)
            results.append(result)
            time.sleep(0.1)
        
        return results
    
    def evaluate_by_difficulty(self, difficulty: str) -> List[EvaluationResult]:
        """
        Evaluate test cases by difficulty.
        
        Args:
            difficulty: Difficulty level to evaluate
            
        Returns:
            List of evaluation results
        """
        test_cases = self.dataset.get_test_cases_by_difficulty(difficulty)
        results = []
        
        print(f"🧪 Evaluating {len(test_cases)} {difficulty} difficulty test cases...")
        
        for test_case in test_cases:
            result = self.evaluate_single_test_case(test_case)
            results.append(result)
            time.sleep(0.1)
        
        return results
    
    def generate_evaluation_summary(self, results: List[EvaluationResult]) -> EvaluationSummary:
        """
        Generate a summary of evaluation results.
        
        Args:
            results: List of evaluation results
            
        Returns:
            Evaluation summary
        """
        if not results:
            return EvaluationSummary(
                total_tests=0, passed_tests=0, failed_tests=0,
                intent_accuracy=0.0, action_accuracy=0.0, response_quality_avg=0.0,
                overall_accuracy=0.0, category_breakdown={}, difficulty_breakdown={},
                error_count=0, evaluation_duration=0.0
            )
        
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.overall_score >= 0.7)
        failed_tests = total_tests - passed_tests
        error_count = sum(1 for r in results if r.error_message)
        
        # Calculate accuracies
        intent_correct = sum(1 for r in results if r.intent_correct)
        action_correct = sum(1 for r in results if r.action_correct)
        intent_accuracy = intent_correct / total_tests
        action_accuracy = action_correct / total_tests
        
        # Calculate response quality average
        response_quality_avg = sum(r.response_quality_score for r in results) / total_tests
        
        # Calculate overall accuracy
        overall_accuracy = sum(r.overall_score for r in results) / total_tests
        
        # Calculate evaluation duration
        evaluation_duration = sum(r.evaluation_time for r in results)
        
        # Category breakdown
        category_breakdown = {}
        for result in results:
            test_case = self.dataset.get_test_case_by_id(result.test_case_id)
            category = test_case.category
            if category not in category_breakdown:
                category_breakdown[category] = {
                    "total": 0, "passed": 0, "accuracy": 0.0, "avg_score": 0.0
                }
            
            category_breakdown[category]["total"] += 1
            if result.overall_score >= 0.7:
                category_breakdown[category]["passed"] += 1
        
        # Calculate category accuracies
        for category in category_breakdown:
            total = category_breakdown[category]["total"]
            passed = category_breakdown[category]["passed"]
            category_breakdown[category]["accuracy"] = passed / total if total > 0 else 0.0
            
            # Calculate average score for category
            category_results = [r for r in results 
                              if self.dataset.get_test_case_by_id(r.test_case_id).category == category]
            avg_score = sum(r.overall_score for r in category_results) / len(category_results) if category_results else 0.0
            category_breakdown[category]["avg_score"] = avg_score
        
        # Difficulty breakdown
        difficulty_breakdown = {}
        for result in results:
            test_case = self.dataset.get_test_case_by_id(result.test_case_id)
            difficulty = test_case.difficulty
            if difficulty not in difficulty_breakdown:
                difficulty_breakdown[difficulty] = {
                    "total": 0, "passed": 0, "accuracy": 0.0, "avg_score": 0.0
                }
            
            difficulty_breakdown[difficulty]["total"] += 1
            if result.overall_score >= 0.7:
                difficulty_breakdown[difficulty]["passed"] += 1
        
        # Calculate difficulty accuracies
        for difficulty in difficulty_breakdown:
            total = difficulty_breakdown[difficulty]["total"]
            passed = difficulty_breakdown[difficulty]["passed"]
            difficulty_breakdown[difficulty]["accuracy"] = passed / total if total > 0 else 0.0
            
            # Calculate average score for difficulty
            difficulty_results = [r for r in results 
                                if self.dataset.get_test_case_by_id(r.test_case_id).difficulty == difficulty]
            avg_score = sum(r.overall_score for r in difficulty_results) / len(difficulty_results) if difficulty_results else 0.0
            difficulty_breakdown[difficulty]["avg_score"] = avg_score
        
        return EvaluationSummary(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            intent_accuracy=intent_accuracy,
            action_accuracy=action_accuracy,
            response_quality_avg=response_quality_avg,
            overall_accuracy=overall_accuracy,
            category_breakdown=category_breakdown,
            difficulty_breakdown=difficulty_breakdown,
            error_count=error_count,
            evaluation_duration=evaluation_duration
        )
    
    def save_evaluation_results(self, results: List[EvaluationResult], 
                              summary: EvaluationSummary, filename: str = None) -> str:
        """
        Save evaluation results to a JSON file.
        
        Args:
            results: List of evaluation results
            summary: Evaluation summary
            filename: Optional filename
            
        Returns:
            Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"email_evaluation_results_{timestamp}.json"
        
        # Create results directory if it doesn't exist
        os.makedirs("evaluation_results", exist_ok=True)
        filepath = os.path.join("evaluation_results", filename)
        
        # Convert results to dictionaries
        results_dict = [asdict(result) for result in results]
        summary_dict = asdict(summary)
        
        # Save to file
        with open(filepath, 'w') as f:
            json.dump({
                "evaluation_timestamp": datetime.now().isoformat(),
                "summary": summary_dict,
                "results": results_dict
            }, f, indent=2)
        
        print(f"✅ Evaluation results saved to: {filepath}")
        return filepath
    
    def print_evaluation_summary(self, summary: EvaluationSummary):
        """
        Print a formatted evaluation summary.
        
        Args:
            summary: Evaluation summary
        """
        print("\n" + "="*60)
        print("📊 EMAIL ASSISTANT EVALUATION SUMMARY")
        print("="*60)
        
        print(f"📈 Overall Results:")
        print(f"   Total Tests: {summary.total_tests}")
        print(f"   Passed Tests: {summary.passed_tests}")
        print(f"   Failed Tests: {summary.failed_tests}")
        print(f"   Overall Accuracy: {summary.overall_accuracy:.2%}")
        print(f"   Evaluation Duration: {summary.evaluation_duration:.2f}s")
        
        print(f"\n🎯 Accuracy Metrics:")
        print(f"   Intent Detection: {summary.intent_accuracy:.2%}")
        print(f"   Action Detection: {summary.action_accuracy:.2%}")
        print(f"   Response Quality: {summary.response_quality_avg:.2%}")
        
        print(f"\n📂 Category Breakdown:")
        for category, stats in summary.category_breakdown.items():
            print(f"   {category.title()}: {stats['passed']}/{stats['total']} "
                  f"({stats['accuracy']:.2%}) - Avg Score: {stats['avg_score']:.3f}")
        
        print(f"\n📊 Difficulty Breakdown:")
        for difficulty, stats in summary.difficulty_breakdown.items():
            print(f"   {difficulty.title()}: {stats['passed']}/{stats['total']} "
                  f"({stats['accuracy']:.2%}) - Avg Score: {stats['avg_score']:.3f}")
        
        if summary.error_count > 0:
            print(f"\n⚠️  Errors: {summary.error_count}")
        
        print("="*60)

# Convenience functions
def run_email_evaluation(user_id: str = "evaluation_user", 
                        save_results: bool = True) -> Tuple[List[EvaluationResult], EvaluationSummary]:
    """
    Run a complete email assistant evaluation.
    
    Args:
        user_id: User ID for testing
        save_results: Whether to save results to file
        
    Returns:
        Tuple of (results, summary)
    """
    evaluator = EmailEvaluator(user_id)
    
    print("�� Starting Email Assistant Evaluation")
    print("="*50)
    
    # Get dataset statistics
    stats = evaluator.dataset.get_statistics()
    print(f"📊 Dataset Statistics:")
    print(f"   Total Test Cases: {stats['total_test_cases']}")
    print(f"   Categories: {stats['categories_count']}")
    print(f"   Difficulties: {stats['difficulties_count']}")
    print(f"   Intents: {stats['intents_count']}")
    
    # Run evaluation
    results = evaluator.evaluate_all_test_cases()
    summary = evaluator.generate_evaluation_summary(results)
    
    # Print summary
    evaluator.print_evaluation_summary(summary)
    
    # Save results if requested
    if save_results:
        evaluator.save_evaluation_results(results, summary)
    
    return results, summary

def run_category_evaluation(category: str, user_id: str = "evaluation_user") -> Tuple[List[EvaluationResult], EvaluationSummary]:
    """
    Run evaluation for a specific category.
    
    Args:
        category: Category to evaluate
        user_id: User ID for testing
        
    Returns:
        Tuple of (results, summary)
    """
    evaluator = EmailEvaluator(user_id)
    results = evaluator.evaluate_by_category(category)
    summary = evaluator.generate_evaluation_summary(results)
    
    print(f"\n📊 {category.title()} Category Evaluation Results:")
    evaluator.print_evaluation_summary(summary)
    
    return results, summary
