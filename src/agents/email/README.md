# Email Assistant Agent Package

This package contains all email-related functionality for the Remo AI assistant, providing comprehensive email management capabilities.

## 📁 Package Structure

```
src/agents/email/
├── __init__.py                 # Package initialization and exports
├── email_agent.py             # Main email management agent
├── email_tools.py             # Core email operations and tools
├── email_triage.py            # Email classification and prioritization
└── README.md                  # This documentation file
```

## 🚀 Core Components

### EmailAgent
The main email management agent that provides:
- Email composition and sending
- Email search and organization
- Email scheduling and follow-ups
- Meeting scheduling with Google Calendar
- Email triage and classification

### EmailTools
Core email operations including:
- `compose_email()` - Create email drafts
- `send_email()` - Send emails via Gmail API
- `schedule_email()` - Schedule emails for later
- `search_emails()` - Search and filter emails
- `schedule_meeting()` - Create Google Calendar events
- And more...

### EmailTriage
Email classification and prioritization system that:
- Analyzes email content and context
- Categorizes emails by importance
- Suggests appropriate actions
- Manages email workflow

## 🔧 Usage

### Basic Usage
```python
from src.agents.email import EmailAgent

# Create email agent
email_agent = EmailAgent(user_id="user123")

# Process email request
response = email_agent.process("Compose an email to john@example.com")
```

### Direct Tool Usage
```python
from src.agents.email import compose_email, send_email

# Compose email
result = compose_email(
    to_recipients=["john@example.com"],
    subject="Meeting Tomorrow",
    body="Hi John, let's meet tomorrow at 2pm.",
    user_id="user123"
)

# Send email
send_email(email_id=result["email_id"], user_id="user123")
```

### Meeting Scheduling
```python
from src.agents.email import schedule_meeting

# Schedule meeting
result = schedule_meeting(
    attendees=["john@example.com", "jane@example.com"],
    subject="Project Review",
    start_time="2025-01-15T14:00:00Z",
    end_time="2025-01-15T15:00:00Z",
    user_id="user123"
)
```

## 🔌 Integration

The email agent integrates with:
- **Gmail API** - For email operations
- **Google Calendar API** - For meeting scheduling
- **DynamoDB** - For data persistence
- **LangGraph** - For agent orchestration
- **Supervisor Orchestrator** - For multi-agent coordination

## 🔐 Authentication

The email agent requires Google OAuth authentication for:
- Gmail API access
- Google Calendar API access
- Email sending and management

Users must complete the OAuth flow through the Integrations page before using email features.

## 🚨 Error Handling

The email agent includes comprehensive error handling for:
- Authentication failures
- API rate limits
- Network connectivity issues
- Invalid email addresses
- Calendar conflicts

## 📈 Performance

The email agent is optimized for:
- Fast response times
- High accuracy in intent detection
- Efficient email processing
- Scalable user management

## 🔄 Updates and Maintenance

To update the email agent:
1. Modify the relevant component files
2. Test functionality manually
3. Update this documentation

## 📞 Support

For issues or questions about the email agent:
1. Check the usage examples above
2. Consult the main Remo documentation
3. Check the Google API documentation for integration details 