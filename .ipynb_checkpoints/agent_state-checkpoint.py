"""
Agent State
"""

from typing_extensions import TypedDict, Optional


class State(TypedDict):
    """
    The state of the graph
    """

    # the original user request
    user_request: str
    chat_history: list = []

    # the question reformulated using chat_history
    standalone_question: str = ""

    # similarity_search
    retriever_docs: Optional[list] = []
    # reranker
    reranker_docs: Optional[list] = []
    # Answer
    final_answer: str
    # Citations
    citations: list = []

    # if any step encounter an error
    error: Optional[str] = None
