# Email Assistant Evaluation Guide

This guide covers the comprehensive evaluation system for the Email Assistant agent, following the LangChain agents-from-scratch evaluation pattern.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Setup and Configuration](#setup-and-configuration)
4. [Evaluation Dataset](#evaluation-dataset)
5. [Evaluation Framework](#evaluation-framework)
6. [Running Evaluations](#running-evaluations)
7. [Results Analysis](#results-analysis)
8. [Customization](#customization)
9. [Integration with LangSmith](#integration-with-langsmith)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

## Overview

The Email Assistant Evaluation System provides comprehensive testing and evaluation capabilities for the email assistant agent. It follows the LangChain agents-from-scratch evaluation pattern and includes:

- **Comprehensive Test Dataset**: 30+ test cases covering various email scenarios
- **LLM-as-a-Judge Evaluation**: Automated quality assessment using GPT-4
- **Multi-dimensional Metrics**: Intent detection, action accuracy, response quality
- **Detailed Reporting**: Category and difficulty breakdowns with visualizations
- **LangSmith Integration**: Tracing and monitoring capabilities

## Architecture

```
evaluation_data/
├── __init__.py              # Module exports
├── email_dataset.py         # Test case definitions and dataset management
└── email_evaluator.py       # Evaluation framework and LLM-as-a-judge

evaluation_results/          # Generated evaluation results (JSON)
test_email_evaluation.py     # Test script for the evaluation system
```

### Key Components

1. **EmailTestCase**: Individual test case with expected outcomes
2. **EmailEvaluationDataset**: Dataset management and filtering
3. **EmailEvaluator**: Main evaluation engine with LLM-as-a-judge
4. **EvaluationResult**: Single test case evaluation result
5. **EvaluationSummary**: Aggregated results and statistics

## Setup and Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Required for evaluation
OPENAI_API_KEY=your_openai_api_key

# Optional for enhanced evaluation
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=remo-email-assistant

# AWS Configuration (for DynamoDB)
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=us-east-1

# Evaluation Configuration
EVALUATION_MODE=true
EVALUATION_DATASET_PATH=./evaluation_data/
EVALUATION_RESULTS_PATH=./evaluation_results/
```

### Installation

```bash
# Install evaluation dependencies
pip install -r requirements.txt

# Create evaluation directories
mkdir -p evaluation_results
```

## Evaluation Dataset

### Test Case Structure

Each test case includes:

```python
@dataclass
class EmailTestCase:
    id: str                           # Unique identifier
    user_message: str                 # User input
    expected_intent: str              # Expected detected intent
    expected_action: str              # Expected action
    expected_response_contains: List[str]  # Required response elements
    expected_response_not_contains: List[str] = None  # Forbidden elements
    context: Dict[str, Any] = None    # Additional context
    difficulty: str = "medium"        # easy, medium, hard
    category: str = "general"         # composition, search, management, etc.
```

### Dataset Categories

1. **Composition**: Email writing and drafting
2. **Search**: Email search and filtering
3. **Management**: Email organization and actions
4. **Summary**: Email statistics and summaries
5. **Scheduling**: Email scheduling and timing
6. **Edge Cases**: Error handling and edge scenarios
7. **Context**: Context-aware interactions
8. **Negative**: Non-email intents (for validation)

### Dataset Statistics

```python
from evaluation_data.email_dataset import get_email_dataset

dataset = get_email_dataset()
stats = dataset.get_statistics()

print(f"Total Test Cases: {stats['total_test_cases']}")
print(f"Categories: {stats['categories']}")
print(f"Difficulties: {stats['difficulties']}")
```

## Evaluation Framework

### Core Evaluation Metrics

1. **Intent Detection Accuracy**: Correct intent identification
2. **Action Detection Accuracy**: Correct action identification
3. **Response Quality Score**: LLM-as-a-judge assessment (0.0-1.0)
4. **Content Compliance**: Expected/unexpected content presence
5. **Overall Score**: Weighted combination of all metrics

### LLM-as-a-Judge Implementation

The evaluator uses GPT-4 to assess response quality:

```python
def _evaluate_response_quality(self, test_case, response, intent_correct, action_correct):
    prompt = f"""
    You are evaluating an email assistant's response to a user query.
    
    User Query: "{test_case.user_message}"
    Expected Intent: {test_case.expected_intent}
    Expected Action: {test_case.expected_action}
    Agent Response: "{response}"
    
    Rate the response quality on a scale of 0.0 to 1.0...
    """
    
    result = self.evaluation_llm.invoke(prompt)
    return float(result.content.strip())
```

### Scoring Weights

```python
intent_weight = 0.3      # Intent detection importance
action_weight = 0.3      # Action detection importance
quality_weight = 0.2     # Response quality importance
content_weight = 0.2     # Content compliance importance
```

## Running Evaluations

### Basic Evaluation

```python
from evaluation_data.email_evaluator import run_email_evaluation

# Run complete evaluation
results, summary = run_email_evaluation(user_id="test_user", save_results=True)
```

### Category-Specific Evaluation

```python
from evaluation_data.email_evaluator import run_category_evaluation

# Evaluate only composition tests
results, summary = run_category_evaluation("composition", "test_user")
```

### Custom Evaluation

```python
from evaluation_data.email_evaluator import EmailEvaluator

# Initialize evaluator
evaluator = EmailEvaluator(user_id="test_user")

# Get specific test cases
test_cases = evaluator.dataset.get_test_cases_by_difficulty("easy")

# Run evaluation
results = []
for test_case in test_cases:
    result = evaluator.evaluate_single_test_case(test_case)
    results.append(result)

# Generate summary
summary = evaluator.generate_evaluation_summary(results)
evaluator.print_evaluation_summary(summary)
```

### Running the Test Script

```bash
# Run comprehensive evaluation tests
python test_email_evaluation.py
```

## Results Analysis

### Evaluation Summary Structure

```python
@dataclass
class EvaluationSummary:
    total_tests: int                    # Total number of tests
    passed_tests: int                   # Tests with score >= 0.7
    failed_tests: int                   # Tests with score < 0.7
    intent_accuracy: float              # Intent detection accuracy
    action_accuracy: float              # Action detection accuracy
    response_quality_avg: float         # Average response quality
    overall_accuracy: float             # Overall accuracy
    category_breakdown: Dict            # Per-category statistics
    difficulty_breakdown: Dict          # Per-difficulty statistics
    error_count: int                    # Number of errors
    evaluation_duration: float          # Total evaluation time
```

### Sample Output

```
📊 EMAIL ASSISTANT EVALUATION SUMMARY
============================================================
📈 Overall Results:
   Total Tests: 30
   Passed Tests: 25
   Failed Tests: 5
   Overall Accuracy: 83.33%
   Evaluation Duration: 45.23s

🎯 Accuracy Metrics:
   Intent Detection: 90.00%
   Action Detection: 86.67%
   Response Quality: 78.50%

📂 Category Breakdown:
   Composition: 3/3 (100.00%) - Avg Score: 0.850
   Search: 4/5 (80.00%) - Avg Score: 0.720
   Management: 5/6 (83.33%) - Avg Score: 0.780
```

### Result Persistence

Results are automatically saved as JSON files:

```python
# Save results
filepath = evaluator.save_evaluation_results(results, summary)

# Load results
with open(filepath, 'r') as f:
    data = json.load(f)
    summary_data = data['summary']
    results_data = data['results']
```

## Customization

### Adding New Test Cases

```python
# In email_dataset.py
def _create_test_cases(self):
    return [
        # ... existing test cases ...
        EmailTestCase(
            id="custom_001",
            user_message="your custom test message",
            expected_intent="email",
            expected_action="custom_action",
            expected_response_contains=["expected", "terms"],
            difficulty="medium",
            category="custom"
        ),
    ]
```

### Custom Evaluation Metrics

```python
class CustomEmailEvaluator(EmailEvaluator):
    def _calculate_overall_score(self, intent_correct, action_correct,
                               response_quality, contains_expected,
                               not_contains_unexpected):
        # Custom scoring logic
        custom_score = (
            intent_correct * 0.4 +
            action_correct * 0.3 +
            response_quality * 0.2 +
            (contains_expected and not_contains_unexpected) * 0.1
        )
        return custom_score
```

### Custom Response Quality Evaluation

```python
def _evaluate_response_quality(self, test_case, response, intent_correct, action_correct):
    # Custom evaluation prompt
    custom_prompt = f"""
    Your custom evaluation criteria...
    """
    
    result = self.evaluation_llm.invoke(custom_prompt)
    return self._parse_custom_score(result.content)
```

## Integration with LangSmith

### Enabling LangSmith Tracing

```python
# Set environment variables
os.environ["LANGSMITH_API_KEY"] = "your_key"
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_PROJECT"] = "remo-email-assistant"

# Initialize evaluator with LangSmith
evaluator = EmailEvaluator(user_id="test_user", use_langsmith=True)
```

### LangSmith Features

1. **Trace Collection**: All evaluation runs are traced
2. **Performance Monitoring**: Track evaluation metrics over time
3. **Debugging**: Detailed logs for failed evaluations
4. **Comparison**: Compare different agent versions

## Best Practices

### 1. Test Case Design

- **Diverse Scenarios**: Cover various email use cases
- **Edge Cases**: Include error conditions and boundary cases
- **Realistic Inputs**: Use natural language variations
- **Clear Expectations**: Define precise expected outcomes

### 2. Evaluation Strategy

- **Start Small**: Begin with easy test cases
- **Iterative Improvement**: Use results to refine the agent
- **Regular Evaluation**: Run evaluations after each change
- **Baseline Comparison**: Track performance over time

### 3. Result Interpretation

- **Focus on Patterns**: Look for systematic issues
- **Category Analysis**: Identify weak areas
- **Difficulty Progression**: Ensure performance across difficulty levels
- **Error Analysis**: Investigate failed test cases

### 4. Performance Optimization

- **Batch Processing**: Evaluate multiple test cases efficiently
- **Caching**: Cache LLM responses for consistency
- **Parallel Processing**: Use multiple evaluators for large datasets
- **Resource Management**: Monitor API usage and costs

## Troubleshooting

### Common Issues

1. **Missing API Keys**
   ```
   Error: OpenAI API key not found
   Solution: Set OPENAI_API_KEY environment variable
   ```

2. **Import Errors**
   ```
   Error: Module not found
   Solution: Ensure evaluation_data directory is in Python path
   ```

3. **LLM Rate Limiting**
   ```
   Error: Rate limit exceeded
   Solution: Add delays between evaluations or use batch processing
   ```

4. **Memory Issues**
   ```
   Error: Out of memory
   Solution: Process test cases in smaller batches
   ```

### Debug Mode

Enable debug mode for detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

evaluator = EmailEvaluator(user_id="test_user")
```

### Performance Monitoring

```python
# Monitor evaluation performance
import time

start_time = time.time()
results, summary = run_email_evaluation("test_user")
duration = time.time() - start_time

print(f"Evaluation completed in {duration:.2f} seconds")
print(f"Average time per test: {duration/len(results):.2f} seconds")
```

## Next Steps

After implementing the evaluation system:

1. **Run Baseline Evaluation**: Establish performance baseline
2. **Identify Improvement Areas**: Focus on low-performing categories
3. **Iterate on Agent**: Improve based on evaluation results
4. **Expand Dataset**: Add more test cases for comprehensive coverage
5. **Automate Evaluation**: Integrate into CI/CD pipeline
6. **Monitor Performance**: Track improvements over time

## Conclusion

The Email Assistant Evaluation System provides a robust foundation for testing and improving the email assistant agent. By following the LangChain agents-from-scratch evaluation pattern, it ensures comprehensive coverage and reliable assessment of agent performance.

For more information, refer to:
- [LangChain Agents from Scratch Guide](https://github.com/langchain-ai/langchain/tree/master/libs/langgraph/langgraph/examples/agents-from-scratch)
- [Email Assistant Implementation Guide](./email_assistant_guide.md)
- [Remo AI Assistant Documentation](../README.md) 