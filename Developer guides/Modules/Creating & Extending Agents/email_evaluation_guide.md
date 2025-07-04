# 📝 Email Assistant Evaluation Guide

## 🎯 Learning Outcomes

- Understand the purpose and structure of the email agent evaluation system
- Learn how to set up, run, and interpret comprehensive email agent tests
- Integrate evaluation with agent development and improvement workflows
- Follow best practices for test design, analysis, and troubleshooting
- Know where to find deeper technical details and related guides

---

## 1. Overview

The Email Assistant Evaluation System provides comprehensive, automated testing for the email agent, following the LangChain agents-from-scratch evaluation pattern. It covers intent detection, action accuracy, response quality, and more, with detailed reporting and integration with LangSmith.

For a high-level system view, see the [Architecture Overview](./architecture_overview.md) and [Email Assistant Guide](./email_assistant_guide.md).

---

## 2. Evaluation Architecture

- **Location:** `evaluation_data/`, `test_email_evaluation.py`
- **Key Components:**
  - `email_dataset.py`: Test case definitions and dataset management
  - `email_evaluator.py`: Evaluation framework and LLM-as-a-judge
  - `test_email_evaluation.py`: Test script for running evaluations

---

## 3. Step-by-Step: Running & Customizing Evaluation

### 3.1 Setup & Configuration

- Set required environment variables (see guide for details)
- Install dependencies: `pip install -r requirements.txt`
- Create evaluation directories: `mkdir -p evaluation_results`

### 3.2 Understand the Dataset

- Test cases cover composition, search, management, summary, scheduling, edge cases, and more
- See [email_dataset.py](../evaluation_data/email_dataset.py) for structure and customization

### 3.3 Run the Evaluation Framework

- Use `run_email_evaluation()` or `run_category_evaluation()` in `email_evaluator.py`
- Run the test script:
  ```bash
  python test_email_evaluation.py
  ```
- Results are saved as JSON in `evaluation_results/`

### 3.4 Analyze Results

- Review summary statistics: intent accuracy, action accuracy, response quality, category breakdowns
- See sample output in the guide for interpretation

### 3.5 Customize & Extend

- Add new test cases in `email_dataset.py`
- Adjust scoring weights or evaluation prompts in `email_evaluator.py`
- Integrate with LangSmith for tracing and monitoring

---

## 4. Best Practices

- **Diverse Scenarios:** Cover a wide range of email use cases and edge cases
- **Clear Expectations:** Define precise expected outcomes for each test
- **Iterative Improvement:** Use results to refine the agent and add new tests
- **Regular Evaluation:** Run tests after each major change
- **Documentation:** Document new test cases and evaluation logic

---

## 5. Troubleshooting

- **Missing API keys:** Ensure all required environment variables are set
- **Import errors:** Check Python paths and module structure
- **LLM rate limiting:** Add delays or use batch processing
- **Test failures:** Review failed cases for patterns and agent improvements
- **Debug mode:** Enable debug logging for detailed output

---

## 6. Next Steps & Related Guides

- [Email Assistant Guide](./email_assistant_guide.md)
- [Creating New Agents](./creating_new_agents.md)
- [Conversation Memory Guide](./conversation_memory_guide.md)
- [Orchestration & Routing Guide](./orchestration_and_routing.md)
- [API Integration Guide](./api_integration_guide.md)
- [User-Specific Implementation Summary](./user_specific_implementation_summary.md)

---

**For more details, see the code in `evaluation_data/`, the test scripts, and the related guides above.**
