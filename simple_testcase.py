"""
LOB issue simple test case
"""

import oracledb
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_community.embeddings import OCIGenAIEmbeddings
from langchain_community.vectorstores.oraclevs import OracleVS

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

#
# Main
#
logger.info("")
logger.info("Starting test...")

questions = ["What are the knwon side effects of metformin?,"]

#
# setup
#
embed_model = OCIGenAIEmbeddings(
    auth_type=AUTH,
    model_id=EMBED_MODEL_ID,
    service_endpoint=SERVICE_ENDPOINT,
    compartment_id=COMPARTMENT_ID,
)

with oracledb.connect(**CONNECT_ARGS) as conn:

    v_store = OracleVS(
        client=conn,
        table_name="BOOKS",
        distance_strategy=DistanceStrategy.COSINE,
        embedding_function=embed_model,
    )

    for question in questions:
        relevant_docs = v_store.similarity_search(query=question, k=TOP_K)
