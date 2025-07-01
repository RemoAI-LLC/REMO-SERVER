"""
Email Assistant Evaluation Module

This module provides comprehensive evaluation capabilities for the email assistant agent,
following the LangChain agents-from-scratch evaluation pattern.
"""

from .email_dataset import (
    EmailTestCase,
    EmailEvaluationDataset,
    get_email_dataset,
    get_test_cases,
    get_composition_tests,
    get_search_tests,
    get_management_tests,
    get_easy_tests,
    get_medium_tests,
    get_hard_tests
)

from .email_evaluator import (
    EvaluationResult,
    EvaluationSummary,
    EmailEvaluator,
    run_email_evaluation,
    run_category_evaluation
)

__all__ = [
    # Dataset classes and functions
    "EmailTestCase",
    "EmailEvaluationDataset",
    "get_email_dataset",
    "get_test_cases",
    "get_composition_tests",
    "get_search_tests",
    "get_management_tests",
    "get_easy_tests",
    "get_medium_tests",
    "get_hard_tests",
    
    # Evaluator classes and functions
    "EvaluationResult",
    "EvaluationSummary",
    "EmailEvaluator",
    "run_email_evaluation",
    "run_category_evaluation"
] 