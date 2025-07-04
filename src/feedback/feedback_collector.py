"""
Feedback Collector

This module handles collection and storage of human feedback for the email assistant agent.
It provides interfaces for collecting feedback on agent responses and storing it for analysis.

Following the LangChain agents-from-scratch human-in-the-loop pattern.
"""

import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

try:
    from langchain_aws import ChatBedrock
except ImportError:
    ChatBedrock = None
import boto3
import os

class FeedbackType(Enum):
    """Types of feedback that can be collected."""
    RESPONSE_QUALITY = "response_quality"
    INTENT_DETECTION = "intent_detection"
    ACTION_ACCURACY = "action_accuracy"
    CONTENT_RELEVANCE = "content_relevance"
    HELPFULNESS = "helpfulness"
    GENERAL = "general"

class FeedbackRating(Enum):
    """Rating scale for feedback."""
    VERY_POOR = 1
    POOR = 2
    FAIR = 3
    GOOD = 4
    EXCELLENT = 5

@dataclass
class FeedbackItem:
    """Represents a single piece of human feedback."""
    id: str
    user_id: str
    session_id: str
    timestamp: datetime
    feedback_type: FeedbackType
    rating: FeedbackRating
    user_message: str
    agent_response: str
    expected_intent: Optional[str] = None
    actual_intent: Optional[str] = None
    expected_action: Optional[str] = None
    actual_action: Optional[str] = None
    comments: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    evaluation_score: Optional[float] = None
    improvement_suggestions: Optional[List[str]] = None

