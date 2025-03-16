"""
Custom RAG Agent
"""

from langchain_core.messages import SystemMessage, HumanMessage
from langchain.prompts import PromptTemplate
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# integration with APM
from py_zipkin.zipkin import zipkin_span

from agent_state import State
from oci_models import get_llm
from prompts import (
    ANSWER_PROMPT_TEMPLATE,
)
from query_rewriter import QueryRewriter
from vector_search import SemanticSearch
from reranker import Reranker
from utils import get_console_logger
from config import AGENT_NAME

logger = get_console_logger()


#
# Helper functions
#
def build_context_for_llm(docs: list):
    """
    Build the context for the final answer from LLM

    docs: list[Documents]
    """
    _context = ""

    for doc in docs:
        _context += doc.page_content + "\n\n"

    return _context


#
# Node functions
#
@zipkin_span(service_name=AGENT_NAME, span_name="generate_answer")
def generate_answer(state: State):
    """
    Generate the final answer
    """
    final_answer = ""
    error = None

    try:
        llm = get_llm()

        _context = build_context_for_llm(state["reranker_docs"])

        _prompt_template = PromptTemplate(
            input_variables=["context"],
            template=ANSWER_PROMPT_TEMPLATE,
        )

        system_prompt = _prompt_template.format(context=_context)

        messages = [
            SystemMessage(content=system_prompt),
        ]
        # add the chat history
        for msg in state["chat_history"]:
            messages.append(msg)

        messages.append(HumanMessage(content=state["user_request"]))

        # here we invoke the LLM
        final_answer = llm.invoke(messages).content

    except Exception as e:
        logger.error("Error in generate_answer: %s", e)
        error = str(e)

    return {"final_answer": final_answer, "error": error}


def create_workflow():
    """
    Create the entire workflow
    """
    workflow = StateGraph(State)

    # create nodes
    query_rewriter = QueryRewriter()
    semantic_search = SemanticSearch()
    reranker = Reranker()

    # Add nodes
    workflow.add_node("QueryRewrite", query_rewriter)
    workflow.add_node("Search", semantic_search)
    workflow.add_node("Rerank", reranker)
    workflow.add_node("Answer", generate_answer)

    # define edges
    workflow.add_edge(START, "QueryRewrite")
    workflow.add_edge("QueryRewrite", "Search")
    workflow.add_edge("Search", "Rerank")
    workflow.add_edge("Rerank", "Answer")
    workflow.add_edge("Answer", END)

    # create workflow executor
    memory = MemorySaver()
    workflow_app = workflow.compile(checkpointer=memory)

    return workflow_app
