# 📧 Email Assistant Agent Guide

## 🎯 Learning Outcomes

- Understand the architecture and purpose of the Email Assistant agent
- Learn how to use, extend, and test the email agent and its tools
- Integrate the email agent with orchestration, memory, and user data isolation
- Follow best practices for email agent design, security, and troubleshooting
- Know where to find deeper technical details and related guides

---

## 1. Overview

The Email Assistant Agent is a specialized agent in Remo-Server for comprehensive email management: composing, sending, searching, triaging, and organizing emails. It follows the modular, multi-agent architecture and integrates with user-specific data storage and orchestration.

For a high-level system view, see the [Architecture Overview](./architecture_overview.md).

---

## 2. Email Agent Architecture

- **Location:** `src/agents/email/`
- **Key Files:**
  - `email_agent.py`: Main agent class and orchestration
  - `email_tools.py`: Core email management tools
  - `email_triage.py`: Email classification and prioritization

---

## 3. Step-by-Step: Using & Extending the Email Agent

### 3.1 Understand the Tools

- `compose_email()`, `send_email()`, `schedule_email()`, `search_emails()`, `mark_email_read()`, `archive_email()`, `forward_email()`, `reply_to_email()`, `get_email_summary()`
- See [email_tools.py](../src/agents/email/email_tools.py) for full API and examples.

### 3.2 Explore the Agent Class

- `EmailAgent` in `email_agent.py` orchestrates email operations, intent detection, and conversation management.
- Key methods: `process()`, `_analyze_intent()`, `_handle_compose_email()`, `_handle_send_email()`, `_handle_search_emails()`, etc.
- See [email_agent.py](../src/agents/email/email_agent.py) for details.

### 3.3 Use Email Triage

- `EmailTriage` in `email_triage.py` classifies and prioritizes emails.
- Features: priority analysis, category detection, urgency scoring, action suggestions.
- See [email_triage.py](../src/agents/email/email_triage.py) for usage.

### 3.4 Integrate with DynamoDB

- All email data is user-specific and stored in DynamoDB (`remo-emails` table).
- See [DynamoDB Integration Guide](./dynamodb_integration_guide.md) and [User-Specific Implementation Summary](./user_specific_implementation_summary.md).

### 3.5 Integrate with Memory & Orchestration

- Email agent uses conversation memory and context for multi-turn tasks.
- Integrated with the supervisor orchestrator for intent detection and routing.
- See [Conversation Memory Guide](./conversation_memory_guide.md) and [Orchestration & Routing Guide](./orchestration_and_routing.md).

### 3.6 API Integration

- Email agent is accessible via the `/chat` endpoint and intent detection.
- See [API Integration Guide](./api_integration_guide.md) for request/response patterns.

### 3.7 Testing & Usage

- Test script: `python test_email_functionality.py`
- Try API calls:
  ```bash
  curl -X POST "http://localhost:8000/chat" \
    -H "Content-Type: application/json" \
    -d '{"message": "compose an email to john@example.com", "user_id": "user_123"}'
  ```
- See [email_agent.py](../src/agents/email/email_agent.py) for more usage examples.

---

## 4. Best Practices

- **User Data Isolation:** Always require `user_id` for all email operations
- **Security:** Store credentials securely, use minimal Gmail scopes, and follow privacy best practices
- **Error Handling:** Handle missing credentials, API errors, and edge cases gracefully
- **Testing:** Use the provided test scripts and add your own cases for new features
- **Documentation:** Document new tools, agent methods, and integration points

---

## 5. Troubleshooting

- **DynamoDB issues:** Check AWS credentials and table setup ([DynamoDB Guide](./dynamodb_integration_guide.md))
- **Intent detection:** Test with various email-related phrases and check routing
- **OAuth issues:** See [Google OAuth Guide](./google_oauth_guide.md) for authentication troubleshooting
- **API errors:** Check `/chat` endpoint logs and error messages
- **Testing:** Use `test_email_functionality.py` for comprehensive validation

---

## 6. Next Steps & Related Guides

- [Creating New Agents](./creating_new_agents.md)
- [Email Evaluation Guide](./email_evaluation_guide.md)
- [DynamoDB Integration Guide](./dynamodb_integration_guide.md)
- [User-Specific Implementation Summary](./user_specific_implementation_summary.md)
- [Conversation Memory Guide](./conversation_memory_guide.md)
- [Orchestration & Routing Guide](./orchestration_and_routing.md)
- [API Integration Guide](./api_integration_guide.md)
- [Google OAuth Guide](./google_oauth_guide.md)

---

**For more details, see the code in `src/agents/email/`, the test scripts, and the related guides above.**
