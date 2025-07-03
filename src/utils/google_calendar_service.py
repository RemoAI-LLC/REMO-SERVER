"""
Google Calendar Service
Handles Google Calendar integration including OAuth flow and calendar operations.
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle
import sys

# Global storage for user credentials (moved from app.py)
user_credentials = {}

class GoogleCalendarService:
    """
    Service for Google Calendar integration.
    Handles OAuth flow and calendar operations.
    """
    
    def __init__(self):
        """Initialize the Google Calendar service."""
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        self.redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')
        print("[DEBUG] GOOGLE_CLIENT_ID:", self.client_id)
        print("[DEBUG] GOOGLE_CLIENT_SECRET:", self.client_secret)
        print("[DEBUG] GOOGLE_REDIRECT_URI:", self.redirect_uri)
        
        # Scopes for Calendar and Gmail API
        self.scopes = [
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/calendar.events',
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
            'openid'
        ]
        
        # Token file path for storing credentials
        self.token_file = 'google_calendar_token.json'
    
    def get_authorization_url(self, user_id: str) -> str:
        """
        Get the authorization URL for Google OAuth.
        
        Args:
            user_id: User ID for state parameter
            
        Returns:
            Authorization URL
        """
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            raise ValueError("Google OAuth credentials not configured")
        
        # Create OAuth flow
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.scopes
        )
        
        flow.redirect_uri = self.redirect_uri
        
        # Generate authorization URL
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=user_id
        )
        
        return authorization_url
    
    def exchange_code_for_tokens(self, authorization_code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens.
        
        Args:
            authorization_code: Authorization code from Google
            
        Returns:
            Dictionary with tokens and user info
        """
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            raise ValueError("Google OAuth credentials not configured")
        
        # Create OAuth flow
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.scopes
        )
        
        flow.redirect_uri = self.redirect_uri
        
        # Exchange code for tokens
        flow.fetch_token(code=authorization_code)
        
        # Get credentials
        credentials = flow.credentials
        
        # Get user info
        user_info = self._get_user_info(credentials)
        
        return {
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
            'user_info': user_info
        }
    
    def _get_user_info(self, credentials: Credentials) -> Dict[str, Any]:
        """Get user information from Google."""
        try:
            service = build('oauth2', 'v2', credentials=credentials)
            user_info = service.userinfo().get().execute()
            return user_info
        except Exception as e:
            print(f"Error getting user info: {e}")
            return {}
    
    def create_calendar_event(self, credentials_data: Dict[str, Any], event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a calendar event using Google Calendar API.
        
        Args:
            credentials_data: User's Google credentials
            event_data: Event details
            
        Returns:
            Created event data
        """
        try:
            # Create credentials object
            credentials = Credentials(
                token=credentials_data['access_token'],
                refresh_token=credentials_data['refresh_token'],
                token_uri=credentials_data['token_uri'],
                client_id=credentials_data['client_id'],
                client_secret=credentials_data['client_secret'],
                scopes=credentials_data['scopes']
            )
            
            # Refresh token if needed
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            
            # Build Calendar service
            service = build('calendar', 'v3', credentials=credentials)
            
            # Prepare event data
            event = {
                'summary': event_data['subject'],
                'location': event_data.get('location', ''),
                'description': event_data.get('description', ''),
                'start': {
                    'dateTime': event_data['start_time'],
                    'timeZone': event_data.get('timezone', 'UTC'),
                },
                'end': {
                    'dateTime': event_data['end_time'],
                    'timeZone': event_data.get('timezone', 'UTC'),
                },
                'attendees': [{'email': email} for email in event_data['attendees']],
                'reminders': {
                    'useDefault': True,
                },
            }
            
            # Create the event
            event = service.events().insert(
                calendarId='primary',
                body=event,
                sendUpdates='all'  # Send invites to all attendees
            ).execute()
            
            return {
                'success': True,
                'event_id': event['id'],
                'event_link': event['htmlLink'],
                'event_data': event
            }
            
        except HttpError as error:
            print(f"Error creating calendar event: {error}")
            return {
                'success': False,
                'error': str(error),
                'error_details': error.error_details if hasattr(error, 'error_details') else None
            }
        except Exception as e:
            print(f"Unexpected error creating calendar event: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_calendars(self, credentials_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        List user's calendars.
        
        Args:
            credentials_data: User's Google credentials
            
        Returns:
            List of calendars
        """
        try:
            # Create credentials object
            credentials = Credentials(
                token=credentials_data['access_token'],
                refresh_token=credentials_data['refresh_token'],
                token_uri=credentials_data['token_uri'],
                client_id=credentials_data['client_id'],
                client_secret=credentials_data['client_secret'],
                scopes=credentials_data['scopes']
            )
            
            # Refresh token if needed
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            
            # Build Calendar service
            service = build('calendar', 'v3', credentials=credentials)
            
            # List calendars
            calendar_list = service.calendarList().list().execute()
            return calendar_list.get('items', [])
            
        except Exception as e:
            print(f"Error listing calendars: {e}")
            return []
    
    def get_events(self, credentials_data: Dict[str, Any], calendar_id: str = 'primary', 
                   time_min: str = None, time_max: str = None, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Get calendar events.
        
        Args:
            credentials_data: User's Google credentials
            calendar_id: Calendar ID (default: 'primary')
            time_min: Start time (ISO format)
            time_max: End time (ISO format)
            max_results: Maximum number of events
            
        Returns:
            List of events
        """
        try:
            # Create credentials object
            credentials = Credentials(
                token=credentials_data['access_token'],
                refresh_token=credentials_data['refresh_token'],
                token_uri=credentials_data['token_uri'],
                client_id=credentials_data['client_id'],
                client_secret=credentials_data['client_secret'],
                scopes=credentials_data['scopes']
            )
            
            # Refresh token if needed
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            
            # Build Calendar service
            service = build('calendar', 'v3', credentials=credentials)
            
            # Set default time range if not provided
            if not time_min:
                time_min = datetime.utcnow().isoformat() + 'Z'
            if not time_max:
                time_max = (datetime.utcnow() + timedelta(days=7)).isoformat() + 'Z'
            
            # Get events
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            return events_result.get('items', [])
            
        except Exception as e:
            print(f"Error getting events: {e}")
            return []

    def send_email(self, credentials_data: Dict[str, Any], to: str, subject: str, body: str, 
                   cc: List[str] = None, bcc: List[str] = None) -> Dict[str, Any]:
        """
        Send email using Gmail API.
        
        Args:
            credentials_data: User's Google credentials
            to: Recipient email address
            subject: Email subject
            body: Email body
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)
            
        Returns:
            Dictionary with send result
        """
        try:
            import base64
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Create credentials object
            credentials = Credentials(
                token=credentials_data['access_token'],
                refresh_token=credentials_data['refresh_token'],
                token_uri=credentials_data['token_uri'],
                client_id=credentials_data['client_id'],
                client_secret=credentials_data['client_secret'],
                scopes=credentials_data['scopes']
            )
            
            # Refresh token if needed
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            
            # Build Gmail service
            service = build('gmail', 'v1', credentials=credentials)
            
            # Create message
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            
            if cc:
                message['cc'] = ', '.join(cc)
            if bcc:
                message['bcc'] = ', '.join(bcc)
            
            # Add body
            text_part = MIMEText(body, 'plain')
            message.attach(text_part)
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send email
            sent_message = service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return {
                'success': True,
                'message_id': sent_message['id'],
                'thread_id': sent_message['threadId']
            }
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_emails(self, credentials_data: Dict[str, Any], query: str = None, 
                   max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Get emails from Gmail.
        
        Args:
            credentials_data: User's Google credentials
            query: Gmail search query (optional)
            max_results: Maximum number of emails
            
        Returns:
            List of emails
        """
        try:
            # Create credentials object
            credentials = Credentials(
                token=credentials_data['access_token'],
                refresh_token=credentials_data['refresh_token'],
                token_uri=credentials_data['token_uri'],
                client_id=credentials_data['client_id'],
                client_secret=credentials_data['client_secret'],
                scopes=credentials_data['scopes']
            )
            
            # Refresh token if needed
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            
            # Build Gmail service
            service = build('gmail', 'v1', credentials=credentials)
            
            # List messages
            if query:
                messages_result = service.users().messages().list(
                    userId='me',
                    q=query,
                    maxResults=max_results
                ).execute()
            else:
                messages_result = service.users().messages().list(
                    userId='me',
                    maxResults=max_results
                ).execute()
            
            messages = messages_result.get('messages', [])
            
            # Get full message details
            emails = []
            for message in messages:
                msg = service.users().messages().get(
                    userId='me',
                    id=message['id']
                ).execute()
                
                # Extract headers
                headers = msg['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                
                emails.append({
                    'id': msg['id'],
                    'thread_id': msg['threadId'],
                    'subject': subject,
                    'sender': sender,
                    'date': date,
                    'snippet': msg.get('snippet', '')
                })
            
            return emails
            
        except Exception as e:
            print(f"Error getting emails: {e}")
            return []

def create_google_calendar_event(user_id, subject, start_time, end_time, attendees, location, description):
    """Create a Google Calendar event for the specified user."""
    try:
        if user_id not in user_credentials:
            raise Exception("User not authenticated with Google. Please complete OAuth flow first to connect your Gmail account.")
        
        credentials = user_credentials[user_id]
        
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        
        creds = Credentials(
            token=credentials['token'],
            refresh_token=credentials['refresh_token'],
            token_uri=credentials['token_uri'],
            client_id=credentials['client_id'],
            client_secret=credentials['client_secret'],
            scopes=credentials['scopes']
        )
        
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        
        service = build('calendar', 'v3', credentials=creds)
        
        event = {
            'summary': subject,
            'location': location,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'UTC',
            },
            'attendees': [{'email': email} for email in attendees],
            'reminders': {
                'useDefault': True,
            },
        }
        
        event = service.events().insert(
            calendarId='primary',
            body=event,
            sendUpdates='all'
        ).execute()
        
        return {
            "user_id": user_id,
            "success": True,
            "event_id": event['id'],
            "event_link": event['htmlLink'],
            "message": "Calendar event created successfully"
        }
    except Exception as e:
        return {
            "user_id": user_id,
            "success": False,
            "error": str(e)
        }

def set_user_credentials(user_id, credentials):
    """Set user credentials for Google Calendar access."""
    user_credentials[user_id] = credentials

def get_user_credentials(user_id):
    """Get user credentials for Google Calendar access."""
    return user_credentials.get(user_id)

def remove_user_credentials(user_id):
    """Remove user credentials."""
    if user_id in user_credentials:
        del user_credentials[user_id] 