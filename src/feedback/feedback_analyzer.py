"""
Feedback Analyzer

This module analyzes collected feedback to identify patterns, trends, and improvement opportunities
for the email assistant agent.

Following the LangChain agents-from-scratch human-in-the-loop pattern.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter

from langchain_openai import ChatOpenAI

from .feedback_collector import FeedbackItem, FeedbackType, FeedbackRating

class FeedbackAnalyzer:
    """Analyzes feedback to identify patterns and improvement opportunities."""
    
    def __init__(self):
        """Initialize the feedback analyzer."""
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.0,
            tags=["remo", "feedback-analysis"]
        )
    
    def analyze_feedback_patterns(self, feedback_items: List[FeedbackItem]) -> Dict[str, Any]:
        """
        Analyze feedback to identify patterns and trends.
        
        Args:
            feedback_items: List of feedback items to analyze
            
        Returns:
            Analysis results with patterns and insights
        """
        if not feedback_items:
            return {
                "total_items": 0,
                "patterns": {},
                "insights": [],
                "recommendations": []
            }
        
        # Basic statistics
        total_items = len(feedback_items)
        average_rating = sum(item.rating.value for item in feedback_items) / total_items
        
        # Rating distribution
        rating_distribution = Counter(item.rating.value for item in feedback_items)
        
        # Feedback type distribution
        type_distribution = Counter(item.feedback_type.value for item in feedback_items)
        
        # Time-based analysis
        time_patterns = self._analyze_time_patterns(feedback_items)
        
        # Content analysis
        content_patterns = self._analyze_content_patterns(feedback_items)
        
        # Intent detection analysis
        intent_patterns = self._analyze_intent_patterns(feedback_items)
        
        # Generate insights and recommendations
        insights = self._generate_insights(feedback_items, {
            "total_items": total_items,
            "average_rating": average_rating,
            "rating_distribution": dict(rating_distribution),
            "type_distribution": dict(type_distribution),
            "time_patterns": time_patterns,
            "content_patterns": content_patterns,
            "intent_patterns": intent_patterns
        })
        
        recommendations = self._generate_recommendations(feedback_items, insights)
        
        return {
            "total_items": total_items,
            "average_rating": average_rating,
            "rating_distribution": dict(rating_distribution),
            "type_distribution": dict(type_distribution),
            "time_patterns": time_patterns,
            "content_patterns": content_patterns,
            "intent_patterns": intent_patterns,
            "insights": insights,
            "recommendations": recommendations
        }
    
    def _analyze_time_patterns(self, feedback_items: List[FeedbackItem]) -> Dict[str, Any]:
        """Analyze feedback patterns over time."""
        if len(feedback_items) < 2:
            return {"trend": "insufficient_data"}
        
        # Sort by timestamp
        sorted_items = sorted(feedback_items, key=lambda x: x.timestamp)
        
        # Calculate rating trends
        ratings_over_time = [(item.timestamp, item.rating.value) for item in sorted_items]
        
        # Simple trend analysis
        first_half = ratings_over_time[:len(ratings_over_time)//2]
        second_half = ratings_over_time[len(ratings_over_time)//2:]
        
        first_avg = sum(rating for _, rating in first_half) / len(first_half)
        second_avg = sum(rating for _, rating in second_half) / len(second_half)
        
        if second_avg > first_avg:
            trend = "improving"
        elif second_avg < first_avg:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "first_half_average": first_avg,
            "second_half_average": second_avg,
            "improvement_rate": second_avg - first_avg
        }
    
    def _analyze_content_patterns(self, feedback_items: List[FeedbackItem]) -> Dict[str, Any]:
        """Analyze patterns in user messages and agent responses."""
        # Common user message patterns
        user_messages = [item.user_message.lower() for item in feedback_items]
        
        # Extract common keywords
        keywords = []
        for message in user_messages:
            words = message.split()
            keywords.extend([word for word in words if len(word) > 3])
        
        keyword_freq = Counter(keywords)
        common_keywords = keyword_freq.most_common(10)
        
        # Analyze response length patterns
        response_lengths = [len(item.agent_response) for item in feedback_items]
        avg_response_length = sum(response_lengths) / len(response_lengths)
        
        # Correlation between response length and rating
        length_rating_correlation = self._calculate_correlation(response_lengths, 
                                                              [item.rating.value for item in feedback_items])
        
        return {
            "common_keywords": common_keywords,
            "average_response_length": avg_response_length,
            "length_rating_correlation": length_rating_correlation,
            "response_length_distribution": {
                "short": len([l for l in response_lengths if l < 100]),
                "medium": len([l for l in response_lengths if 100 <= l < 300]),
                "long": len([l for l in response_lengths if l >= 300])
            }
        }
    
    def _analyze_intent_patterns(self, feedback_items: List[FeedbackItem]) -> Dict[str, Any]:
        """Analyze intent detection patterns."""
        intent_accuracy = {}
        intent_counts = Counter()
        
        for item in feedback_items:
            if item.expected_intent and item.actual_intent:
                intent_counts[item.expected_intent] += 1
                
                if item.expected_intent not in intent_accuracy:
                    intent_accuracy[item.expected_intent] = {"correct": 0, "total": 0}
                
                intent_accuracy[item.expected_intent]["total"] += 1
                if item.expected_intent == item.actual_intent:
                    intent_accuracy[item.expected_intent]["correct"] += 1
        
        # Calculate accuracy percentages
        for intent in intent_accuracy:
            total = intent_accuracy[intent]["total"]
            correct = intent_accuracy[intent]["correct"]
            intent_accuracy[intent]["accuracy"] = (correct / total) * 100 if total > 0 else 0
        
        return {
            "intent_accuracy": intent_accuracy,
            "intent_distribution": dict(intent_counts),
            "most_common_intent": intent_counts.most_common(1)[0] if intent_counts else None
        }
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate correlation coefficient between two lists."""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        sum_y2 = sum(y[i] ** 2 for i in range(n))
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = ((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2)) ** 0.5
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def _generate_insights(self, feedback_items: List[FeedbackItem], 
                          analysis_data: Dict[str, Any]) -> List[str]:
        """Generate insights from feedback analysis."""
        insights = []
        
        # Rating insights
        avg_rating = analysis_data["average_rating"]
        if avg_rating < 3.0:
            insights.append("Overall feedback ratings are below average, indicating significant improvement needed")
        elif avg_rating > 4.0:
            insights.append("Overall feedback ratings are excellent, agent is performing well")
        else:
            insights.append("Overall feedback ratings are moderate, room for improvement")
        
        # Intent detection insights
        intent_patterns = analysis_data["intent_patterns"]
        if intent_patterns["intent_accuracy"]:
            worst_intent = min(intent_patterns["intent_accuracy"].items(), 
                             key=lambda x: x[1]["accuracy"])
            insights.append(f"Intent detection is weakest for '{worst_intent[0]}' with {worst_intent[1]['accuracy']:.1f}% accuracy")
        
        # Time trend insights
        time_patterns = analysis_data["time_patterns"]
        if time_patterns["trend"] == "improving":
            insights.append("Agent performance is improving over time")
        elif time_patterns["trend"] == "declining":
            insights.append("Agent performance is declining over time, immediate attention needed")
        
        # Content insights
        content_patterns = analysis_data["content_patterns"]
        if content_patterns["length_rating_correlation"] > 0.3:
            insights.append("Longer responses tend to receive higher ratings")
        elif content_patterns["length_rating_correlation"] < -0.3:
            insights.append("Shorter responses tend to receive higher ratings")
        
        return insights
    
    def _generate_recommendations(self, feedback_items: List[FeedbackItem], 
                                insights: List[str]) -> List[str]:
        """Generate improvement recommendations based on insights."""
        recommendations = []
        
        # Analyze low-rated feedback for specific issues
        low_rated = [item for item in feedback_items if item.rating.value <= 2]
        
        if low_rated:
            # Common issues in low-rated feedback
            common_issues = self._identify_common_issues(low_rated)
            
            for issue in common_issues:
                if "intent" in issue.lower():
                    recommendations.append("Improve intent detection accuracy through better training data")
                elif "response" in issue.lower():
                    recommendations.append("Enhance response quality and relevance")
                elif "clarity" in issue.lower():
                    recommendations.append("Improve response clarity and understandability")
        
        # General recommendations based on insights
        for insight in insights:
            if "intent detection" in insight:
                recommendations.append("Review and update intent detection patterns")
            if "declining" in insight:
                recommendations.append("Investigate recent changes that may have caused performance decline")
            if "improving" in insight:
                recommendations.append("Continue current improvement strategies")
        
        # Add general recommendations
        if not recommendations:
            recommendations.append("Collect more feedback to identify specific improvement areas")
            recommendations.append("Implement A/B testing for different response strategies")
        
        return recommendations
    
    def _identify_common_issues(self, feedback_items: List[FeedbackItem]) -> List[str]:
        """Identify common issues in low-rated feedback."""
        issues = []
        
        for item in feedback_items:
            if item.comments:
                # Simple keyword extraction for common issues
                comment_lower = item.comments.lower()
                
                if "intent" in comment_lower and "wrong" in comment_lower:
                    issues.append("Wrong intent detection")
                elif "unclear" in comment_lower or "confusing" in comment_lower:
                    issues.append("Unclear response")
                elif "incomplete" in comment_lower or "missing" in comment_lower:
                    issues.append("Incomplete information")
                elif "irrelevant" in comment_lower or "off-topic" in comment_lower:
                    issues.append("Irrelevant response")
        
        # Count and return most common issues
        issue_counts = Counter(issues)
        return [issue for issue, count in issue_counts.most_common(5)]
    
    def generate_improvement_report(self, feedback_items: List[FeedbackItem]) -> Dict[str, Any]:
        """
        Generate a comprehensive improvement report.
        
        Args:
            feedback_items: List of feedback items to analyze
            
        Returns:
            Comprehensive improvement report
        """
        analysis = self.analyze_feedback_patterns(feedback_items)
        
        # Generate detailed report using LLM
        report_prompt = f"""
Based on the following feedback analysis, generate a comprehensive improvement report:

Analysis Data: {json.dumps(analysis, indent=2)}

Please provide:
1. Executive Summary (2-3 sentences)
2. Key Findings (bullet points)
3. Priority Improvement Areas (ranked by importance)
4. Specific Action Items (with timelines)
5. Success Metrics (how to measure improvement)

Format the response as JSON:
{{
    "executive_summary": "Brief summary",
    "key_findings": ["finding1", "finding2"],
    "priority_areas": ["area1", "area2"],
    "action_items": [
        {{"action": "description", "priority": "high/medium/low", "timeline": "1-2 weeks"}}
    ],
    "success_metrics": ["metric1", "metric2"]
}}
"""
        
        try:
            result = self.llm.invoke(report_prompt)
            report = json.loads(result.content.strip())
        except Exception as e:
            print(f"Error generating improvement report: {e}")
            report = {
                "executive_summary": "Analysis completed but report generation failed",
                "key_findings": analysis["insights"],
                "priority_areas": analysis["recommendations"],
                "action_items": [],
                "success_metrics": ["Average rating improvement", "Intent detection accuracy"]
            }
        
        return {
            "analysis": analysis,
            "report": report,
            "generated_at": datetime.now().isoformat()
        }
