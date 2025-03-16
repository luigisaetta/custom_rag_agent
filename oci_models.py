"""
OCI Models
"""

from langchain_community.chat_models import ChatOCIGenAI

from utils import get_console_logger
from config import (
    AUTH,
    SERVICE_ENDPOINT,
    LLM_MODEL_ID,
    COMPARTMENT_ID,
    TEMPERATURE,
    MAX_TOKENS,
)


logger = get_console_logger()


def get_llm(temperature=TEMPERATURE, max_tokens=MAX_TOKENS):
    """
    Initialize and return an instance of ChatOCIGenAI with the specified configuration.

    Returns:
        ChatOCIGenAI: An instance of the OCI GenAI language model.
    """
    llm = ChatOCIGenAI(
        auth_type=AUTH,
        model_id=LLM_MODEL_ID,
        service_endpoint=SERVICE_ENDPOINT,
        compartment_id=COMPARTMENT_ID,
        is_stream=True,
        model_kwargs={
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
    )
    return llm
