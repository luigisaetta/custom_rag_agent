"""
Node for the Semantic Search

Encapsulate Oracle VS, based on 23AI
"""

import oracledb
from langchain_core.runnables import Runnable
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_community.embeddings import OCIGenAIEmbeddings
from langchain_community.vectorstores.oraclevs import OracleVS

# integration with APM
from py_zipkin.zipkin import zipkin_span

from agent_state import State
from utils import get_console_logger

from config import (
    AGENT_NAME,
    DEBUG,
    AUTH,
    EMBED_MODEL_ID,
    SERVICE_ENDPOINT,
    COMPARTMENT_ID,
    TOP_K,
)

from config_private import CONNECT_ARGS

logger = get_console_logger()


class SemanticSearch(Runnable):
    """
    This class is a base class for all nodes in the agent
    where you equip the node with APM tracing capabilities.
    It provides a common interface for running a node and a hook for adding
    custom logic
    """

    def __init__(self):
        """
        Init
        """

    def get_connection(self):
        """
        get a connection to the DB
        """
        return oracledb.connect(**CONNECT_ARGS)

    def get_embedding_model(self):
        """
        Create the Embedding Model
        """
        embed_model = OCIGenAIEmbeddings(
            auth_type=AUTH,
            model_id=EMBED_MODEL_ID,
            service_endpoint=SERVICE_ENDPOINT,
            compartment_id=COMPARTMENT_ID,
        )

        return embed_model

    @zipkin_span(service_name=AGENT_NAME, span_name="similarity_search")
    def invoke(self, input: State, config=None, **kwargs):
        """
        This method invokes the vector search

        input: the agent state
        """
        collection_name = config["configurable"]["collection_name"]

        relevant_docs = []
        error = None

        standalone_question = input["standalone_question"]

        if DEBUG:
            logger.info("Search question: %s", standalone_question)

        try:
            embed_model = self.get_embedding_model()

            # get a connection to the DB and init VS
            with self.get_connection() as conn:
                v_store = OracleVS(
                    client=conn,
                    table_name=collection_name,
                    distance_strategy=DistanceStrategy.COSINE,
                    embedding_function=embed_model,
                )

                relevant_docs = v_store.similarity_search(
                    query=standalone_question, k=TOP_K
                )

            if DEBUG:
                logger.info("Result from similarity search:")
                logger.info(relevant_docs)

        except Exception as e:
            logger.error("Error in vector_store.invoke: %s", e)
            error = str(e)

        return {"retriever_docs": relevant_docs, "error": error}
