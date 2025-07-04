# 🚀 Remo-Server Developer Course & Guide Index

Welcome to the Remo-Server developer course! This course is designed to take you from zero to expert in building, extending, and maintaining the Remo multi-agent AI backend. Each module is a step in your journey, with clear learning outcomes, code references, and hands-on examples.

---

## 📑 Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Building from Scratch](#2-building-from-scratch)
3. [API & FastAPI Integration](#3-api--fastapi-integration)
4. [Conversation Memory System](#4-conversation-memory-system)
5. [DynamoDB & User Data Isolation](#5-dynamodb--user-data-isolation)
6. [Agent Orchestration & Routing](#6-agent-orchestration--routing)
7. [Creating & Extending Agents](#7-creating--extending-agents)
8. [Testing, Debugging & Visualization](#8-testing-debugging--visualization)
9. [Deployment & Production](#9-deployment--production)
10. [Voice & Advanced Features](#10-voice--advanced-features)

---

## 🗺️ Course Structure & Learning Path

### 1. Architecture Overview

_Get a high-level understanding of Remo-Server's architecture, components, and how everything fits together._

- **Goal:** Understand what Remo is, its use cases, and the big-picture architecture.
- **Guide:** [Architecture Overview](./Modules/Architecture%20Overview/architecture_overview.md)

### 2. Building from Scratch

_Learn how to set up Remo-Server from a fresh environment, install dependencies, and run the system locally._

- **Goal:** Set up Remo from scratch, run the server, and visualize the system.
- **Guide:** [Building from Scratch](./Modules/Building%20from%20Scratch/building_from_scratch.md)

### 3. API & FastAPI Integration

_Explore the FastAPI backend, available API endpoints, and how to connect the backend with the frontend or other services._

- **Goal:** Learn how the FastAPI backend works, API endpoints, and how to integrate with the frontend or other services.
- **Guides:**
  - [API Integration Guide](./Modules/API%20&%20FastAPI%20Integration/api_integration_guide.md)
  - [FastAPI Integration Guide](./Modules/API%20&%20FastAPI%20Integration/fastapi_integration_guide.md)

### 4. Conversation Memory System

_Understand Remo's memory system for multi-turn, context-aware conversations, including buffer and summary memory types._

- **Goal:** Understand and extend the memory system (buffer, summary, context, persistence).
- **Guides:**
  - [Conversation Memory Guide](./Modules/Conversation%20Memory%20System/conversation_memory_guide.md)
  - [Conversation Memory API Guide](./Modules/Conversation%20Memory%20System/conversation_memory_api_guide.md)

### 5. DynamoDB & User Data Isolation

_Learn how Remo-Server uses DynamoDB for secure, user-specific data storage and isolation, and how to extend or debug this integration._

- **Goal:** Implement and maintain user-specific data storage and isolation using DynamoDB.
- **Guides:**
  - [DynamoDB Integration Guide](./Modules/DynamoDB%20&%20User%20Data%20Isolation/dynamodb_integration_guide.md)
  - [Enhanced DynamoDB Guide](./Modules/DynamoDB%20&%20User%20Data%20Isolation/enhanced_dynamodb_guide.md)
  - [User-Specific Implementation Summary](./Modules/DynamoDB%20&%20User%20Data%20Isolation/user_specific_implementation_summary.md)

### 6. Agent Orchestration & Routing

_Master the orchestration of multiple specialized agents, intent detection, context management, and routing logic._

- **Goal:** Master the multi-agent orchestration, intent detection, context management, and routing logic.
- **Guides:**
  - [Orchestration & Routing Guide](./Modules/Agent%20Orchestration%20&%20Routing/orchestration_and_routing.md)
  - [Intent Detection & Routing Improvements](./Modules/Agent%20Orchestration%20&%20Routing/intent_detection_and_routing_improvements.md)

### 7. Creating & Extending Agents

_Learn how to add new agents (like email, reminders, todos), extend existing ones, and integrate with authentication and Gmail._

- **Goal:** Add new specialized agents (e.g., email, reminders, todos) and extend existing ones.
- **Guides:**
  - [Creating New Agents](./Modules/Creating%20&%20Extending%20Agents/creating_new_agents.md)
  - [Email Assistant Guide](./Modules/Creating%20&%20Extending%20Agents/email_assistant_guide.md)
  - [Email Evaluation Guide](./Modules/Creating%20&%20Extending%20Agents/email_evaluation_guide.md)
  - [Google OAuth Guide](./Modules/Creating%20&%20Extending%20Agents/google_oauth_guide.md)

### 8. Testing, Debugging & Visualization

_Test, debug, and visualize the orchestration system and agent flows using provided scripts and visualization tools._

- **Goal:** Test, debug, and visualize the orchestration system and agent flows.
- **Guides:**
  - [Visualization & Debugging](./Modules/Testing,%20Debugging%20&%20Visualization/visualization_and_debugging.md)

### 9. Deployment & Production

_Deploy Remo-Server to production, manage environment variables, monitor health, and follow best practices for reliability._

- **Goal:** Deploy Remo-Server to production, manage environment variables, and monitor health.
- **Guides:**
  - [Deployment Guide](./Modules/Deployment%20&%20Production/deployment_guide.md)

### 10. Voice & Advanced Features

_Integrate and extend voice input, advanced memory, and explore future enhancements for Remo-Server._

- **Goal:** Integrate and extend voice input, advanced memory, and future enhancements.
- **Guides:**
  - [Voice Chat Guide](./Modules/Voice%20&%20Advanced%20Features/voice_chat_guide.md)

---

## 📚 Additional Resources

- [LangChain Agents from Scratch](https://github.com/langchain-ai/langchain/tree/master/libs/langgraph/langgraph/examples/agents-from-scratch)
- [Remo-Server Source Code](../src/)
- [Frontend Integration Guide](../../REMO-APP/)

---

**Complete this course to become a Remo-Server expert!**

If you find any guide out of date or unclear, please update it or contact the maintainers.
