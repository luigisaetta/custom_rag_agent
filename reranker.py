"""
Reranker
"""

# Import traceback for better error logging
import traceback
from langchain_core.runnables import Runnable
from langchain_core.messages import HumanMessage
from langchain.prompts import PromptTemplate

# integration with APM
from py_zipkin.zipkin import zipkin_span

from agent_state import State
from prompts import (
    RERANKER_TEMPLATE,
)
from oci_models import get_llm
from utils import get_console_logger, extract_json_from_text
from config import DEBUG, ENABLE_RERANKER, AGENT_NAME

logger = get_console_logger()


class Reranker(Runnable):
    """
    Implements a reranker using a LLM
    """

    def __init__(self):
        """
        Init
        """
        super().__init__()

    def generate_refs(self, docs: list):
        """
        Returns a list of reference dictionaries used in the reranker.
        """
        return [
            {"source": doc.metadata["source"], "page_label": doc.metadata["page_label"]}
            for doc in docs
        ]

    @staticmethod
    def get_reranked_docs(llm, query, retriever_docs):
        """
        Rerank documents using LLM based on user request.

        query: the search query (can be reformulated)
        retriever_docs: list of Langchain Documents
        """
        # Prepare chunk texts
        chunks = [doc.page_content for doc in retriever_docs]

        _prompt = PromptTemplate(
            input_variables=["query", "chunks"],
            template=RERANKER_TEMPLATE,
        ).format(query=query, chunks=chunks)

        messages = [HumanMessage(content=_prompt)]
        reranker_output = llm.invoke(messages).content

        # Extract ranking order
        json_dict = extract_json_from_text(reranker_output)

        if DEBUG:
            logger.info(json_dict.get("ranked_chunks", "No ranked chunks found."))

        # Get indexes and sort documents
        indexes = [chunk["index"] for chunk in json_dict.get("ranked_chunks", [])]

        return [retriever_docs[i] for i in indexes]

    @zipkin_span(service_name=AGENT_NAME, span_name="reranking")
    def invoke(self, input: State, config=None, **kwargs):
        """
        Implements reranking logic.

        input: The agent state.
        """
        user_request = input.get("standalone_question", "")
        retriever_docs = input.get("retriever_docs", [])
        error = None

        if DEBUG:
            logger.info("Reranker input state: %s", input)

        try:
            llm = get_llm(temperature=0.0, max_tokens=4000)

            if retriever_docs:
                reranked_docs = (
                    self.get_reranked_docs(llm, user_request, retriever_docs)
                    if ENABLE_RERANKER
                    else retriever_docs
                )
            else:
                reranked_docs = []

        except Exception as e:
            logger.error("Error in reranker: %s", e)
            logger.debug(
                traceback.format_exc()
            )  # Log the full stack trace for debugging
            error = str(e)
            reranked_docs = retriever_docs  # Fallback to original documents

        # Get reference citations
        citations = self.generate_refs(reranked_docs)

        return {"reranker_docs": reranked_docs, "citations": citations, "error": error}
