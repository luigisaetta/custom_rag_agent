"""
AnswerGenerator

Using the LLM and the provided context generate the answer to the user request

19/03: updated to stream the answer generation
"""

from langchain_core.runnables import Runnable
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.prompts import PromptTemplate

# integration with APM
from py_zipkin.zipkin import zipkin_span

from agent_state import State
from oci_models import get_llm
from prompts import (
    ANSWER_PROMPT_TEMPLATE,
)

from utils import get_console_logger
from config import AGENT_NAME

logger = get_console_logger()


class AnswerGenerator(Runnable):
    """
    Takes the user request and the chat history and rewrite the user query
    in a standalone question that is used for the semantic search
    """

    def __init__(self):
        """
        Init
        """

    def build_context_for_llm(self, docs: list):
        """
        Build the context for the final answer from LLM

        docs: list[Documents]
        """
        _context = ""

        for doc in docs:
            _context += doc.page_content + "\n\n"

        return _context

    @zipkin_span(service_name=AGENT_NAME, span_name="answer_generation")
    def invoke(self, input: State, config=None, **kwargs):
        """
        Generate the final answer
        """
        final_answer = ""
        error = None

        try:
            llm = get_llm()

            _context = self.build_context_for_llm(input["reranker_docs"])

            _prompt_template = PromptTemplate(
                input_variables=["context"],
                template=ANSWER_PROMPT_TEMPLATE,
            )

            system_prompt = _prompt_template.format(context=_context)

            messages = [
                SystemMessage(content=system_prompt),
            ]
            # add the chat history
            for msg in input["chat_history"]:
                messages.append(msg)

            messages.append(HumanMessage(content=input["user_request"]))

            # here we invoke the LLM and we return the generator
            final_answer = llm.stream(messages)

        except Exception as e:
            logger.error("Error in generate_answer: %s", e)
            error = str(e)

        return {"final_answer": final_answer, "error": error}
