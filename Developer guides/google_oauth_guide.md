# Google OAuth and Gmail Integration Guide

This guide covers the implementation of Google OAuth authentication for Gmail access in the Remo AI assistant.

## Overview

The Google OAuth integration allows users to securely authenticate with their Google accounts and access their Gmail inbox through the Remo assistant. This enables email reading, searching, and management capabilities.

## Architecture

### Components

1. **OAuth Flow Management**: Handles the OAuth 2.0 authorization flow
2. **Credential Storage**: Securely stores user credentials (in-memory for development)
3. **Gmail API Integration**: Provides email reading and searching capabilities
4. **Authentication Endpoints**: REST API endpoints for OAuth flow
5. **Email Management Endpoints**: API endpoints for email operations

### Security Considerations

- **Production**: Use encrypted database storage for credentials
- **Token Refresh**: Automatic token refresh handling
- **Scope Limitation**: Minimal required scopes for Gmail access
- **User Isolation**: User-specific credential storage

## Setup Instructions

### 1. Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing project
3. Enable the Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

### 2. OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Configure OAuth consent screen:
   - User Type: External (or Internal for Google Workspace)
   - App name: "Remo AI Assistant"
   - User support email: Your email
   - Developer contact information: Your email
   - Scopes: Add Gmail scopes manually

4. Create OAuth 2.0 Client ID:
   - Application type: Web application
   - Name: "Remo Gmail Integration"
   - Authorized redirect URIs: `http://localhost:8000/auth/google/callback`
   - For production: Add your production callback URL

### 3. Environment Variables

Add the following to your `.env` file:

```bash
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8000/auth/google/callback
```

### 4. Dependencies

The following packages are required (already in requirements.txt):

```bash
google-auth==2.29.0
google-auth-oauthlib==1.2.0
google-api-python-client==2.126.0
```

## API Endpoints

### Authentication Endpoints

#### 1. Initiate OAuth Login
```http
GET /auth/google/login
```

**Response:**
```json
{
  "authorization_url": "https://accounts.google.com/o/oauth2/auth?...",
  "state": "random_state_string",
  "message": "Redirect user to this URL to authorize Gmail access"
}
```

#### 2. OAuth Callback
```http
GET /auth/google/callback?code={authorization_code}&state={state}&user_id={user_id}
```

**Response:**
```json
{
  "success": true,
  "user_id": "user123",
  "message": "Gmail access authorized successfully",
  "scopes": ["https://www.googleapis.com/auth/gmail.readonly", ...]
}
```

#### 3. Check Authentication Status
```http
GET /auth/status/{user_id}
```

**Response:**
```json
{
  "user_id": "user123",
  "authenticated": true,
  "scopes": ["https://www.googleapis.com/auth/gmail.readonly", ...],
  "message": "User is authenticated with Gmail"
}
```

#### 4. Logout
```http
DELETE /auth/logout/{user_id}
```

**Response:**
```json
{
  "user_id": "user123",
  "success": true,
  "message": "User logged out successfully"
}
```

### Email Management Endpoints

#### 1. Read Emails
```http
GET /emails/read?user_id={user_id}&max_results={count}&query={gmail_query}
```

**Parameters:**
- `user_id`: User identifier
- `max_results`: Maximum number of emails to return (default: 10)
- `query`: Gmail search query (default: "in:inbox")

**Response:**
```json
{
  "user_id": "user123",
  "success": true,
  "emails": [
    {
      "id": "message_id",
      "subject": "Email Subject",
      "sender": "sender@example.com",
      "date": "Wed, 15 Jan 2024 10:30:00 +0000",
      "body": "Email body content...",
      "snippet": "Email snippet...",
      "labels": ["INBOX", "UNREAD"]
    }
  ],
  "total": 5,
  "query": "in:inbox"
}
```

#### 2. Search Emails
```http
GET /emails/search?user_id={user_id}&query={search_query}&max_results={count}
```

**Parameters:**
- `user_id`: User identifier
- `query`: Gmail search query (required)
- `max_results`: Maximum number of emails to return (default: 10)

## Gmail Query Examples

### Basic Queries
- `in:inbox` - All inbox emails
- `is:unread` - Unread emails
- `is:read` - Read emails
- `from:someone@example.com` - Emails from specific sender
- `to:me` - Emails sent to me
- `subject:meeting` - Emails with "meeting" in subject

### Advanced Queries
- `in:inbox is:unread` - Unread inbox emails
- `from:boss@company.com is:unread` - Unread emails from boss
- `subject:urgent` - Emails with "urgent" in subject
- `has:attachment` - Emails with attachments
- `larger:10M` - Emails larger than 10MB
- `newer_than:7d` - Emails from last 7 days

