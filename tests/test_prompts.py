"""
File name: tests/test_prompts.py
Author: Luigi Saetta
Last modified: 25-02-2026
Python Version: 3.11
License: MIT
Description: Unit tests for prompt templates placeholders used by reformulation, reranking, and answering steps.
"""

import agent.prompts as prompts
from langchain_core.prompts import PromptTemplate


def test_reformulate_prompt_has_required_placeholders():
    tpl = prompts.REFORMULATE_PROMPT_TEMPLATE
    assert "{user_request}" in tpl
    assert "{chat_history}" in tpl


def test_answer_prompt_has_context_placeholder():
    assert "{context}" in prompts.ANSWER_PROMPT_TEMPLATE


def test_reranker_prompt_has_required_placeholders():
    tpl = prompts.RERANKER_TEMPLATE
    assert "{query}" in tpl
    assert "{chunks}" in tpl


def test_intent_classifier_prompt_has_user_request_placeholder():
    assert "{user_request}" in prompts.INTENT_CLASSIFIER_TEMPLATE


def test_intent_classifier_prompt_formats_without_missing_keys():
    prompt = PromptTemplate(
        input_variables=["user_request"],
        template=prompts.INTENT_CLASSIFIER_TEMPLATE,
    ).format(user_request="test")
    assert '"intent"' in prompt
