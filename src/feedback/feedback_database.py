"""
Feedback Database

This module provides persistent storage for feedback data using DynamoDB.
It handles storing and retrieving feedback items and improvement actions.

Following the LangChain agents-from-scratch human-in-the-loop pattern.
"""

import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import asdict

from src.utils.dynamodb_service import dynamodb_service_singleton as dynamodb_service
from .feedback_collector import FeedbackItem, FeedbackType, FeedbackRating
from .agent_improver import ImprovementAction, ImprovementResult

class FeedbackDatabase:
    """Manages persistent storage of feedback data in DynamoDB."""
    
    def __init__(self):
        """Initialize the feedback database."""
        self.db = dynamodb_service
        self.table_name = "remo-feedback"
        self.ensure_table_exists()
    
    def ensure_table_exists(self):
        """Ensure the feedback table exists in DynamoDB."""
        try:
            # Check if table exists
            self.db.dynamodb.Table(self.table_name).load()
            print(f"✅ Feedback table '{self.table_name}' exists")
        except Exception:
            # Create table if it doesn't exist
            self._create_feedback_table()
    
    def _create_feedback_table(self):
        """Create the feedback table in DynamoDB."""
        try:
            table = self.db.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {'AttributeName': 'id', 'KeyType': 'HASH'},  # Partition key
                    {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}  # Sort key
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'id', 'AttributeType': 'S'},
                    {'AttributeName': 'timestamp', 'AttributeType': 'S'},
                    {'AttributeName': 'user_id', 'AttributeType': 'S'},
                    {'AttributeName': 'feedback_type', 'AttributeType': 'S'},
                    {'AttributeName': 'rating', 'AttributeType': 'N'}
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'user_id-index',
                        'KeySchema': [
                            {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                            {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'},
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 5,
                            'WriteCapacityUnits': 5
                        }
                    },
                    {
                        'IndexName': 'feedback_type-index',
                        'KeySchema': [
                            {'AttributeName': 'feedback_type', 'KeyType': 'HASH'},
                            {'AttributeName': 'rating', 'KeyType': 'RANGE'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'},
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 5,
                            'WriteCapacityUnits': 5
                        }
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            )
            
            # Wait for table to be created
            table.meta.client.get_waiter('table_exists').wait(TableName=self.table_name)
            print(f"✅ Created feedback table '{self.table_name}'")
            
        except Exception as e:
            print(f"❌ Error creating feedback table: {e}")
    
    def save_feedback_item(self, feedback_item: FeedbackItem) -> bool:
        """
        Save a feedback item to the database.
        
        Args:
            feedback_item: The feedback item to save
            
        Returns:
            True if saved successfully
        """
        try:
            item_data = asdict(feedback_item)
            
            # Convert datetime to string for DynamoDB
            item_data['timestamp'] = feedback_item.timestamp.isoformat()
            item_data['feedback_type'] = feedback_item.feedback_type.value
            item_data['rating'] = feedback_item.rating.value
            
            # Convert any remaining datetime objects
            if 'context' in item_data and item_data['context']:
                for key, value in item_data['context'].items():
                    if isinstance(value, datetime):
                        item_data['context'][key] = value.isoformat()
            
            self.db.dynamodb.Table(self.table_name).put_item(Item=item_data)
            return True
            
        except Exception as e:
            print(f"❌ Error saving feedback item: {e}")
            return False
    
    def save_improvement_action(self, action: ImprovementAction) -> bool:
        """
        Save an improvement action to the database.
        
        Args:
            action: The improvement action to save
            
        Returns:
            True if saved successfully
        """
        try:
            action_data = asdict(action)
            action_data['timestamp'] = action.created_at.isoformat()
            action_data['item_type'] = 'improvement_action'
            
            self.db.dynamodb.Table(self.table_name).put_item(Item=action_data)
            return True
            
        except Exception as e:
            print(f"❌ Error saving improvement action: {e}")
            return False
    
    def save_improvement_result(self, result: ImprovementResult) -> bool:
        """
        Save an improvement result to the database.
        
        Args:
            result: The improvement result to save
            
        Returns:
            True if saved successfully
        """
        try:
            result_data = asdict(result)
            result_data['timestamp'] = result.completed_at.isoformat()
            result_data['item_type'] = 'improvement_result'
            
            self.db.dynamodb.Table(self.table_name).put_item(Item=result_data)
            return True
            
        except Exception as e:
            print(f"❌ Error saving improvement result: {e}")
            return False
    
    def get_user_feedback(self, user_id: str, limit: int = 100) -> List[FeedbackItem]:
        """
        Get feedback items for a specific user.
        
        Args:
            user_id: User ID to filter by
            limit: Maximum number of items to return
            
        Returns:
            List of feedback items
        """
        try:
            response = self.db.dynamodb.Table(self.table_name).query(
                IndexName='user_id-index',
                KeyConditionExpression='user_id = :user_id',
                ExpressionAttributeValues={':user_id': user_id},
                ScanIndexForward=False,  # Most recent first
                Limit=limit
            )
            
            feedback_items = []
            for item in response.get('Items', []):
                if 'item_type' not in item:  # Only feedback items
                    feedback_item = self._item_to_feedback(item)
                    if feedback_item:
                        feedback_items.append(feedback_item)
            
            return feedback_items
            
        except Exception as e:
            print(f"❌ Error getting user feedback: {e}")
            return []
    
    def get_feedback_by_type(self, feedback_type: FeedbackType, limit: int = 100) -> List[FeedbackItem]:
        """
        Get feedback items by type.
        
        Args:
            feedback_type: Type of feedback to filter by
            limit: Maximum number of items to return
            
        Returns:
            List of feedback items
        """
        try:
            response = self.db.dynamodb.Table(self.table_name).query(
                IndexName='feedback_type-index',
                KeyConditionExpression='feedback_type = :feedback_type',
                ExpressionAttributeValues={':feedback_type': feedback_type.value},
                ScanIndexForward=False,  # Most recent first
                Limit=limit
            )
            
            feedback_items = []
            for item in response.get('Items', []):
                if 'item_type' not in item:  # Only feedback items
                    feedback_item = self._item_to_feedback(item)
                    if feedback_item:
                        feedback_items.append(feedback_item)
            
            return feedback_items
            
        except Exception as e:
            print(f"❌ Error getting feedback by type: {e}")
            return []
    
    def get_low_rated_feedback(self, max_rating: int = 2, limit: int = 100) -> List[FeedbackItem]:
        """
        Get feedback items with low ratings.
        
        Args:
            max_rating: Maximum rating to consider "low"
            limit: Maximum number of items to return
            
        Returns:
            List of low-rated feedback items
        """
        try:
            response = self.db.dynamodb.Table(self.table_name).query(
                IndexName='feedback_type-index',
                KeyConditionExpression='feedback_type = :feedback_type AND rating <= :max_rating',
                ExpressionAttributeValues={
                    ':feedback_type': FeedbackType.RESPONSE_QUALITY.value,
                    ':max_rating': max_rating
                },
                ScanIndexForward=False,  # Most recent first
                Limit=limit
            )
            
            feedback_items = []
            for item in response.get('Items', []):
                if 'item_type' not in item:  # Only feedback items
                    feedback_item = self._item_to_feedback(item)
                    if feedback_item:
                        feedback_items.append(feedback_item)
            
            return feedback_items
            
        except Exception as e:
            print(f"❌ Error getting low-rated feedback: {e}")
            return []
    
    def get_improvement_actions(self, user_id: str = None, status: str = None) -> List[ImprovementAction]:
        """
        Get improvement actions.
        
        Args:
            user_id: Optional user ID filter
            status: Optional status filter
            
        Returns:
            List of improvement actions
        """
        try:
            scan_kwargs = {
                'FilterExpression': 'item_type = :item_type',
                'ExpressionAttributeValues': {':item_type': 'improvement_action'}
            }
            
            if user_id:
                scan_kwargs['FilterExpression'] += ' AND user_id = :user_id'
                scan_kwargs['ExpressionAttributeValues'][':user_id'] = user_id
            
            if status:
                scan_kwargs['FilterExpression'] += ' AND #status = :status'
                scan_kwargs['ExpressionAttributeValues'][':status'] = status
                scan_kwargs['ExpressionAttributeNames'] = {'#status': 'status'}
            
            response = self.db.dynamodb.Table(self.table_name).scan(**scan_kwargs)
            
            actions = []
            for item in response.get('Items', []):
                action = self._item_to_improvement_action(item)
                if action:
                    actions.append(action)
            
            return actions
            
        except Exception as e:
            print(f"❌ Error getting improvement actions: {e}")
            return []
    
    def get_improvement_results(self, action_id: str = None) -> List[ImprovementResult]:
        """
        Get improvement results.
        
        Args:
            action_id: Optional action ID filter
            
        Returns:
            List of improvement results
        """
        try:
            scan_kwargs = {
                'FilterExpression': 'item_type = :item_type',
                'ExpressionAttributeValues': {':item_type': 'improvement_result'}
            }
            
            if action_id:
                scan_kwargs['FilterExpression'] += ' AND action_id = :action_id'
                scan_kwargs['ExpressionAttributeValues'][':action_id'] = action_id
            
            response = self.db.dynamodb.Table(self.table_name).scan(**scan_kwargs)
            
            results = []
            for item in response.get('Items', []):
                result = self._item_to_improvement_result(item)
                if result:
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"❌ Error getting improvement results: {e}")
            return []
    
    def _item_to_feedback(self, item: Dict[str, Any]) -> Optional[FeedbackItem]:
        """Convert DynamoDB item to FeedbackItem."""
        try:
            # Convert string back to enum
            feedback_type = FeedbackType(item['feedback_type'])
            rating = FeedbackRating(item['rating'])
            
            # Convert timestamp string back to datetime
            timestamp = datetime.fromisoformat(item['timestamp'])
            
            # Convert context datetime strings back to datetime objects
            context = item.get('context', {})
            if context:
                for key, value in context.items():
                    if isinstance(value, str) and 'T' in value:
                        try:
                            context[key] = datetime.fromisoformat(value)
                        except:
                            pass  # Keep as string if conversion fails
            
            return FeedbackItem(
                id=item['id'],
                user_id=item['user_id'],
                session_id=item['session_id'],
                timestamp=timestamp,
                feedback_type=feedback_type,
                rating=rating,
                user_message=item['user_message'],
                agent_response=item['agent_response'],
                expected_intent=item.get('expected_intent'),
                actual_intent=item.get('actual_intent'),
                expected_action=item.get('expected_action'),
                actual_action=item.get('actual_action'),
                comments=item.get('comments'),
                context=context,
                evaluation_score=item.get('evaluation_score'),
                improvement_suggestions=item.get('improvement_suggestions', [])
            )
            
        except Exception as e:
            print(f"❌ Error converting item to feedback: {e}")
            return None
    
    def _item_to_improvement_action(self, item: Dict[str, Any]) -> Optional[ImprovementAction]:
        """Convert DynamoDB item to ImprovementAction."""
        try:
            created_at = datetime.fromisoformat(item['timestamp'])
            
            return ImprovementAction(
                id=item['id'],
                action_type=item['action_type'],
                description=item['description'],
                priority=item['priority'],
                target_component=item['target_component'],
                implementation_details=item['implementation_details'],
                expected_impact=item['expected_impact'],
                created_at=created_at,
                status=item.get('status', 'pending')
            )
            
        except Exception as e:
            print(f"❌ Error converting item to improvement action: {e}")
            return None
    
    def _item_to_improvement_result(self, item: Dict[str, Any]) -> Optional[ImprovementResult]:
        """Convert DynamoDB item to ImprovementResult."""
        try:
            completed_at = datetime.fromisoformat(item['timestamp'])
            
            return ImprovementResult(
                action_id=item['action_id'],
                success=item['success'],
                before_metrics=item['before_metrics'],
                after_metrics=item['after_metrics'],
                improvement_percentage=item['improvement_percentage'],
                notes=item.get('notes'),
                completed_at=completed_at
            )
            
        except Exception as e:
            print(f"❌ Error converting item to improvement result: {e}")
            return None
    
    def delete_feedback_item(self, feedback_id: str) -> bool:
        """
        Delete a feedback item from the database.
        
        Args:
            feedback_id: ID of the feedback item to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            self.db.dynamodb.Table(self.table_name).delete_item(
                Key={'id': feedback_id}
            )
            return True
            
        except Exception as e:
            print(f"❌ Error deleting feedback item: {e}")
            return False
    
    def get_feedback_summary(self, user_id: str = None) -> Dict[str, Any]:
        """
        Get a summary of feedback data.
        
        Args:
            user_id: Optional user ID filter
            
        Returns:
            Summary statistics
        """
        try:
            # Get all feedback items
            if user_id:
                feedback_items = self.get_user_feedback(user_id, limit=1000)
            else:
                # For all users, we'd need to scan the table
                response = self.db.dynamodb.Table(self.table_name).scan(
                    FilterExpression='attribute_not_exists(item_type)'
                )
                feedback_items = []
                for item in response.get('Items', []):
                    feedback_item = self._item_to_feedback(item)
                    if feedback_item:
                        feedback_items.append(feedback_item)
            
            if not feedback_items:
                return {
                    "total_feedback": 0,
                    "average_rating": 0.0,
                    "feedback_types": {},
                    "rating_distribution": {}
                }
            
            # Calculate statistics
            total_feedback = len(feedback_items)
            average_rating = sum(item.rating.value for item in feedback_items) / total_feedback
            
            # Feedback type distribution
            feedback_types = {}
            for item in feedback_items:
                feedback_type = item.feedback_type.value
                feedback_types[feedback_type] = feedback_types.get(feedback_type, 0) + 1
            
            # Rating distribution
            rating_distribution = {}
            for item in feedback_items:
                rating = item.rating.value
                rating_distribution[rating] = rating_distribution.get(rating, 0) + 1
            
            return {
                "total_feedback": total_feedback,
                "average_rating": average_rating,
                "feedback_types": feedback_types,
                "rating_distribution": rating_distribution
            }
            
        except Exception as e:
            print(f"❌ Error getting feedback summary: {e}")
            return {
                "total_feedback": 0,
                "average_rating": 0.0,
                "feedback_types": {},
                "rating_distribution": {}
            }