### Label Queries
- `label:work` - Emails with "work" label
- `label:important` - Emails with "important" label
- `-label:spam` - Exclude spam label

## Usage Examples

### 1. Complete OAuth Flow

```python
import requests

# Step 1: Initiate OAuth
response = requests.get("http://localhost:8000/auth/google/login")
auth_data = response.json()
auth_url = auth_data["authorization_url"]

# Step 2: User visits auth_url in browser and authorizes
# Step 3: Handle callback with authorization code
code = "authorization_code_from_callback"
state = auth_data["state"]
user_id = "user123"

callback_response = requests.get(
    "http://localhost:8000/auth/google/callback",
    params={"code": code, "state": state, "user_id": user_id}
)
```

### 2. Read Recent Emails

```python
# Read last 10 inbox emails
response = requests.get(
    "http://localhost:8000/emails/read",
    params={"user_id": "user123", "max_results": 10}
)

emails = response.json()["emails"]
for email in emails:
    print(f"Subject: {email['subject']}")
    print(f"From: {email['sender']}")
    print(f"Date: {email['date']}")
    print(f"Snippet: {email['snippet']}")
    print("---")
```

### 3. Search Unread Emails

```python
# Search for unread emails
response = requests.get(
    "http://localhost:8000/emails/search",
    params={
        "user_id": "user123",
        "query": "is:unread",
        "max_results": 5
    }
)

unread_emails = response.json()["emails"]
print(f"Found {len(unread_emails)} unread emails")
```

### 4. Check Authentication Status

```python
# Check if user is authenticated
response = requests.get("http://localhost:8000/auth/status/user123")
status = response.json()

if status["authenticated"]:
    print("User is authenticated with Gmail")
    print(f"Scopes: {status['scopes']}")
else:
    print("User needs to authenticate")
```

## Integration with Email Agent

The Gmail integration works seamlessly with the existing email agent:

```python
# Email agent can now access real Gmail data
email_agent = EmailAgent()

# Read emails for analysis
emails = email_agent.read_recent_emails(user_id="user123", count=5)

# Search for specific emails
urgent_emails = email_agent.search_emails(
    user_id="user123",
    query="subject:urgent is:unread"
)

# Process and respond to email queries
response = email_agent.process_email_request(
    user_message="Show me my unread emails",
    user_id="user123"
)
```

## Error Handling

### Common Errors

1. **401 Unauthorized**: User not authenticated
   ```json
   {
     "detail": "User not authenticated with Gmail. Please complete OAuth flow first."
   }
   ```

2. **400 Bad Request**: Invalid Gmail API request
   ```json
   {
     "detail": "Gmail API error: Invalid query"
   }
   ```

3. **500 Internal Server Error**: OAuth configuration issues
   ```json
   {
     "detail": "Error creating OAuth flow: Invalid client configuration"
   }
   ```

### Troubleshooting

1. **OAuth Flow Fails**:
   - Check Google Cloud Console credentials
   - Verify redirect URI matches exactly
   - Ensure Gmail API is enabled

2. **Email Reading Fails**:
   - Verify user has completed OAuth flow
   - Check Gmail API quotas
   - Ensure proper scopes are granted

3. **Token Expired**:
   - Implement automatic token refresh
   - Handle refresh token errors gracefully

## Security Best Practices

### Development
- Use environment variables for sensitive data
- Implement proper error handling
- Log authentication events

### Production
- Use encrypted database for credential storage
- Implement session management
- Add rate limiting
- Use HTTPS for all endpoints
- Implement proper token refresh logic
- Add audit logging

## Testing

Run the test script to verify the implementation:

```bash
python test_google_oauth.py
```

The test script will:
1. Test the complete OAuth flow
2. Verify email reading functionality
3. Test authentication management
4. Verify error handling

## Next Steps

1. **Outlook Integration**: Implement Microsoft Graph API for Outlook
2. **Email Composition**: Add email sending capabilities
3. **Advanced Search**: Implement more sophisticated email search
4. **Email Analytics**: Add email usage analytics
5. **Bulk Operations**: Support for bulk email operations
6. **Email Templates**: Pre-defined email templates
7. **Smart Filtering**: AI-powered email filtering and categorization

## Resources

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Google OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)
- [Gmail API Python Client](https://github.com/googleapis/google-api-python-client)
- [Gmail Search Operators](https://support.google.com/mail/answer/7190?hl=en) 