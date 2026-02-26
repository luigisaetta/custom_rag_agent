"""
File name: tests/test_prompts.py
Author: Luigi Saetta
Last modified: 25-02-2026
Python Version: 3.11
License: MIT
Description: Unit tests for prompt templates placeholders used by reformulation, reranking, and answering steps.
"""

import agent.prompts as prompts


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
