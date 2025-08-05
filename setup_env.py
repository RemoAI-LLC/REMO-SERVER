#!/usr/bin/env python3
"""
Environment Variables Setup Script for REMO-SERVER
Loads environment variables from AWS Parameter Store or creates them
"""

import boto3
import os
import json
from typing import Dict, Any

def setup_environment_from_parameter_store():
    """Load environment variables from AWS Parameter Store"""
    try:
        ssm = boto3.client('ssm', region_name='us-east-1')
        
        # List of parameters to load
        parameters = [
            'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY', 
            'AWS_REGION',
            'BEDROCK_MODEL_ID',
            'LANGCHAIN_API_KEY',
            'LANGCHAIN_PROJECT',
            'LANGCHAIN_TRACING_V2',
            'DYNAMODB_TABLE_NAME',
            'HOST',
            'PORT',
            'DEBUG',
            'GOOGLE_CLIENT_ID',
            'GOOGLE_CLIENT_SECRET',
            'GOOGLE_REDIRECT_URI',
            'GEMINI_API_KEY'
        ]
        
        # Load parameters from Parameter Store
        for param_name in parameters:
            try:
                response = ssm.get_parameter(
                    Name=f'/remo-server/{param_name}',
                    WithDecryption=True
                )
                os.environ[param_name] = response['Parameter']['Value']
                print(f"✅ Loaded {param_name} from Parameter Store")
            except ssm.exceptions.ParameterNotFound:
                print(f"⚠️  Parameter {param_name} not found in Parameter Store")
            except Exception as e:
                print(f"❌ Error loading {param_name}: {e}")
                
    except Exception as e:
        print(f"❌ Error connecting to Parameter Store: {e}")
        print("📝 Falling back to local .env file")

def create_parameter_store_entries():
    """Create environment variables in AWS Parameter Store"""
    try:
        ssm = boto3.client('ssm', region_name='us-east-1')
        
        # Environment variables to store
        env_vars = {
            'AWS_ACCESS_KEY_ID': 'your-aws-access-key-id',
            'AWS_SECRET_ACCESS_KEY': 'your-aws-secret-access-key',
            'AWS_REGION': 'us-east-1',
            'BEDROCK_MODEL_ID': 'amazon.nova-lite-v1:0',
            'LANGCHAIN_API_KEY': 'your-langchain-api-key-here',
            'LANGCHAIN_PROJECT': 'your-langchain-project-name',
            'LANGCHAIN_TRACING_V2': 'false',
            'DYNAMODB_TABLE_NAME': 'remo-user-data',
            'HOST': '0.0.0.0',
            'PORT': '8000',
            'DEBUG': 'true',
            'GOOGLE_CLIENT_ID': 'your-google-client-id',
            'GOOGLE_CLIENT_SECRET': 'your-google-client-secret',
            'GOOGLE_REDIRECT_URI': 'http://your-ec2-ip:8000/auth/google/callback',
            'GEMINI_API_KEY': 'your-gemini-api-key'
        }
        
        for param_name, param_value in env_vars.items():
            try:
                ssm.put_parameter(
                    Name=f'/remo-server/{param_name}',
                    Value=param_value,
                    Type='SecureString' if 'SECRET' in param_name or 'KEY' in param_name else 'String',
                    Overwrite=True
                )
                print(f"✅ Created parameter: /remo-server/{param_name}")
            except Exception as e:
                print(f"❌ Error creating {param_name}: {e}")
                
    except Exception as e:
        print(f"❌ Error creating Parameter Store entries: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "create":
        print("🔧 Creating Parameter Store entries...")
        create_parameter_store_entries()
    else:
        print("📥 Loading environment from Parameter Store...")
        setup_environment_from_parameter_store() 