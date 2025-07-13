"""
Enhanced DynamoDB Service for Remo AI Assistant
Provides user-specific data storage with proper table structure for reminders, todos, and user details.
Uses DynamoDB with optimized table design for NoSQL operations.
"""

import boto3
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError, NoCredentialsError
import json

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Continue without dotenv if not available

class DynamoDBService:
    """
    Enhanced DynamoDB service for Remo AI Assistant.
    Manages user-specific data with proper table structure.
    """
    
    def __init__(self):
        """Initialize DynamoDB service with proper table structure."""
        self.dynamodb = None
        self.reminders_table = None
        self.todos_table = None
        self.users_table = None
        self.conversation_table = None
        self.conversation_context_table = None  # NEW: Table for conversation context
        
        # Initialize DynamoDB client
        try:
            # Try to get credentials from environment
            aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
            aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            aws_region = os.getenv('AWS_REGION', 'us-east-1')
            
            if aws_access_key_id and aws_secret_access_key:
                self.dynamodb = boto3.resource(
                    'dynamodb',
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    region_name=aws_region
                )
            else:
                # Use default credentials (IAM role, AWS CLI config, etc.)
                self.dynamodb = boto3.resource('dynamodb', region_name=aws_region)
            
            # Ensure all tables exist
            self._ensure_tables_exist()
            self._ensure_conversation_context_table()  # NEW: Ensure context table
            
        except NoCredentialsError:
            print("❌ AWS credentials not found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
            self.dynamodb = None
        except Exception as e:
            print(f"❌ Error initializing DynamoDB: {e}")
            self.dynamodb = None
    
    def _ensure_tables_exist(self):
        """Ensure all required tables exist, create them if they don't."""
        if not self.dynamodb:
            return
        try:
            self._ensure_reminders_table()
            self._ensure_todos_table()
            self._ensure_users_table()
            self._ensure_conversation_table()
            self._ensure_emails_table()
            self._ensure_waitlist_table()  # NEW: waitlist table
            self._ensure_data_analyst_reports_table() # NEW: data analyst reports table
            print("✅ All DynamoDB tables are ready")
        except Exception as e:
            print(f"❌ Error ensuring tables exist: {e}")
    
    def _ensure_reminders_table(self):
        """Ensure reminders table exists."""
        table_name = 'remo-reminders'
        
        try:
            self.reminders_table = self.dynamodb.Table(table_name)
            self.reminders_table.load()
            print(f"✅ Reminders table '{table_name}' exists")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"📝 Creating reminders table '{table_name}'...")
                self._create_reminders_table(table_name)
            else:
                raise e
    
    def _create_reminders_table(self, table_name: str):
        """Create reminders table with proper structure."""
        table = self.dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'user_id',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'reminder_id',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'user_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'reminder_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'status',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST',
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'status-index',
                    'KeySchema': [
                        {
                            'AttributeName': 'user_id',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'status',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                }
            ]
        )
        
        # Wait for table to be created
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        self.reminders_table = table
        print(f"✅ Reminders table '{table_name}' created successfully")
    
    def _ensure_todos_table(self):
        """Ensure todos table exists."""
        table_name = 'remo-todos'
        
        try:
            self.todos_table = self.dynamodb.Table(table_name)
            self.todos_table.load()
            print(f"✅ Todos table '{table_name}' exists")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"📝 Creating todos table '{table_name}'...")
                self._create_todos_table(table_name)
            else:
                raise e
    
    def _create_todos_table(self, table_name: str):
        """Create todos table with proper structure."""
        table = self.dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'user_id',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'todo_id',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'user_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'todo_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'status',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'priority',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST',
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'status-index',
                    'KeySchema': [
                        {
                            'AttributeName': 'user_id',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'status',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                },
                {
                    'IndexName': 'priority-index',
                    'KeySchema': [
                        {
                            'AttributeName': 'user_id',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'priority',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                }
            ]
        )
        
        # Wait for table to be created
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        self.todos_table = table
        print(f"✅ Todos table '{table_name}' created successfully")
    
    def _ensure_users_table(self):
        """Ensure users table exists."""
        table_name = 'remo-users'
        
        try:
            self.users_table = self.dynamodb.Table(table_name)
            self.users_table.load()
            print(f"✅ Users table '{table_name}' exists")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"📝 Creating users table '{table_name}'...")
                self._create_users_table(table_name)
            else:
                raise e
    
    def _create_users_table(self, table_name: str):
        """Create users table with proper structure."""
        table = self.dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'privy_id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'privy_id',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Wait for table to be created
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        self.users_table = table
        print(f"✅ Users table '{table_name}' created successfully")
    
    def _ensure_conversation_table(self):
        """Ensure conversation table exists."""
        table_name = 'remo-conversations'
        
        try:
            self.conversation_table = self.dynamodb.Table(table_name)
            self.conversation_table.load()
            print(f"✅ Conversations table '{table_name}' exists")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"📝 Creating conversations table '{table_name}'...")
                self._create_conversation_table(table_name)
            else:
                raise e
    
    def _create_conversation_table(self, table_name: str):
        """Create conversation table with proper structure."""
        table = self.dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'user_id',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'timestamp',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'user_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'timestamp',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Wait for table to be created
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        self.conversation_table = table
        print(f"✅ Conversations table '{table_name}' created successfully")
        
        # Enable TTL on the table
        try:
            self.dynamodb.meta.client.update_time_to_live(
                TableName=table_name,
                TimeToLiveSpecification={
                    'Enabled': True,
                    'AttributeName': 'ttl'
                }
            )
            print(f"✅ TTL enabled for '{table_name}' on attribute 'ttl'")
        except Exception as e:
            print(f"⚠️  Could not enable TTL for '{table_name}': {e}")
    
    def _ensure_emails_table(self):
        """Ensure emails table exists."""
        table_name = 'remo-emails'
        
        try:
            self.emails_table = self.dynamodb.Table(table_name)
            self.emails_table.load()
            print(f"✅ Emails table '{table_name}' exists")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"📝 Creating emails table '{table_name}'...")
                self._create_emails_table(table_name)
            else:
                raise e
    
    def _create_emails_table(self, table_name: str):
        """Create emails table with proper structure."""
        table = self.dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'user_id',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'email_id',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'user_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'email_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'status',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'priority',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST',
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'status-index',
                    'KeySchema': [
                        {
                            'AttributeName': 'user_id',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'status',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                },
                {
                    'IndexName': 'priority-index',
                    'KeySchema': [
                        {
                            'AttributeName': 'user_id',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'priority',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                }
            ]
        )
        
        # Wait for table to be created
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        self.emails_table = table
        print(f"✅ Emails table '{table_name}' created successfully")
        
        # Enable TTL on the table
        try:
            self.dynamodb.meta.client.update_time_to_live(
                TableName=table_name,
                TimeToLiveSpecification={
                    'Enabled': True,
                    'AttributeName': 'ttl'
                }
            )
            print(f"✅ TTL enabled for '{table_name}' on attribute 'ttl'")
        except Exception as e:
            print(f"⚠️  Could not enable TTL for '{table_name}': {e}")
    
    def _ensure_conversation_context_table(self):
        """Ensure conversation context table exists."""
        table_name = 'remo-conversation-context'
        try:
            self.conversation_context_table = self.dynamodb.Table(table_name)
            self.conversation_context_table.load()
            print(f"✅ Conversation context table '{table_name}' exists")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"📝 Creating conversation context table '{table_name}'...")
                table = self.dynamodb.create_table(
                    TableName=table_name,
                    KeySchema=[
                        {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'user_id', 'AttributeType': 'S'},
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )
                table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
                self.conversation_context_table = table
                print(f"✅ Conversation context table '{table_name}' created successfully")
            else:
                raise e
    
    def _ensure_waitlist_table(self):
        """Ensure waitlist table exists."""
        table_name = 'remo-waitlist'
        try:
            self.waitlist_table = self.dynamodb.Table(table_name)
            self.waitlist_table.load()
            print(f"✅ Waitlist table '{table_name}' exists")
        except Exception as e:
            if hasattr(e, 'response') and e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"📝 Creating waitlist table '{table_name}'...")
                table = self.dynamodb.create_table(
                    TableName=table_name,
                    KeySchema=[
                        {'AttributeName': 'email', 'KeyType': 'HASH'},
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'email', 'AttributeType': 'S'},
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )
                table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
                self.waitlist_table = table
                print(f"✅ Waitlist table '{table_name}' created successfully")
            else:
                print(f"❌ Error ensuring waitlist table: {e}")
                raise e

    def _ensure_data_analyst_reports_table(self):
        """Ensure data analyst reports table exists."""
        table_name = 'remo-data-analyst-reports'
        try:
            self.data_analyst_reports_table = self.dynamodb.Table(table_name)
            self.data_analyst_reports_table.load()
            print(f"✅ Data Analyst Reports table '{table_name}' exists")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"📝 Creating data analyst reports table '{table_name}'...")
                self._create_data_analyst_reports_table(table_name)
            else:
                raise e

    def _create_data_analyst_reports_table(self, table_name: str):
        table = self.dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'report_id', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'report_id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        self.data_analyst_reports_table = table
        print(f"✅ Data Analyst Reports table '{table_name}' created successfully")

    def save_data_analyst_report(self, user_id: str, report_id: str, report_data: dict) -> bool:
        """Save a data analyst report for a user."""
        if not hasattr(self, 'data_analyst_reports_table'):
            self._ensure_data_analyst_reports_table()
        try:
            item = {
                'user_id': user_id,
                'report_id': report_id,
                'created_at': datetime.now().isoformat(),
                'report_data': json.dumps(report_data)
            }
            self.data_analyst_reports_table.put_item(Item=item)
            return True
        except Exception as e:
            print(f"[DynamoDB] Error saving data analyst report: {e}")
            return False

    def get_data_analyst_reports(self, user_id: str, limit: int = 10) -> list:
        """Retrieve data analyst reports for a user."""
        if not hasattr(self, 'data_analyst_reports_table'):
            self._ensure_data_analyst_reports_table()
        try:
            response = self.data_analyst_reports_table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(user_id),
                Limit=limit,
                ScanIndexForward=False
            )
            items = response.get('Items', [])
            for item in items:
                if 'report_data' in item:
                    item['report_data'] = json.loads(item['report_data'])
            return items
        except Exception as e:
            print(f"[DynamoDB] Error retrieving data analyst reports: {e}")
            return []

    # ===== REMINDERS METHODS =====
    
    def save_reminder(self, user_id: str, reminder_data: Dict) -> bool:
        """
        Save a reminder to DynamoDB.
        
        Args:
            user_id: Privy user ID
            reminder_data: Reminder data with structure:
                - reminder_id: Unique identifier
                - title: Reminder title
                - description: Reminder description
                - reminding_time: ISO datetime string
                - status: 'pending', 'done', 'cancelled'
                - created_at: ISO datetime string
        
        Returns:
            True if successful, False otherwise
        """
        if not self.reminders_table:
            print(f"[DynamoDBService] [save_reminder] Table not initialized for user_id={user_id}")
            return False
        
        try:
            item = {
                'user_id': user_id,
                'reminder_id': reminder_data['reminder_id'],
                'title': reminder_data['title'],
                'description': reminder_data.get('description', ''),
                'reminding_time': reminder_data['reminding_time'],
                'status': reminder_data.get('status', 'pending'),
                'created_at': reminder_data['created_at'],
                'updated_at': datetime.now().isoformat(),
                'ttl': int(datetime.now().timestamp()) + (365 * 24 * 60 * 60)  # 1 year TTL
            }
            print(f"[DynamoDBService] [save_reminder] user_id={user_id} item={item}")
            self.reminders_table.put_item(Item=item)
            return True
            
        except Exception as e:
            print(f"[DynamoDBService] Error saving reminder for user_id={user_id}: {e}")
            return False
    
    def get_reminders(self, user_id: str, status: str = None) -> List[Dict]:
        """
        Get reminders for a user, optionally filtered by status.
        
        Args:
            user_id: Privy user ID
            status: Optional status filter ('pending', 'done', 'cancelled')
        
        Returns:
            List of reminder dictionaries
        """
        if not self.reminders_table:
            print(f"[DynamoDBService] [get_reminders] Table not initialized for user_id={user_id}")
            return []
        
        try:
            if status:
                response = self.reminders_table.query(
                    IndexName='status-index',
                    KeyConditionExpression='user_id = :user_id AND #status = :status',
                    ExpressionAttributeNames={'#status': 'status'},
                    ExpressionAttributeValues={
                        ':user_id': user_id,
                        ':status': status
                    }
                )
            else:
                response = self.reminders_table.query(
                    KeyConditionExpression='user_id = :user_id',
                    ExpressionAttributeValues={':user_id': user_id}
                )
            print(f"[DynamoDBService] [get_reminders] user_id={user_id} status={status} items_count={len(response.get('Items', []))}")
            return response.get('Items', [])
            
        except Exception as e:
            print(f"[DynamoDBService] Error getting reminders for user_id={user_id}: {e}")
            return []
    
    def update_reminder_status(self, user_id: str, reminder_id: str, status: str) -> bool:
        """
        Update reminder status.
        
        Args:
            user_id: Privy user ID
            reminder_id: Reminder ID
            status: New status ('pending', 'done', 'cancelled')
        
        Returns:
            True if successful, False otherwise
        """
        if not self.reminders_table:
            print(f"[DynamoDBService] [update_reminder_status] Table not initialized for user_id={user_id}")
            return False
        
        try:
            self.reminders_table.update_item(
                Key={
                    'user_id': user_id,
                    'reminder_id': reminder_id
                },
                UpdateExpression='SET #status = :status, updated_at = :updated_at',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': status,
                    ':updated_at': datetime.now().isoformat()
                }
            )
            print(f"[DynamoDBService] [update_reminder_status] user_id={user_id} reminder_id={reminder_id} status={status}")
            return True
            
        except Exception as e:
            print(f"[DynamoDBService] Error updating reminder status for user_id={user_id}: {e}")
            return False
    
    def delete_reminder(self, user_id: str, reminder_id: str) -> bool:
        """
        Delete a reminder.
        
        Args:
            user_id: Privy user ID
            reminder_id: Reminder ID
        
        Returns:
            True if successful, False otherwise
        """
        if not self.reminders_table:
            print(f"[DynamoDBService] [delete_reminder] Table not initialized for user_id={user_id}")
            return False
        
        try:
            self.reminders_table.delete_item(
                Key={
                    'user_id': user_id,
                    'reminder_id': reminder_id
                }
            )
            print(f"[DynamoDBService] [delete_reminder] user_id={user_id} reminder_id={reminder_id}")
            return True
            
        except Exception as e:
            print(f"[DynamoDBService] Error deleting reminder for user_id={user_id}: {e}")
            return False
    
    # ===== TODOS METHODS =====
    
    def save_todo(self, user_id: str, todo_data: Dict) -> bool:
        """
        Save a todo to DynamoDB.
        
        Args:
            user_id: Privy user ID
            todo_data: Todo data with structure:
                - todo_id: Unique identifier
                - title: Todo title
                - description: Todo description
                - priority: 'low', 'medium', 'high', 'urgent'
                - status: 'pending', 'done', 'cancelled'
                - created_at: ISO datetime string
        
        Returns:
            True if successful, False otherwise
        """
        if not self.todos_table:
            print(f"[DynamoDBService] [save_todo] Table not initialized for user_id={user_id}")
            return False
        
        try:
            item = {
                'user_id': user_id,
                'todo_id': todo_data['todo_id'],
                'title': todo_data['title'],
                'description': todo_data.get('description', ''),
                'priority': todo_data.get('priority', 'medium'),
                'status': todo_data.get('status', 'pending'),
                'created_at': todo_data['created_at'],
                'updated_at': datetime.now().isoformat(),
                'ttl': int(datetime.now().timestamp()) + (365 * 24 * 60 * 60)  # 1 year TTL
            }
            print(f"[DynamoDBService] [save_todo] user_id={user_id} item={item}")
            self.todos_table.put_item(Item=item)
            return True
            
        except Exception as e:
            print(f"[DynamoDBService] Error saving todo for user_id={user_id}: {e}")
            return False
    
    def get_todos(self, user_id: str, status: str = None, priority: str = None) -> List[Dict]:
        """
        Get todos for a user, optionally filtered by status and priority.
        
        Args:
            user_id: Privy user ID
            status: Optional status filter ('pending', 'done', 'cancelled')
            priority: Optional priority filter ('low', 'medium', 'high', 'urgent')
        
        Returns:
            List of todo dictionaries
        """
        if not self.todos_table:
            print(f"[DynamoDBService] [get_todos] Table not initialized for user_id={user_id}")
            return []
        
        try:
            if status:
                response = self.todos_table.query(
                    IndexName='status-index',
                    KeyConditionExpression='user_id = :user_id AND #status = :status',
                    ExpressionAttributeNames={'#status': 'status'},
                    ExpressionAttributeValues={
                        ':user_id': user_id,
                        ':status': status
                    }
                )
            elif priority:
                response = self.todos_table.query(
                    IndexName='priority-index',
                    KeyConditionExpression='user_id = :user_id AND #priority = :priority',
                    ExpressionAttributeNames={'#priority': 'priority'},
                    ExpressionAttributeValues={
                        ':user_id': user_id,
                        ':priority': priority
                    }
                )
            else:
                response = self.todos_table.query(
                    KeyConditionExpression='user_id = :user_id',
                    ExpressionAttributeValues={':user_id': user_id}
                )
            print(f"[DynamoDBService] [get_todos] user_id={user_id} status={status} priority={priority} items_count={len(response.get('Items', []))}")
            return response.get('Items', [])
            
        except Exception as e:
            print(f"[DynamoDBService] Error getting todos for user_id={user_id}: {e}")
            return []
    
    def update_todo_status(self, user_id: str, todo_id: str, status: str) -> bool:
        """
        Update todo status.
        
        Args:
            user_id: Privy user ID
            todo_id: Todo ID
            status: New status ('pending', 'done', 'cancelled')
        
        Returns:
            True if successful, False otherwise
        """
        if not self.todos_table:
            print(f"[DynamoDBService] [update_todo_status] Table not initialized for user_id={user_id}")
            return False
        
        try:
            self.todos_table.update_item(
                Key={
                    'user_id': user_id,
                    'todo_id': todo_id
                },
                UpdateExpression='SET #status = :status, updated_at = :updated_at',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': status,
                    ':updated_at': datetime.now().isoformat()
                }
            )
            print(f"[DynamoDBService] [update_todo_status] user_id={user_id} todo_id={todo_id} status={status}")
            return True
            
        except Exception as e:
            print(f"[DynamoDBService] Error updating todo status for user_id={user_id}: {e}")
            return False
    
    def delete_todo(self, user_id: str, todo_id: str) -> bool:
        """
        Delete a todo.
        
        Args:
            user_id: Privy user ID
            todo_id: Todo ID
        
        Returns:
            True if successful, False otherwise
        """
        if not self.todos_table:
            print(f"[DynamoDBService] [delete_todo] Table not initialized for user_id={user_id}")
            return False
        
        try:
            self.todos_table.delete_item(
                Key={
                    'user_id': user_id,
                    'todo_id': todo_id
                }
            )
            print(f"[DynamoDBService] [delete_todo] user_id={user_id} todo_id={todo_id}")
            return True
            
        except Exception as e:
            print(f"[DynamoDBService] Error deleting todo for user_id={user_id}: {e}")
            return False
    
    # ===== USER DETAILS METHODS =====
    
    def save_user_details(self, user_data: Dict) -> bool:
        """
        Save user details to DynamoDB.
        
        Args:
            user_data: User data with structure:
                - privy_id: Privy user ID
                - email: User email
                - wallet: Wallet address (optional)
                - first_name: First name
                - last_name: Last name
                - phone_number: Phone number (optional)
        
        Returns:
            True if successful, False otherwise
        """
        if not self.users_table:
            print(f"[DynamoDBService] [save_user_details] Table not initialized for privy_id={user_data.get('privy_id')}")
            return False
        
        try:
            item = {
                'privy_id': user_data['privy_id'],
                'email': user_data.get('email', ''),
                'wallet': user_data.get('wallet', ''),
                'first_name': user_data.get('first_name', ''),
                'last_name': user_data.get('last_name', ''),
                'phone_number': user_data.get('phone_number', ''),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            print(f"[DynamoDBService] [save_user_details] privy_id={user_data['privy_id']} item={item}")
            self.users_table.put_item(Item=item)
            return True
            
        except Exception as e:
            print(f"[DynamoDBService] Error saving user details for privy_id={user_data.get('privy_id')}: {e}")
            return False
    
    def get_user_details(self, privy_id: str) -> Optional[Dict]:
        """
        Get user details by Privy ID.
        
        Args:
            privy_id: Privy user ID
        
        Returns:
            User details dictionary or None if not found
        """
        if not self.users_table:
            print(f"[DynamoDBService] [get_user_details] Table not initialized for privy_id={privy_id}")
            return None
        
        try:
            response = self.users_table.get_item(Key={'privy_id': privy_id})
            print(f"[DynamoDBService] [get_user_details] privy_id={privy_id} found={bool(response.get('Item'))}")
            return response.get('Item')
            
        except Exception as e:
            print(f"[DynamoDBService] Error getting user details for privy_id={privy_id}: {e}")
            return None
    
    # ===== CONVERSATION MEMORY METHODS =====
    
    def save_conversation_message(self, user_id: str, message_data: Dict) -> bool:
        """
        Save a conversation message to DynamoDB.
        
        Args:
            user_id: Privy user ID
            message_data: Message data with structure:
                - role: 'user' or 'assistant'
                - content: Message content
                - timestamp: ISO datetime string
        
        Returns:
            True if successful, False otherwise
        """
        if not self.conversation_table:
            return False
        
        try:
            item = {
                'user_id': user_id,
                'timestamp': message_data['timestamp'],
                'role': message_data['role'],
                'content': message_data['content'],
                'ttl': int(datetime.now().timestamp()) + (30 * 24 * 60 * 60)  # 30 days TTL
            }
            
            self.conversation_table.put_item(Item=item)
            return True
            
        except Exception as e:
            print(f"Error saving conversation message: {e}")
            return False
    
    def get_conversation_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """
        Get conversation history for a user.
        
        Args:
            user_id: Privy user ID
            limit: Maximum number of messages to return
        
        Returns:
            List of conversation messages
        """
        if not self.conversation_table:
            return []
        
        try:
            response = self.conversation_table.query(
                KeyConditionExpression='user_id = :user_id',
                ExpressionAttributeValues={':user_id': user_id},
                ScanIndexForward=False,  # Get most recent first
                Limit=limit
            )
            
            # Reverse to get chronological order
            messages = response.get('Items', [])
            messages.reverse()
            return messages
            
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []
    
    # ===== LEGACY COMPATIBILITY METHODS =====
    
    def save_reminder_data(self, user_id: str, reminder_data: Dict) -> bool:
        """Legacy method for backward compatibility."""
        if 'reminders' in reminder_data:
            for reminder in reminder_data['reminders']:
                if 'id' in reminder:
                    reminder['reminder_id'] = reminder['id']
                if 'datetime' in reminder:
                    reminder['reminding_time'] = reminder['datetime']
                if 'created' in reminder:
                    reminder['created_at'] = reminder['created']
                if 'completed' in reminder:
                    reminder['status'] = 'done' if reminder['completed'] else 'pending'
                
                self.save_reminder(user_id, reminder)
        return True
    
    def load_reminder_data(self, user_id: str) -> Optional[Dict]:
        """Legacy method for backward compatibility."""
        reminders = self.get_reminders(user_id)
        return {'reminders': reminders} if reminders else None
    
    def save_todo_data(self, user_id: str, todo_data: Dict) -> bool:
        """Legacy method for backward compatibility."""
        if 'todos' in todo_data:
            for todo in todo_data['todos']:
                if 'id' in todo:
                    todo['todo_id'] = todo['id']
                if 'created' in todo:
                    todo['created_at'] = todo['created']
                if 'completed' in todo:
                    todo['status'] = 'done' if todo['completed'] else 'pending'
                
                self.save_todo(user_id, todo)
        return True
    
    def load_todo_data(self, user_id: str) -> Optional[Dict]:
        """Legacy method for backward compatibility."""
        todos = self.get_todos(user_id)
        return {'todos': todos} if todos else None
    
    def save_conversation_memory(self, user_id: str, conversation_data: Dict) -> bool:
        """Legacy method for backward compatibility."""
        if 'messages' in conversation_data:
            for message in conversation_data['messages']:
                self.save_conversation_message(user_id, message)
        return True
    
    def load_conversation_memory(self, user_id: str) -> Optional[Dict]:
        """Legacy method for backward compatibility."""
        messages = self.get_conversation_history(user_id)
        return {'messages': messages} if messages else None
    
    def save_conversation_context(self, user_id: str, context_data: Dict) -> bool:
        """
        Save conversation context to DynamoDB (now in its own table).
        """
        if not self.conversation_context_table:
            print(f"[DynamoDBService] [save_conversation_context] Table not initialized for user_id={user_id}")
            return False
        try:
            # Clean, compact log for conversation context
            summary = {
                'user_id': user_id,
                'current_state': context_data.get('current_state'),
                'active_agent': context_data.get('active_agent'),
                'conversation_topic': context_data.get('conversation_topic'),
                'last_user_intent': context_data.get('last_user_intent'),
                'keywords': context_data.get('context_keywords'),
                'history_len': len(context_data.get('agent_interaction_history', [])),
            }
            item = {
                'user_id': user_id,
                'conversation_context': context_data,
                'updated_at': datetime.now().isoformat(),
                'ttl': int(datetime.now().timestamp()) + (30 * 24 * 60 * 60)  # 30 days TTL
            }
            self.conversation_context_table.put_item(Item=item)
            return True
        except Exception as e:
            print(f"[DynamoDBService] Error saving conversation context for user_id={user_id}: {e}")
            return False

    def load_conversation_context(self, user_id: str) -> Optional[Dict]:
        """
        Load conversation context from DynamoDB (now in its own table).
        """
        if not self.conversation_context_table:
            print(f"[DynamoDBService] [load_conversation_context] Table not initialized for user_id={user_id}")
            return None
        try:
            response = self.conversation_context_table.get_item(Key={'user_id': user_id})
            if 'Item' in response:
                return response['Item'].get('conversation_context')
            return None
        except Exception as e:
            print(f"[DynamoDBService] Error loading conversation context for user_id={user_id}: {e}")
            return None
    
    # ===== UTILITY METHODS =====
    
    def get_user_data_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get a summary of all data stored for a user.
        
        Args:
            user_id: Privy user ID
        
        Returns:
            Dictionary with data summary
        """
        try:
            reminders = self.get_reminders(user_id)
            todos = self.get_todos(user_id)
            conversation_messages = self.get_conversation_history(user_id, limit=10)
            
            summary = {
                'user_id': user_id,
                'data_types': [],
                'total_items': 0,
                'last_updated': None
            }
            
            if reminders:
                summary['data_types'].append('reminders')
                summary['total_items'] += len(reminders)
            
            if todos:
                summary['data_types'].append('todos')
                summary['total_items'] += len(todos)
            
            if conversation_messages:
                summary['data_types'].append('conversations')
                summary['total_items'] += len(conversation_messages)
            
            return summary
            
        except Exception as e:
            print(f"Error getting user data summary: {e}")
            return {}
    
    def delete_user_data(self, user_id: str, data_type: str = None) -> bool:
        """
        Delete user data for a specific user and data type.
        
        Args:
            user_id: Privy user ID
            data_type: Specific data type to delete (optional, deletes all if None)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if data_type == 'reminders' or data_type is None:
                reminders = self.get_reminders(user_id)
                for reminder in reminders:
                    self.delete_reminder(user_id, reminder['reminder_id'])
            
            if data_type == 'todos' or data_type is None:
                todos = self.get_todos(user_id)
                for todo in todos:
                    self.delete_todo(user_id, todo['todo_id'])
            
            if data_type == 'emails' or data_type is None:
                emails = self.get_emails(user_id)
                for email in emails:
                    self.delete_email(user_id, email['email_id'])
            
            if data_type == 'conversations' or data_type is None:
                # For conversations, we'll let TTL handle cleanup
                pass
            
            return True
            
        except Exception as e:
            print(f"Error deleting user data: {e}")
            return False
    
    # ===== EMAIL METHODS =====
    
    def save_email_draft(self, user_id: str, email_data: Dict) -> bool:
        """
        Save an email draft to DynamoDB.
        
        Args:
            user_id: Privy user ID
            email_data: Email data with structure:
                - email_id: Unique identifier
                - to_recipients: List of recipients
                - subject: Email subject
                - body: Email body
                - cc_recipients: List of CC recipients (optional)
                - bcc_recipients: List of BCC recipients (optional)
                - attachments: List of attachments (optional)
                - status: 'draft', 'sent', 'scheduled'
                - created_at: ISO datetime string
        
        Returns:
            True if successful, False otherwise
        """
        if not self.emails_table:
            return False
        
        try:
            item = {
                'user_id': user_id,
                'email_id': email_data['email_id'],
                'to_recipients': email_data['to_recipients'],
                'subject': email_data['subject'],
                'body': email_data['body'],
                'cc_recipients': email_data.get('cc_recipients', []),
                'bcc_recipients': email_data.get('bcc_recipients', []),
                'attachments': email_data.get('attachments', []),
                'status': email_data.get('status', 'draft'),
                'priority': email_data.get('priority', 'medium'),
                'created_at': email_data['created_at'],
                'updated_at': datetime.now().isoformat(),
                'ttl': int(datetime.now().timestamp()) + (365 * 24 * 60 * 60)  # 1 year TTL
            }
            
            self.emails_table.put_item(Item=item)
            return True
            
        except Exception as e:
            print(f"Error saving email draft: {e}")
            return False
    
    def get_email_draft(self, user_id: str, email_id: str) -> Optional[Dict]:
        """
        Get an email draft by ID.
        
        Args:
            user_id: Privy user ID
            email_id: Email ID
        
        Returns:
            Email data dictionary or None
        """
        if not self.emails_table:
            return None
        
        try:
            response = self.emails_table.get_item(
                Key={
                    'user_id': user_id,
                    'email_id': email_id
                }
            )
            
            return response.get('Item')
            
        except Exception as e:
            print(f"Error getting email draft: {e}")
            return None
    
    def get_emails(self, user_id: str, status: str = None, priority: str = None) -> List[Dict]:
        """
        Get emails for a user, optionally filtered by status and priority.
        
        Args:
            user_id: Privy user ID
            status: Optional status filter ('draft', 'sent', 'scheduled')
            priority: Optional priority filter ('low', 'medium', 'high', 'urgent')
        
        Returns:
            List of email dictionaries
        """
        if not self.emails_table:
            return []
        
        try:
            if status:
                # Use status GSI
                response = self.emails_table.query(
                    IndexName='status-index',
                    KeyConditionExpression='user_id = :user_id AND #status = :status',
                    ExpressionAttributeNames={'#status': 'status'},
                    ExpressionAttributeValues={
                        ':user_id': user_id,
                        ':status': status
                    }
                )
            elif priority:
                # Use priority GSI
                response = self.emails_table.query(
                    IndexName='priority-index',
                    KeyConditionExpression='user_id = :user_id AND #priority = :priority',
                    ExpressionAttributeNames={'#priority': 'priority'},
                    ExpressionAttributeValues={
                        ':user_id': user_id,
                        ':priority': priority
                    }
                )
            else:
                # Get all emails for user
                response = self.emails_table.query(
                    KeyConditionExpression='user_id = :user_id',
                    ExpressionAttributeValues={':user_id': user_id}
                )
            
            return response.get('Items', [])
            
        except Exception as e:
            print(f"Error getting emails: {e}")
            return []
    
    def update_email_status(self, user_id: str, email_id: str, status: str) -> bool:
        """
        Update email status.
        
        Args:
            user_id: Privy user ID
            email_id: Email ID
            status: New status ('draft', 'sent', 'scheduled')
        
        Returns:
            True if successful, False otherwise
        """
        if not self.emails_table:
            return False
        
        try:
            self.emails_table.update_item(
                Key={
                    'user_id': user_id,
                    'email_id': email_id
                },
                UpdateExpression='SET #status = :status, updated_at = :updated_at',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': status,
                    ':updated_at': datetime.now().isoformat()
                }
            )
            return True
            
        except Exception as e:
            print(f"Error updating email status: {e}")
            return False
    
    def delete_email(self, user_id: str, email_id: str) -> bool:
        """
        Delete an email.
        
        Args:
            user_id: Privy user ID
            email_id: Email ID
        
        Returns:
            True if successful, False otherwise
        """
        if not self.emails_table:
            return False
        
        try:
            self.emails_table.delete_item(
                Key={
                    'user_id': user_id,
                    'email_id': email_id
                }
            )
            return True
            
        except Exception as e:
            print(f"Error deleting email: {e}")
            return False
    
    def save_scheduled_email(self, user_id: str, scheduled_data: Dict) -> bool:
        """
        Save a scheduled email.
        
        Args:
            user_id: Privy user ID
            scheduled_data: Scheduled email data
        
        Returns:
            True if successful, False otherwise
        """
        if not self.emails_table:
            return False
        
        try:
            item = {
                'user_id': user_id,
                'email_id': scheduled_data['email_id'],
                'scheduled_time': scheduled_data['scheduled_time'],
                'status': 'scheduled',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'ttl': int(datetime.now().timestamp()) + (365 * 24 * 60 * 60)  # 1 year TTL
            }
            
            self.emails_table.put_item(Item=item)
            return True
            
        except Exception as e:
            print(f"Error saving scheduled email: {e}")
            return False

    def save_meeting(self, user_id: str, meeting_data: Dict) -> bool:
        """
        Save a meeting to the emails table (since meetings are related to calendar/email functionality).
        
        Args:
            user_id: Privy user ID
            meeting_data: Meeting data dictionary
        
        Returns:
            True if successful, False otherwise
        """
        if not self.emails_table:
            return False
        
        try:
            item = {
                'user_id': user_id,
                'email_id': meeting_data['meeting_id'],  # Use meeting_id as email_id for consistency
                'meeting_type': 'calendar_event',
                'attendees': meeting_data['attendees'],
                'subject': meeting_data['subject'],
                'body': meeting_data.get('description', ''),
                'date': meeting_data['date'],
                'time': meeting_data['time'],
                'duration': meeting_data['duration'],
                'location': meeting_data.get('location', ''),
                'status': meeting_data.get('status', 'scheduled'),
                'created_at': meeting_data['created_at'],
                'updated_at': datetime.now().isoformat(),
                'ttl': int(datetime.now().timestamp()) + (365 * 24 * 60 * 60)  # 1 year TTL
            }
            
            self.emails_table.put_item(Item=item)
            return True
            
        except Exception as e:
            print(f"Error saving meeting: {e}")
            return False

    def save_google_credentials(self, user_id: str, credentials: dict, google_email: str) -> bool:
        """
        Save Google OAuth credentials and email to the users table.
        """
        if not self.users_table:
            return False
        try:
            item = {
                'privy_id': user_id,
                'google_credentials': json.dumps(credentials),
                'google_email': google_email,
                'updated_at': datetime.now().isoformat()
            }
            self.users_table.put_item(Item=item)
            return True
        except Exception as e:
            print(f"Error saving Google credentials: {e}")
            return False

    def get_google_credentials(self, user_id: str) -> Optional[dict]:
        """
        Retrieve Google OAuth credentials for a user from the users table.
        """
        if not self.users_table:
            return None
        try:
            response = self.users_table.get_item(Key={'privy_id': user_id})
            item = response.get('Item')
            if item and 'google_credentials' in item:
                return json.loads(item['google_credentials'])
            return None
        except Exception as e:
            print(f"Error retrieving Google credentials: {e}")
            return None

    def delete_google_credentials(self, user_id: str) -> bool:
        """
        Delete Google OAuth credentials and email for a user from the users table.
        """
        if not self.users_table:
            return False
        try:
            self.users_table.update_item(
                Key={'privy_id': user_id},
                UpdateExpression="REMOVE google_credentials, google_email"
            )
            return True
        except Exception as e:
            print(f"Error deleting Google credentials: {e}")
            return False

    # Account deletion methods
    def delete_user_reminders(self, user_id: str) -> bool:
        """Delete all reminders for a user."""
        try:
            if not self.reminders_table:
                return False
            
            # Get all reminders for the user
            response = self.reminders_table.query(
                KeyConditionExpression='user_id = :user_id',
                ExpressionAttributeValues={':user_id': user_id}
            )
            
            # Delete each reminder
            with self.reminders_table.batch_writer() as batch:
                for item in response.get('Items', []):
                    batch.delete_item(
                        Key={
                            'user_id': item['user_id'],
                            'reminder_id': item['reminder_id']
                        }
                    )
            
            print(f"✅ Deleted all reminders for user: {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting user reminders: {e}")
            return False

    def delete_user_todos(self, user_id: str) -> bool:
        """Delete all todos for a user."""
        try:
            if not self.todos_table:
                return False
            
            # Get all todos for the user
            response = self.todos_table.query(
                KeyConditionExpression='user_id = :user_id',
                ExpressionAttributeValues={':user_id': user_id}
            )
            
            # Delete each todo
            with self.todos_table.batch_writer() as batch:
                for item in response.get('Items', []):
                    batch.delete_item(
                        Key={
                            'user_id': item['user_id'],
                            'todo_id': item['todo_id']
                        }
                    )
            
            print(f"✅ Deleted all todos for user: {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting user todos: {e}")
            return False

    def delete_user_conversations(self, user_id: str) -> bool:
        """Delete all conversations for a user."""
        try:
            if not self.conversation_table:
                return False
            
            # Get all conversations for the user
            response = self.conversation_table.query(
                KeyConditionExpression='user_id = :user_id',
                ExpressionAttributeValues={':user_id': user_id}
            )
            
            # Delete each conversation
            with self.conversation_table.batch_writer() as batch:
                for item in response.get('Items', []):
                    batch.delete_item(
                        Key={
                            'user_id': item['user_id'],
                            'timestamp': item['timestamp']
                        }
                    )
            
            print(f"✅ Deleted all conversations for user: {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting user conversations: {e}")
            return False

    def delete_user_conversation_context(self, user_id: str) -> bool:
        """Delete conversation context for a user."""
        try:
            if not self.conversation_context_table:
                return False
            
            # Delete the context entry
            response = self.conversation_context_table.delete_item(
                Key={'user_id': user_id}
            )
            
            print(f"✅ Deleted conversation context for user: {user_id}")
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"⚠️ No conversation context found for user: {user_id}")
                return False
            else:
                print(f"❌ Error deleting conversation context: {e}")
                return False
        except Exception as e:
            print(f"❌ Error deleting conversation context: {e}")
            return False

    def delete_user_preferences(self, user_id: str) -> bool:
        """Delete user preferences."""
        try:
            if not self.users_table:
                return False
            
            # Update user record to remove preferences
            response = self.users_table.update_item(
                Key={'privy_id': user_id},
                UpdateExpression='REMOVE preferences',
                ConditionExpression='attribute_exists(privy_id)'
            )
            
            print(f"✅ Deleted preferences for user: {user_id}")
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                print(f"⚠️ No user preferences found for user: {user_id}")
                return False
            else:
                print(f"❌ Error deleting user preferences: {e}")
                return False
        except Exception as e:
            print(f"❌ Error deleting user preferences: {e}")
            return False

    def delete_user_feedback(self, user_id: str) -> bool:
        """Delete all feedback for a user."""
        try:
            # This would require a feedback table - for now, return True
            # as feedback deletion is not critical for account deletion
            print(f"✅ Feedback deletion not implemented for user: {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting user feedback: {e}")
            return False

    def delete_user_profile(self, user_id: str) -> bool:
        """Delete user profile from users table."""
        try:
            if not self.users_table:
                return False
            
            # Delete the user profile
            response = self.users_table.delete_item(
                Key={'privy_id': user_id}
            )
            
            print(f"✅ Deleted user profile for user: {user_id}")
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"⚠️ No user profile found for user: {user_id}")
                return False
            else:
                print(f"❌ Error deleting user profile: {e}")
                return False
        except Exception as e:
            print(f"❌ Error deleting user profile: {e}")
            return False

    def save_waitlist_entry(self, email: str, name: str, timestamp: str) -> bool:
        """Save a waitlist entry."""
        if not hasattr(self, 'waitlist_table') or not self.waitlist_table:
            print("[DynamoDBService] Waitlist table not initialized")
            return False
        try:
            item = {
                'email': email,
                'name': name,
                'timestamp': timestamp
            }
            self.waitlist_table.put_item(Item=item)
            print(f"[DynamoDBService] Saved waitlist entry: {item}")
            return True
        except Exception as e:
            print(f"[DynamoDBService] Error saving waitlist entry: {e}")
            return False

    def get_waitlist_entries(self) -> list:
        """Get all waitlist entries."""
        if not hasattr(self, 'waitlist_table') or not self.waitlist_table:
            print("[DynamoDBService] Waitlist table not initialized")
            return []
        try:
            response = self.waitlist_table.scan()
            return response.get('Items', [])
        except Exception as e:
            print(f"[DynamoDBService] Error getting waitlist entries: {e}")
            return []

dynamodb_service_singleton = DynamoDBService() 