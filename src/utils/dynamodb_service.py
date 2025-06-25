"""
DynamoDB Service for Remo
Handles user-specific data storage and retrieval using DynamoDB.
"""

import boto3
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

load_dotenv()

class DynamoDBService:
    """
    Service class for DynamoDB operations in Remo.
    Handles user-specific conversation memory, context, and preferences.
    """
    
    def __init__(self):
        """Initialize DynamoDB service with credentials from environment."""
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        self.table_name = os.getenv('DYNAMODB_TABLE_NAME', 'remo-user-data')
        
        # Initialize DynamoDB client
        try:
            self.dynamodb = boto3.resource(
                'dynamodb',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.aws_region
            )
            self.table = self.dynamodb.Table(self.table_name)
            self._ensure_table_exists()
        except NoCredentialsError:
            print("Warning: AWS credentials not found. DynamoDB operations will fail.")
            self.table = None
        except Exception as e:
            print(f"Error initializing DynamoDB: {e}")
            self.table = None
    
    def _ensure_table_exists(self):
        """Ensure the DynamoDB table exists, create if it doesn't."""
        try:
            self.table.load()
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                self._create_table()
            else:
                raise e
    
    def _create_table(self):
        """Create the DynamoDB table with proper schema."""
        try:
            table = self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {
                        'AttributeName': 'user_id',
                        'KeyType': 'HASH'  # Partition key
                    },
                    {
                        'AttributeName': 'data_type',
                        'KeyType': 'RANGE'  # Sort key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'user_id',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'data_type',
                        'AttributeType': 'S'
                    }
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            
            # Wait for table to be created
            table.meta.client.get_waiter('table_exists').wait(TableName=self.table_name)
            print(f"Created DynamoDB table: {self.table_name}")
            
        except Exception as e:
            print(f"Error creating table: {e}")
    
    def save_conversation_memory(self, user_id: str, conversation_data: Dict) -> bool:
        """
        Save conversation memory for a specific user.
        
        Args:
            user_id: Privy user ID
            conversation_data: Conversation memory data
            
        Returns:
            True if successful, False otherwise
        """
        if not self.table:
            return False
        
        try:
            item = {
                'user_id': user_id,
                'data_type': 'conversation_memory',
                'data': conversation_data,
                'timestamp': datetime.now().isoformat(),
                'ttl': int(datetime.now().timestamp()) + (30 * 24 * 60 * 60)  # 30 days TTL
            }
            
            self.table.put_item(Item=item)
            return True
            
        except Exception as e:
            print(f"Error saving conversation memory: {e}")
            return False
    
    def load_conversation_memory(self, user_id: str) -> Optional[Dict]:
        """
        Load conversation memory for a specific user.
        
        Args:
            user_id: Privy user ID
            
        Returns:
            Conversation memory data or None if not found
        """
        if not self.table:
            return None
        
        try:
            response = self.table.get_item(
                Key={
                    'user_id': user_id,
                    'data_type': 'conversation_memory'
                }
            )
            
            if 'Item' in response:
                return response['Item']['data']
            return None
            
        except Exception as e:
            print(f"Error loading conversation memory: {e}")
            return None
    
    def save_conversation_context(self, user_id: str, context_data: Dict) -> bool:
        """
        Save conversation context for a specific user.
        
        Args:
            user_id: Privy user ID
            context_data: Conversation context data
            
        Returns:
            True if successful, False otherwise
        """
        if not self.table:
            return False
        
        try:
            item = {
                'user_id': user_id,
                'data_type': 'conversation_context',
                'data': context_data,
                'timestamp': datetime.now().isoformat(),
                'ttl': int(datetime.now().timestamp()) + (30 * 24 * 60 * 60)  # 30 days TTL
            }
            
            self.table.put_item(Item=item)
            return True
            
        except Exception as e:
            print(f"Error saving conversation context: {e}")
            return False
    
    def load_conversation_context(self, user_id: str) -> Optional[Dict]:
        """
        Load conversation context for a specific user.
        
        Args:
            user_id: Privy user ID
            
        Returns:
            Conversation context data or None if not found
        """
        if not self.table:
            return None
        
        try:
            response = self.table.get_item(
                Key={
                    'user_id': user_id,
                    'data_type': 'conversation_context'
                }
            )
            
            if 'Item' in response:
                return response['Item']['data']
            return None
            
        except Exception as e:
            print(f"Error loading conversation context: {e}")
            return None
    
    def save_user_preferences(self, user_id: str, preferences: Dict) -> bool:
        """
        Save user preferences for a specific user.
        
        Args:
            user_id: Privy user ID
            preferences: User preferences data
            
        Returns:
            True if successful, False otherwise
        """
        if not self.table:
            return False
        
        try:
            item = {
                'user_id': user_id,
                'data_type': 'user_preferences',
                'data': preferences,
                'timestamp': datetime.now().isoformat(),
                'ttl': int(datetime.now().timestamp()) + (365 * 24 * 60 * 60)  # 1 year TTL
            }
            
            self.table.put_item(Item=item)
            return True
            
        except Exception as e:
            print(f"Error saving user preferences: {e}")
            return False
    
    def load_user_preferences(self, user_id: str) -> Optional[Dict]:
        """
        Load user preferences for a specific user.
        
        Args:
            user_id: Privy user ID
            
        Returns:
            User preferences data or None if not found
        """
        if not self.table:
            return None
        
        try:
            response = self.table.get_item(
                Key={
                    'user_id': user_id,
                    'data_type': 'user_preferences'
                }
            )
            
            if 'Item' in response:
                return response['Item']['data']
            return None
            
        except Exception as e:
            print(f"Error loading user preferences: {e}")
            return None
    
    def save_reminder_data(self, user_id: str, reminder_data: Dict) -> bool:
        """
        Save reminder data for a specific user.
        
        Args:
            user_id: Privy user ID
            reminder_data: Reminder data
            
        Returns:
            True if successful, False otherwise
        """
        if not self.table:
            return False
        
        try:
            item = {
                'user_id': user_id,
                'data_type': 'reminder_data',
                'data': reminder_data,
                'timestamp': datetime.now().isoformat(),
                'ttl': int(datetime.now().timestamp()) + (365 * 24 * 60 * 60)  # 1 year TTL
            }
            
            self.table.put_item(Item=item)
            return True
            
        except Exception as e:
            print(f"Error saving reminder data: {e}")
            return False
    
    def load_reminder_data(self, user_id: str) -> Optional[Dict]:
        """
        Load reminder data for a specific user.
        
        Args:
            user_id: Privy user ID
            
        Returns:
            Reminder data or None if not found
        """
        if not self.table:
            return None
        
        try:
            response = self.table.get_item(
                Key={
                    'user_id': user_id,
                    'data_type': 'reminder_data'
                }
            )
            
            if 'Item' in response:
                return response['Item']['data']
            return None
            
        except Exception as e:
            print(f"Error loading reminder data: {e}")
            return None
    
    def save_todo_data(self, user_id: str, todo_data: Dict) -> bool:
        """
        Save todo data for a specific user.
        
        Args:
            user_id: Privy user ID
            todo_data: Todo data
            
        Returns:
            True if successful, False otherwise
        """
        if not self.table:
            return False
        
        try:
            item = {
                'user_id': user_id,
                'data_type': 'todo_data',
                'data': todo_data,
                'timestamp': datetime.now().isoformat(),
                'ttl': int(datetime.now().timestamp()) + (365 * 24 * 60 * 60)  # 1 year TTL
            }
            
            self.table.put_item(Item=item)
            return True
            
        except Exception as e:
            print(f"Error saving todo data: {e}")
            return False
    
    def load_todo_data(self, user_id: str) -> Optional[Dict]:
        """
        Load todo data for a specific user.
        
        Args:
            user_id: Privy user ID
            
        Returns:
            Todo data or None if not found
        """
        if not self.table:
            return None
        
        try:
            response = self.table.get_item(
                Key={
                    'user_id': user_id,
                    'data_type': 'todo_data'
                }
            )
            
            if 'Item' in response:
                return response['Item']['data']
            return None
            
        except Exception as e:
            print(f"Error loading todo data: {e}")
            return None
    
    def delete_user_data(self, user_id: str, data_type: str = None) -> bool:
        """
        Delete user data for a specific user and data type.
        
        Args:
            user_id: Privy user ID
            data_type: Specific data type to delete (optional, deletes all if None)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.table:
            return False
        
        try:
            if data_type:
                # Delete specific data type
                self.table.delete_item(
                    Key={
                        'user_id': user_id,
                        'data_type': data_type
                    }
                )
            else:
                # Delete all data for user
                response = self.table.query(
                    KeyConditionExpression='user_id = :user_id',
                    ExpressionAttributeValues={':user_id': user_id}
                )
                
                for item in response['Items']:
                    self.table.delete_item(
                        Key={
                            'user_id': user_id,
                            'data_type': item['data_type']
                        }
                    )
            
            return True
            
        except Exception as e:
            print(f"Error deleting user data: {e}")
            return False
    
    def get_user_data_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get a summary of all data stored for a user.
        
        Args:
            user_id: Privy user ID
            
        Returns:
            Dictionary with data summary
        """
        if not self.table:
            return {}
        
        try:
            response = self.table.query(
                KeyConditionExpression='user_id = :user_id',
                ExpressionAttributeValues={':user_id': user_id}
            )
            
            summary = {
                'user_id': user_id,
                'data_types': [],
                'total_items': len(response['Items']),
                'last_updated': None
            }
            
            for item in response['Items']:
                summary['data_types'].append(item['data_type'])
                if not summary['last_updated'] or item['timestamp'] > summary['last_updated']:
                    summary['last_updated'] = item['timestamp']
            
            return summary
            
        except Exception as e:
            print(f"Error getting user data summary: {e}")
            return {} 