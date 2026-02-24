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
