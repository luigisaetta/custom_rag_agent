"""
File name: assistant_ui.py
Author: Luigi Saetta
Date created: 2023-12-04
Date last modified: 2025-03-19
Python Version: 3.11

Description:
    This module provides the UI for the RAG demo

Usage:
    streamlit run assistant_ui_langgraph.py

License:
    This code is released under the MIT License.

Notes:
    This is part of a  series of demo developed using OCI GenAI and LangChain

Warnings:
    This module is in development, may change in future versions.
"""

import uuid
from typing import List, Union
import time
import streamlit as st

from langchain_core.messages import HumanMessage, AIMessage

# for APM integration
from py_zipkin.zipkin import zipkin_span
from py_zipkin import Encoding

from rag_agent import State, create_workflow
from transport import http_transport
from utils import get_console_logger
from config import AGENT_NAME, COLLECTION_NAME

# Constant

# name for the roles

USER = "user"
ASSISTANT = "assistant"

logger = get_console_logger()

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "workflow" not in st.session_state:
    # the agent instance
    st.session_state.workflow = create_workflow()
if "thread_id" not in st.session_state:
    # generate a new thread_Id
    st.session_state.thread_id = str(uuid.uuid4())
if "model_id" not in st.session_state:
    st.session_state.model_id = "meta.llama3.3-70B"
if "main_language" not in st.session_state:
    st.session_state.main_language = "en"


#
# supporting functions
#
def display_msg_on_rerun(chat_hist: List[Union[HumanMessage, AIMessage]]) -> None:
    """Display all messages on rerun."""
    for msg in chat_hist:
        role = USER if isinstance(msg, HumanMessage) else ASSISTANT
        with st.chat_message(role):
            st.markdown(msg.content)


# when push the button reset the chat_history
def reset_conversation():
    """Reset the chat history."""
    st.session_state.chat_history = []

    # change thread_id
    st.session_state.thread_id = str(uuid.uuid4())


def add_to_chat_history(msg):
    """
    add the msg to chat history
    """
    st.session_state.chat_history.append(msg)


def get_chat_history():
    """return the chat history from the session"""
    return st.session_state.chat_history


#
# Main
#
st.title("OCI Custom RAG Agent")

# Reset button
if st.sidebar.button("Clear Chat History"):
    reset_conversation()

# the collection used for semantic search
st.sidebar.markdown("### Collection")
st.sidebar.markdown(COLLECTION_NAME)

st.sidebar.header("Options")

# add the choice of LLM (not used for now)
st.session_state.main_language = st.sidebar.selectbox(
    "Select the main language", ["en", "it", "fr"]
)
st.session_state.model_id = st.sidebar.selectbox(
    "Select the Chat Model",
    ["meta.llama-3.3-70b-instruct", "cohere.command-r-plus-08-2024"],
)
ENABLE_RERANKER = st.sidebar.checkbox("Enable Reranker", value=True, disabled=True)


#
# Here the code where react to user input
#

# Display chat messages from history on app rerun
display_msg_on_rerun(get_chat_history())

if question := st.chat_input("Hello, how can I help you?"):
    # Display user message in chat message container
    st.chat_message(USER).markdown(question)

    try:
        with st.spinner("Calling AI..."):
            time_start = time.time()

            # get the chat history to give as input to LLM
            _chat_history = get_chat_history()

            # modified to be more responsive, show result asap
            try:
                input_state = State(
                    user_request=question,
                    chat_history=_chat_history,
                    error=None,
                )

                # collect the results of all steps
                results = []
                ERROR = None

                # integration with tracing, start the trace
                with zipkin_span(
                    service_name=AGENT_NAME,
                    span_name="stream",
                    transport_handler=http_transport,
                    encoding=Encoding.V2_JSON,
                    sample_rate=100,
                ) as span:
                    # loop to manage streaming
                    # set the agent config
                    agent_config = {
                        "configurable": {
                            "model_id": st.session_state.model_id,
                            "main_language": st.session_state.main_language,
                            "enable_reranker": ENABLE_RERANKER,
                            "thread_id": st.session_state.thread_id,
                        }
                    }

                    logger.info("Agent config: %s", agent_config)

                    for event in st.session_state.workflow.stream(
                        input_state,
                        config=agent_config,
                    ):
                        for key, value in event.items():
                            MSG = f"Completed: {key}!"
                            logger.info(MSG)
                            st.toast(MSG)
                            results.append(value)

                            # to see if there has been an error
                            ERROR = value["error"]

                            # update UI asap
                            if key == "QueryRewrite":
                                st.sidebar.header("Standalone question:")
                                st.sidebar.write(value["standalone_question"])
                            if key == "Rerank":
                                st.sidebar.header("References:")
                                st.sidebar.write(value["citations"])

                # process final result from agent
                if ERROR is None:
                    # visualize the output
                    answer_generator = results[-1]["final_answer"]

                    # Stream
                    with st.chat_message(ASSISTANT):
                        response_container = st.empty()
                        full_response = ""

                        for chunk in answer_generator:
                            full_response += chunk.content
                            response_container.markdown(full_response + "▌")

                        response_container.markdown(full_response)

                else:
                    st.error(ERROR)

                # Add user/assistant message to chat history
                add_to_chat_history(HumanMessage(content=question))
                add_to_chat_history(AIMessage(content=full_response))

            except Exception as e:
                ERR_MSG = f"Error in assistant_ui, generate_and_exec {e}"
                logger.error(ERR_MSG)
                st.error(ERR_MSG)

        elapsed_time = round((time.time() - time_start), 1)
        logger.info("Elapsed time: %s sec.", elapsed_time)

    except Exception as e:
        ERR_MSG = "An error occurred: " + str(e)
        logger.error(ERR_MSG)
        st.error(ERR_MSG)