class FeedbackCollector:
    """Collects and manages human feedback for agent improvement."""
    
    def __init__(self, user_id: str = "default_user"):
        """
        Initialize the feedback collector.
        
        Args:
            user_id: User ID for feedback collection
        """
        self.user_id = user_id
        self.session_id = self._generate_session_id()
        self.feedback_items: List[FeedbackItem] = []
        
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
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        return f"session_{int(time.time())}_{self.user_id}"
    
    def collect_response_feedback(self, 
                                user_message: str,
                                agent_response: str,
                                expected_intent: Optional[str] = None,
                                actual_intent: Optional[str] = None,
                                expected_action: Optional[str] = None,
                                actual_action: Optional[str] = None,
                                evaluation_score: Optional[float] = None) -> FeedbackItem:
        """
        Collect feedback on an agent response.
        
        Args:
            user_message: The user's original message
            agent_response: The agent's response
            expected_intent: Expected intent (if known)
            actual_intent: Actual detected intent
            expected_action: Expected action (if known)
            actual_action: Actual detected action
            evaluation_score: Automated evaluation score
            
        Returns:
            FeedbackItem with collected feedback
        """
        feedback_id = f"feedback_{int(time.time())}_{len(self.feedback_items)}"
        
        # Analyze the response for potential issues
        analysis = self._analyze_response_for_feedback(
            user_message, agent_response, expected_intent, actual_intent
        )
        
        # Create feedback item
        feedback_item = FeedbackItem(
            id=feedback_id,
            user_id=self.user_id,
            session_id=self.session_id,
            timestamp=datetime.now(),
            feedback_type=FeedbackType.RESPONSE_QUALITY,
            rating=analysis.get("suggested_rating", FeedbackRating.FAIR),
            user_message=user_message,
            agent_response=agent_response,
            expected_intent=expected_intent,
            actual_intent=actual_intent,
            expected_action=expected_action,
            actual_action=actual_action,
            comments=analysis.get("comments"),
            context=analysis.get("context"),
            evaluation_score=evaluation_score,
            improvement_suggestions=analysis.get("suggestions", [])
        )
        
        self.feedback_items.append(feedback_item)
        return feedback_item
    
    def _analyze_response_for_feedback(self, 
                                     user_message: str,
                                     agent_response: str,
                                     expected_intent: Optional[str] = None,
                                     actual_intent: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a response to suggest feedback and improvements.
        
        Args:
            user_message: User's message
            agent_response: Agent's response
            expected_intent: Expected intent
            actual_intent: Actual intent
            
        Returns:
            Analysis results with suggestions
        """
        try:
            prompt = f"""
You are analyzing an email assistant's response to provide feedback and improvement suggestions.

User Message: "{user_message}"
Agent Response: "{agent_response}"
Expected Intent: {expected_intent or "Unknown"}
Actual Intent: {actual_intent or "Unknown"}

Please analyze this response and provide:
1. A suggested rating (1-5 scale)
2. Comments on what worked well and what didn't
3. Specific improvement suggestions
4. Context about the interaction

Focus on:
- Intent detection accuracy
- Response relevance and helpfulness
- Completeness of information
- Clarity and understandability
- Action accuracy

Provide your analysis in JSON format:
{{
    "suggested_rating": 3,
    "comments": "Brief analysis of the response",
    "suggestions": ["suggestion1", "suggestion2"],
    "context": {{"key": "value"}}
}}
"""
            
            result = self.llm.invoke(prompt)
            analysis = json.loads(result.content.strip())
            
            # Convert rating to enum
            rating_value = analysis.get("suggested_rating", 3)
            analysis["suggested_rating"] = FeedbackRating(rating_value)
            
            return analysis
            
        except Exception as e:
            print(f"Error in response analysis: {e}")
            return {
                "suggested_rating": FeedbackRating.FAIR,
                "comments": "Analysis failed",
                "suggestions": ["Improve response analysis"],
                "context": {"error": str(e)}
            }
    
    def collect_explicit_feedback(self,
                                feedback_type: FeedbackType,
                                rating: FeedbackRating,
                                user_message: str,
                                agent_response: str,
                                comments: Optional[str] = None,
                                context: Optional[Dict[str, Any]] = None) -> FeedbackItem:
        """
        Collect explicit feedback from a human user.
        
        Args:
            feedback_type: Type of feedback
            rating: User's rating
            user_message: User's message
            agent_response: Agent's response
            comments: User's comments
            context: Additional context
            
        Returns:
            FeedbackItem with explicit feedback
        """
        feedback_id = f"feedback_{int(time.time())}_{len(self.feedback_items)}"
        
        feedback_item = FeedbackItem(
            id=feedback_id,
            user_id=self.user_id,
            session_id=self.session_id,
            timestamp=datetime.now(),
            feedback_type=feedback_type,
            rating=rating,
            user_message=user_message,
            agent_response=agent_response,
            comments=comments,
            context=context
        )
        
        self.feedback_items.append(feedback_item)
        return feedback_item
    
    def get_feedback_summary(self) -> Dict[str, Any]:
        """
        Get a summary of collected feedback.
        
        Returns:
            Summary statistics
        """
        if not self.feedback_items:
            return {
                "total_feedback": 0,
                "average_rating": 0.0,
                "feedback_types": {},
                "rating_distribution": {},
                "session_duration": 0.0
            }
        
        # Calculate statistics
        total_feedback = len(self.feedback_items)
        average_rating = sum(item.rating.value for item in self.feedback_items) / total_feedback
        
        # Feedback type distribution
        feedback_types = {}
        for item in self.feedback_items:
            feedback_type = item.feedback_type.value
            feedback_types[feedback_type] = feedback_types.get(feedback_type, 0) + 1
        
        # Rating distribution
        rating_distribution = {}
        for item in self.feedback_items:
            rating = item.rating.value
            rating_distribution[rating] = rating_distribution.get(rating, 0) + 1
        
        # Session duration
        if len(self.feedback_items) > 1:
            start_time = min(item.timestamp for item in self.feedback_items)
            end_time = max(item.timestamp for item in self.feedback_items)
            session_duration = (end_time - start_time).total_seconds()
        else:
            session_duration = 0.0
        
        return {
            "total_feedback": total_feedback,
            "average_rating": average_rating,
            "feedback_types": feedback_types,
            "rating_distribution": rating_distribution,
            "session_duration": session_duration,
            "session_id": self.session_id,
            "user_id": self.user_id
        }
    
    def export_feedback(self, format: str = "json") -> str:
        """
        Export collected feedback.
        
        Args:
            format: Export format ("json" or "csv")
            
        Returns:
            Exported feedback data
        """
        if format == "json":
            return json.dumps({
                "session_id": self.session_id,
                "user_id": self.user_id,
                "timestamp": datetime.now().isoformat(),
                "summary": self.get_feedback_summary(),
                "feedback_items": [asdict(item) for item in self.feedback_items]
            }, indent=2, default=str)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def clear_feedback(self):
        """Clear all collected feedback."""
        self.feedback_items = []
        self.session_id = self._generate_session_id()
    
    def get_feedback_by_type(self, feedback_type: FeedbackType) -> List[FeedbackItem]:
        """
        Get feedback items by type.
        
        Args:
            feedback_type: Type of feedback to filter
            
        Returns:
            List of feedback items
        """
        return [item for item in self.feedback_items if item.feedback_type == feedback_type]
    
    def get_low_rated_feedback(self, max_rating: FeedbackRating = FeedbackRating.FAIR) -> List[FeedbackItem]:
        """
        Get feedback items with low ratings (for improvement focus).
        
        Args:
            max_rating: Maximum rating to consider "low"
            
        Returns:
            List of low-rated feedback items
        """
        return [item for item in self.feedback_items if item.rating.value <= max_rating.value]
