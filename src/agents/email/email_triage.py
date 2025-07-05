"""
Email Triage System

This module provides email triage and classification capabilities to:
- Analyze email content and metadata
- Classify emails by priority and category
- Route emails to appropriate handlers
- Provide intelligent email management suggestions

Following the LangChain agents-from-scratch pattern for triage systems.
"""

import os
import sys
from typing import Dict, List, Any
from datetime import datetime
import re

# Add the parent directory to the path to import required modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src.utils.dynamodb_service import dynamodb_service_singleton as dynamodb_service

class EmailTriage:
    """
    Email Triage System for analyzing and classifying emails.
    
    This system follows the LangChain agents-from-scratch pattern for
    intelligent email processing and routing.
    """
    
    def __init__(self, user_id: str = None):
        """
        Initialize the Email Triage system.
        
        Args:
            user_id: User ID for user-specific triage rules
        """
        self.user_id = user_id
        self.dynamodb_service = dynamodb_service
        
        # Priority keywords and patterns
        self.priority_keywords = {
            "urgent": [
                "urgent", "asap", "immediate", "critical", "emergency",
                "deadline", "due today", "important", "priority"
            ],
            "high": [
                "important", "priority", "meeting", "deadline", "project",
                "client", "customer", "boss", "manager"
            ],
            "medium": [
                "update", "information", "newsletter", "notification",
                "reminder", "follow-up"
            ],
            "low": [
                "spam", "advertisement", "promotion", "newsletter",
                "social media", "marketing"
            ]
        }
        
        # Category patterns
        self.category_patterns = {
            "work": [
                r"meeting", r"project", r"deadline", r"client", r"customer",
                r"team", r"collaboration", r"work", r"business"
            ],
            "personal": [
                r"family", r"friend", r"personal", r"social", r"invitation",
                r"party", r"celebration"
            ],
            "finance": [
                r"bill", r"payment", r"invoice", r"bank", r"account",
                r"financial", r"money", r"transaction"
            ],
            "shopping": [
                r"order", r"purchase", r"shipping", r"delivery", r"product",
                r"store", r"shop", r"buy"
            ],
            "travel": [
                r"flight", r"hotel", r"booking", r"reservation", r"travel",
                r"trip", r"vacation"
            ]
        }
        
        # Action suggestions
        self.action_suggestions = {
            "urgent": ["Reply immediately", "Forward to relevant person", "Schedule follow-up"],
            "high": ["Reply within 24 hours", "Add to calendar", "Set reminder"],
            "medium": ["Reply when convenient", "Archive if not needed", "Flag for later"],
            "low": ["Archive", "Mark as read", "Unsubscribe if unwanted"]
        }

    def triage_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze and triage an email to determine priority, category, and suggested actions.
        
        Args:
            email_data: Email data containing subject, body, sender, etc.
            
        Returns:
            Triage results with priority, category, and suggestions
        """
        try:
            # Extract email components
            subject = email_data.get("subject", "").lower()
            body = email_data.get("body", "").lower()
            sender = email_data.get("from", "").lower()
            
            # Analyze priority
            priority = self._analyze_priority(subject, body, sender)
            
            # Analyze category
            category = self._analyze_category(subject, body, sender)
            
            # Generate suggestions
            suggestions = self._generate_suggestions(priority, category, email_data)
            
            # Calculate urgency score
            urgency_score = self._calculate_urgency_score(priority, email_data)
            
            # Determine if immediate attention is needed
            needs_immediate_attention = urgency_score >= 8
            
            return {
                "priority": priority,
                "category": category,
                "urgency_score": urgency_score,
                "needs_immediate_attention": needs_immediate_attention,
                "suggestions": suggestions,
                "triage_timestamp": datetime.now().isoformat(),
                "confidence": self._calculate_confidence(priority, category)
            }
            
        except Exception as e:
            return {
                "priority": "medium",
                "category": "unknown",
                "urgency_score": 5,
                "needs_immediate_attention": False,
                "suggestions": ["Review manually"],
                "error": str(e),
                "triage_timestamp": datetime.now().isoformat(),
                "confidence": 0.5
            }

    def _analyze_priority(self, subject: str, body: str, sender: str) -> str:
        """Analyze email priority based on content and sender."""
        combined_text = f"{subject} {body} {sender}"
        
        # Count priority keywords
        priority_scores = {}
        for priority, keywords in self.priority_keywords.items():
            score = sum(1 for keyword in keywords if keyword in combined_text)
            priority_scores[priority] = score
        
        # Determine priority based on scores
        if priority_scores.get("urgent", 0) > 0:
            return "urgent"
        elif priority_scores.get("high", 0) > 1:
            return "high"
        elif priority_scores.get("low", 0) > 2:
            return "low"
        else:
            return "medium"

    def _analyze_category(self, subject: str, body: str, sender: str) -> str:
        """Analyze email category based on content patterns."""
        combined_text = f"{subject} {body} {sender}"
        
        # Check category patterns
        category_scores = {}
        for category, patterns in self.category_patterns.items():
            score = sum(1 for pattern in patterns if re.search(pattern, combined_text))
            category_scores[category] = score
        
        # Return category with highest score
        if category_scores:
            return max(category_scores, key=category_scores.get)
        else:
            return "general"

    def _generate_suggestions(self, priority: str, category: str, email_data: Dict) -> List[str]:
        """Generate action suggestions based on priority and category."""
        suggestions = []
        
        # Add priority-based suggestions
        suggestions.extend(self.action_suggestions.get(priority, []))
        
        # Add category-specific suggestions
        if category == "work":
            suggestions.extend([
                "Add to work calendar",
                "Forward to team if relevant",
                "Set work reminder"
            ])
        elif category == "finance":
            suggestions.extend([
                "Review payment details",
                "Check account status",
                "Set payment reminder"
            ])
        elif category == "personal":
            suggestions.extend([
                "Add to personal calendar",
                "Reply with personal touch",
                "Share with family if relevant"
            ])
        
        # Remove duplicates and limit to top 5
        unique_suggestions = list(dict.fromkeys(suggestions))
        return unique_suggestions[:5]

    def _calculate_urgency_score(self, priority: str, email_data: Dict) -> int:
        """Calculate urgency score (0-10) based on various factors."""
        score = 0
        
        # Base score from priority
        priority_scores = {"urgent": 8, "high": 6, "medium": 4, "low": 2}
        score += priority_scores.get(priority, 4)
        
        # Additional factors
        subject = email_data.get("subject", "").lower()
        body = email_data.get("body", "").lower()
        
        # Time-sensitive keywords
        time_keywords = ["today", "tomorrow", "asap", "deadline", "due"]
        for keyword in time_keywords:
            if keyword in subject or keyword in body:
                score += 1
        
        # Sender importance (simplified)
        sender = email_data.get("from", "").lower()
        important_senders = ["boss", "manager", "ceo", "director", "client"]
        if any(sender_type in sender for sender_type in important_senders):
            score += 2
        
        # Cap at 10
        return min(score, 10)

    def _calculate_confidence(self, priority: str, category: str) -> float:
        """Calculate confidence score (0-1) in the triage decision."""
        # Simplified confidence calculation
        # In real implementation, this would be based on ML model confidence
        
        confidence = 0.7  # Base confidence
        
        # Adjust based on priority clarity
        if priority in ["urgent", "low"]:
            confidence += 0.2
        elif priority == "medium":
            confidence -= 0.1
        
        # Adjust based on category clarity
        if category != "general":
            confidence += 0.1
        
        return min(confidence, 1.0)

    def batch_triage_emails(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Triage multiple emails at once.
        
        Args:
            emails: List of email data dictionaries
            
        Returns:
            List of triage results
        """
        results = []
        for email in emails:
            triage_result = self.triage_email(email)
            triage_result["email_id"] = email.get("id", "unknown")
            results.append(triage_result)
        
        # Sort by urgency score (highest first)
        results.sort(key=lambda x: x.get("urgency_score", 0), reverse=True)
        
        return results

    def get_triage_summary(self, triage_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary of triage results.
        
        Args:
            triage_results: List of triage results
            
        Returns:
            Summary statistics
        """
        if not triage_results:
            return {"message": "No emails to triage"}
        
        # Count by priority
        priority_counts = {}
        category_counts = {}
        urgency_scores = []
        
        for result in triage_results:
            priority = result.get("priority", "unknown")
            category = result.get("category", "unknown")
            urgency_score = result.get("urgency_score", 0)
            
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
            category_counts[category] = category_counts.get(category, 0) + 1
            urgency_scores.append(urgency_score)
        
        # Calculate statistics
        avg_urgency = sum(urgency_scores) / len(urgency_scores) if urgency_scores else 0
        urgent_count = sum(1 for result in triage_results if result.get("needs_immediate_attention", False))
        
        return {
            "total_emails": len(triage_results),
            "priority_distribution": priority_counts,
            "category_distribution": category_counts,
            "average_urgency_score": round(avg_urgency, 2),
            "emails_needing_immediate_attention": urgent_count,
            "top_priorities": [
                result for result in triage_results 
                if result.get("priority") in ["urgent", "high"]
            ][:5]
        }

    def update_triage_rules(self, user_id: str, rules: Dict[str, Any]) -> bool:
        """
        Update user-specific triage rules.
        
        Args:
            user_id: User ID
            rules: New triage rules
            
        Returns:
            Success status
        """
        try:
            # Save user-specific triage rules to DynamoDB
            rules_data = {
                "user_id": user_id,
                "rules": rules,
                "updated_at": datetime.now().isoformat()
            }
            
            # This would save to a triage_rules table
            # For now, we'll use a mock implementation
            return True
            
        except Exception as e:
            print(f"Error updating triage rules: {e}")
            return False

    def get_user_triage_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get user-specific triage preferences and rules.
        
        Args:
            user_id: User ID
            
        Returns:
            User's triage preferences
        """
        # Mock implementation - in real system, this would fetch from DynamoDB
        return {
            "user_id": user_id,
            "priority_keywords": self.priority_keywords,
            "category_patterns": self.category_patterns,
            "action_suggestions": self.action_suggestions,
            "preferences": {
                "auto_archive_low_priority": True,
                "flag_urgent_emails": True,
                "notify_on_high_priority": True
            }
        } 