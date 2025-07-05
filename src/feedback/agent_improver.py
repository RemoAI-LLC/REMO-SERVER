"""
Agent Improver

This module implements agent improvement strategies based on human feedback and evaluation results.
It provides mechanisms to iteratively improve the email assistant agent.

Following the LangChain agents-from-scratch human-in-the-loop pattern.
"""

import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

try:
    from langchain_aws import ChatBedrock
except ImportError:
    ChatBedrock = None
import boto3
import os

from .feedback_collector import FeedbackItem
from .feedback_analyzer import FeedbackAnalyzer
from src.agents.email.email_agent import EmailAgent

@dataclass
class ImprovementAction:
    """Represents an improvement action to be taken."""
    id: str
    action_type: str
    description: str
    priority: str  # high, medium, low
    target_component: str
    implementation_details: Dict[str, Any]
    expected_impact: str
    created_at: datetime
    status: str = "pending"  # pending, in_progress, completed, failed

@dataclass
class ImprovementResult:
    """Represents the result of an improvement action."""
    action_id: str
    success: bool
    before_metrics: Dict[str, float]
    after_metrics: Dict[str, float]
    improvement_percentage: float
    completed_at: datetime
    notes: Optional[str] = None

class AgentImprover:
    """Implements agent improvement strategies based on feedback."""
    
    def __init__(self, user_id: str = "default_user"):
        """
        Initialize the agent improver.
        
        Args:
            user_id: User ID for improvement tracking
        """
        self.user_id = user_id
        self.email_agent = EmailAgent(user_id)
        self.feedback_analyzer = FeedbackAnalyzer()
        self.improvement_actions: List[ImprovementAction] = []
        self.improvement_results: List[ImprovementResult] = []
        
        # Bedrock LLM initialization
        model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")
        region = os.getenv("AWS_REGION", "us-east-1")
        access_key = os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        temperature = 0.0
        if ChatBedrock:
            self.llm = ChatBedrock(
                model_id=model_id,
                region_name=region,
                model_kwargs={"temperature": temperature}
            )
        else:
            class BedrockLLM:
                def __init__(self, model_id, region, access_key, secret_key, temperature):
                    self.model_id = model_id
                    self.temperature = temperature
                    print(f"[BedrockLLM] Initializing with model_id={model_id}, region={region}")
                    self.client = boto3.client(
                        "bedrock-runtime",
                        region_name=region,
                        aws_access_key_id=access_key,
                        aws_secret_access_key=secret_key,
                    )
                def invoke(self, prompt):
                    messages = [{"role": "user", "content": [{"text": prompt}]}]
                    # Ensure content is a list of objects with 'text' for each message
                    for m in messages:
                        if isinstance(m.get("content"), str):
                            m["content"] = [{"text": m["content"]}]
                        elif isinstance(m.get("content"), list):
                            m["content"] = [c if isinstance(c, dict) else {"text": c} for c in m["content"]]
                    print(f"[BedrockLLM] Invoking model {self.model_id} with messages: {messages}")
                    body = {
                        "messages": messages
                    }
                    try:
                        response = self.client.invoke_model(
                            modelId=self.model_id,
                            body=json.dumps(body),
                            contentType="application/json",
                            accept="application/json"
                        )
                        result = json.loads(response["body"].read())
                        print(f"[BedrockLLM] Response: {str(result)[:200]}")
                        class Result:
                            def __init__(self, content):
                                self.content = content
                        return Result(result.get("completion") or result.get("output", ""))
                    except Exception as e:
                        print(f"[BedrockLLM] ERROR: {e}")
                        raise
            self.llm = BedrockLLM(model_id, region, access_key, secret_key, temperature)
    
    def generate_improvement_actions(self, feedback_items: List[FeedbackItem]) -> List[ImprovementAction]:
        """
        Generate improvement actions based on feedback analysis.
        
        Args:
            feedback_items: List of feedback items to analyze
            
        Returns:
            List of improvement actions
        """
        # Analyze feedback patterns
        analysis = self.feedback_analyzer.analyze_feedback_patterns(feedback_items)
        
        # Generate improvement actions using LLM
        actions = []
        
        # Intent detection improvements
        if "intent_patterns" in analysis and analysis["intent_patterns"]["intent_accuracy"]:
            intent_actions = self._generate_intent_improvements(analysis["intent_patterns"])
            actions.extend(intent_actions)
        
        # Response quality improvements
        if analysis["average_rating"] < 4.0:
            quality_actions = self._generate_quality_improvements(analysis)
            actions.extend(quality_actions)
        
        # Content relevance improvements
        content_actions = self._generate_content_improvements(analysis)
        actions.extend(content_actions)
        
        # Add actions to tracking
        for action in actions:
            self.improvement_actions.append(action)
        
        return actions
    
    def _generate_intent_improvements(self, intent_patterns: Dict[str, Any]) -> List[ImprovementAction]:
        """Generate improvements for intent detection."""
        actions = []
        
        for intent, data in intent_patterns["intent_accuracy"].items():
            if data["accuracy"] < 80.0:  # Below 80% accuracy
                action_id = f"intent_improve_{intent}_{int(time.time())}"
                
                action = ImprovementAction(
                    id=action_id,
                    action_type="intent_detection_improvement",
                    description=f"Improve intent detection for '{intent}' (current accuracy: {data['accuracy']:.1f}%)",
                    priority="high" if data["accuracy"] < 60.0 else "medium",
                    target_component="intent_detection",
                    implementation_details={
                        "target_intent": intent,
                        "current_accuracy": data["accuracy"],
                        "target_accuracy": 90.0,
                        "improvement_strategy": "enhance_patterns"
                    },
                    expected_impact=f"Increase {intent} detection accuracy from {data['accuracy']:.1f}% to 90%",
                    created_at=datetime.now()
                )
                
                actions.append(action)
        
        return actions
    
    def _generate_quality_improvements(self, analysis: Dict[str, Any]) -> List[ImprovementAction]:
        """Generate improvements for response quality."""
        actions = []
        
        # Analyze common issues in low-rated feedback
        low_rated_patterns = self._analyze_low_rated_patterns(analysis)
        
        for pattern in low_rated_patterns:
            action_id = f"quality_improve_{pattern['type']}_{int(time.time())}"
            
            action = ImprovementAction(
                id=action_id,
                action_type="response_quality_improvement",
                description=f"Improve {pattern['type']} in responses",
                priority="high" if pattern["frequency"] > 0.3 else "medium",
                target_component="response_generation",
                implementation_details={
                    "issue_type": pattern["type"],
                    "frequency": pattern["frequency"],
                    "improvement_strategy": pattern["strategy"]
                },
                expected_impact=f"Reduce {pattern['type']} issues by 50%",
                created_at=datetime.now()
            )
            
            actions.append(action)
        
        return actions
    
    def _generate_content_improvements(self, analysis: Dict[str, Any]) -> List[ImprovementAction]:
        """Generate improvements for content relevance."""
        actions = []
        
        # Analyze content patterns
        content_patterns = analysis.get("content_patterns", {})
        
        if content_patterns.get("length_rating_correlation", 0) < -0.2:
            # Shorter responses get better ratings
            action = ImprovementAction(
                id=f"content_length_{int(time.time())}",
                action_type="response_length_optimization",
                description="Optimize response length for better ratings",
                priority="medium",
                target_component="response_generation",
                implementation_details={
                    "target_length": "concise",
                    "current_correlation": content_patterns["length_rating_correlation"],
                    "strategy": "reduce_verbosity"
                },
                expected_impact="Improve ratings through more concise responses",
                created_at=datetime.now()
            )
            actions.append(action)
        
        return actions
    
    def _analyze_low_rated_patterns(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze patterns in low-rated feedback."""
        patterns = []
        
        # This would typically analyze the actual feedback content
        # For now, return common patterns based on analysis insights
        insights = analysis.get("insights", [])
        
        for insight in insights:
            if "intent detection" in insight.lower():
                patterns.append({
                    "type": "intent_detection",
                    "frequency": 0.4,
                    "strategy": "enhance_patterns"
                })
            elif "clarity" in insight.lower():
                patterns.append({
                    "type": "clarity",
                    "frequency": 0.3,
                    "strategy": "improve_explanation"
                })
            elif "relevance" in insight.lower():
                patterns.append({
                    "type": "relevance",
                    "frequency": 0.25,
                    "strategy": "better_context"
                })
        
        return patterns
    
    def implement_improvement(self, action: ImprovementAction) -> bool:
        """
        Implement a specific improvement action.
        
        Args:
            action: The improvement action to implement
            
        Returns:
            True if implementation was successful
        """
        try:
            if action.action_type == "intent_detection_improvement":
                return self._implement_intent_improvement(action)
            elif action.action_type == "response_quality_improvement":
                return self._implement_quality_improvement(action)
            elif action.action_type == "response_length_optimization":
                return self._implement_length_optimization(action)
            else:
                print(f"Unknown improvement action type: {action.action_type}")
                return False
                
        except Exception as e:
            print(f"Error implementing improvement {action.id}: {e}")
            action.status = "failed"
            return False
    
    def _implement_intent_improvement(self, action: ImprovementAction) -> bool:
        """Implement intent detection improvements."""
        target_intent = action.implementation_details["target_intent"]
        
        # Update the memory utils with improved patterns
        # This would typically update the actual intent detection logic
        # For now, we'll simulate the improvement
        
        action.status = "completed"
        return True
    
    def _implement_quality_improvement(self, action: ImprovementAction) -> bool:
        """Implement response quality improvements."""
        issue_type = action.implementation_details["issue_type"]
        
        # Update the email agent with improved templates
        # This would typically update the actual response generation logic
        
        action.status = "completed"
        return True
    
    def _implement_length_optimization(self, action: ImprovementAction) -> bool:
        """Implement response length optimization."""
        # Update the email agent with length guidelines
        
        action.status = "completed"
        return True
    
    def test_improvement(self, action: ImprovementAction, test_cases: List[str]) -> ImprovementResult:
        """
        Test an improvement action with sample test cases.
        
        Args:
            action: The improvement action to test
            test_cases: List of test cases to evaluate
            
        Returns:
            Improvement result with metrics
        """
        # Get baseline metrics
        before_metrics = self._evaluate_test_cases(test_cases)
        
        # Implement the improvement
        success = self.implement_improvement(action)
        
        if success:
            # Get metrics after improvement
            after_metrics = self._evaluate_test_cases(test_cases)
            
            # Calculate improvement
            improvement_percentage = self._calculate_improvement(before_metrics, after_metrics)
            
            result = ImprovementResult(
                action_id=action.id,
                success=True,
                before_metrics=before_metrics,
                after_metrics=after_metrics,
                improvement_percentage=improvement_percentage,
                notes="Improvement implemented successfully",
                completed_at=datetime.now()
            )
        else:
            result = ImprovementResult(
                action_id=action.id,
                success=False,
                before_metrics=before_metrics,
                after_metrics=before_metrics,  # No change
                improvement_percentage=0.0,
                notes="Improvement implementation failed",
                completed_at=datetime.now()
            )
        
        self.improvement_results.append(result)
        return result
    
    def _evaluate_test_cases(self, test_cases: List[str]) -> Dict[str, float]:
        """Evaluate test cases and return metrics."""
        # This would typically run the evaluation system
        # For now, return simulated metrics
        return {
            "intent_accuracy": 0.85,
            "response_quality": 0.78,
            "overall_score": 0.82
        }
    
    def _calculate_improvement(self, before: Dict[str, float], after: Dict[str, float]) -> float:
        """Calculate improvement percentage."""
        if not before or not after:
            return 0.0
        
        # Calculate average improvement across all metrics
        improvements = []
        for metric in before:
            if metric in after:
                before_val = before[metric]
                after_val = after[metric]
                if before_val > 0:
                    improvement = ((after_val - before_val) / before_val) * 100
                    improvements.append(improvement)
        
        return sum(improvements) / len(improvements) if improvements else 0.0
    
    def get_improvement_summary(self) -> Dict[str, Any]:
        """Get a summary of improvement actions and results."""
        total_actions = len(self.improvement_actions)
        completed_actions = len([a for a in self.improvement_actions if a.status == "completed"])
        failed_actions = len([a for a in self.improvement_actions if a.status == "failed"])
        
        successful_results = [r for r in self.improvement_results if r.success]
        avg_improvement = sum(r.improvement_percentage for r in successful_results) / len(successful_results) if successful_results else 0.0
        
        return {
            "total_actions": total_actions,
            "completed_actions": completed_actions,
            "failed_actions": failed_actions,
            "success_rate": (completed_actions / total_actions * 100) if total_actions > 0 else 0.0,
            "average_improvement": avg_improvement,
            "total_results": len(self.improvement_results)
        }
