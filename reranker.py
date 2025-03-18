"""
Reranker
"""

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

    def generate_refs(self, docs: list):
        """
        Return the list of refs, used in the reranker
        """
        # generate references
        citation_links = []

        for doc in docs:
            citation_links.append(
                {
                    "source": doc.metadata["source"],
                    "page_label": doc.metadata["page_label"],
                }
            )

        return citation_links

    @zipkin_span(service_name=AGENT_NAME, span_name="reranking")
    def invoke(self, input: State, config=None, **kwargs):
        """
        This method invokes the reranker

        input: the agent state
        """
        user_request = input["standalone_question"]
        error = None

        if DEBUG:
            logger.info("Reranker input state:")
            logger.info(input)

        try:
            llm = get_llm(temperature=0.0, max_tokens=4000)

            retriever_docs = input["retriever_docs"]
            # create the chunks list
            if len(retriever_docs) > 0:
                if ENABLE_RERANKER:
                    # create the chunks texts list
                    chunks = []
                    for doc in retriever_docs:
                        chunks.append(doc.page_content)

                    _prompt = PromptTemplate(
                        input_variables=["user_request", "chunks"],
                        template=RERANKER_TEMPLATE,
                    ).format(user_request=user_request, chunks=chunks)

                    messages = [
                        HumanMessage(content=_prompt),
                    ]

                    reranker_output = llm.invoke(messages).content

                    json_dict = extract_json_from_text(reranker_output)

                    if DEBUG:
                        logger.info(json_dict["ranked_chunks"])

                    # get the indexes
                    indexes = [
                        chunk["index"] for chunk in json_dict.get("ranked_chunks", [])
                    ]

                    reranked_docs = [retriever_docs[i] for i in indexes]
                else:
                    reranked_docs = retriever_docs
            else:
                reranked_docs = []

        except Exception as e:
            logger.error("Error in reranker: %s", e)
            error = str(e)

            reranked_docs = retriever_docs

        # get the references
        citations = self.generate_refs(reranked_docs)

        return {"reranker_docs": reranked_docs, "citations": citations, "error": error}
