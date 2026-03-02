"""
File name: assistant_ui.py
Author: Luigi Saetta
Date created: 2024-12-04
Last modified: 24-02-2026
Python Version: 3.11

Description:
    This module provides the UI for the RAG demo

Usage:
    streamlit run assistant_ui_langgraph.py

License:
    This code is released under the MIT License.

Notes:
    This is part of a  demo for a RAG solution implemented
    using LangGraph

Warnings:
    This module is in development, may change in future versions.
"""

import uuid
import os
import tempfile
from typing import List, Union
import time
import streamlit as st

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.vectorstores import InMemoryVectorStore

# for APM integration
from py_zipkin.zipkin import zipkin_span
from py_zipkin import Encoding

from agent.rag_agent import State, create_workflow
from core.rag_feedback import RagFeedback
from core.transport import http_transport
from core.utils import get_console_logger, docs_serializable
from core.citation_utils import build_citation_url, parse_page_number
from core.session_pdf_vlm import scan_pdf_to_docs_with_vlm
from core.oci_models import get_embedding_model

# changed to better manage ENABLE_TRACING (can be enabled from UI)
import config

# Constant

# Use full-width layout so chat responses can expand in the main panel.
st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
    .stApp .block-container {
        max-width: 98%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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
    st.session_state.model_id = (
        config.LLM_MODEL_ID
        if config.LLM_MODEL_ID in config.MODEL_LIST
        else config.MODEL_LIST[0]
    )
if "enable_reranker" not in st.session_state:
    st.session_state.enable_reranker = True
if "collection_name" not in st.session_state:
    st.session_state.collection_name = config.COLLECTION_LIST[0]

# to manage feedback
if "get_feedback" not in st.session_state:
    st.session_state.get_feedback = False
if "session_pdf_name" not in st.session_state:
    st.session_state.session_pdf_name = ""
if "session_pdf_chunks_count" not in st.session_state:
    st.session_state.session_pdf_chunks_count = 0
if "session_pdf_vector_store" not in st.session_state:
    st.session_state.session_pdf_vector_store = None
if "session_pdf_docs" not in st.session_state:
    st.session_state.session_pdf_docs = []


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
    st.session_state.session_pdf_name = ""
    st.session_state.session_pdf_chunks_count = 0
    st.session_state.session_pdf_vector_store = None
    st.session_state.session_pdf_docs = []

    # change thread_id
    st.session_state.thread_id = str(uuid.uuid4())


def add_to_chat_history(msg):
    """
    add the msg to chat history
    """
    st.session_state.chat_history.append(msg)


def get_chat_history():
    """return the chat history from the session"""
    return (
        st.session_state.chat_history[-config.MAX_MSGS_IN_HISTORY :]
        if config.MAX_MSGS_IN_HISTORY > 0
        else st.session_state.chat_history
    )


def register_feedback():
    """
    Register the feedback.
    """
    # number of stars, start at 0
    n_stars = st.session_state.feedback + 1
    logger.info("Feedback: %d %s", n_stars, "stars")
    logger.info("")

    # register the feedback in DB
    rag_feedback = RagFeedback()

    rag_feedback.insert_feedback(
        question=st.session_state.chat_history[-2].content,
        answer=st.session_state.chat_history[-1].content,
        feedback=n_stars,
    )

    st.session_state.get_feedback = False


def render_references(citations: list) -> None:
    """
    Render references in a collapsable section and include link in each reference dict.
    """
    if not citations:
        st.sidebar.write("No references available.")
        return

    with st.sidebar.expander("Show references", expanded=False):
        for ref in citations:
            source = ref.get("source", "unknown")
            page = ref.get("page", "")
            retrieval_type = ref.get("retrieval_type", "semantic")
            is_session_pdf_ref = str(retrieval_type).startswith("session_pdf")
            page_number = parse_page_number(page)

            # Session PDF references come from in-memory uploaded docs and have no static server URL.
            if is_session_pdf_ref:
                st.markdown(
                    f'{{"source": "{source}", "page": "{page}", "retrieval_type": "{retrieval_type}"}}'
                )
            elif page_number is not None:
                url = build_citation_url(source, page_number)
                st.markdown(
                    f'{{"source": "{source}", "page": "{page}", "retrieval_type": "{retrieval_type}", "link": [{url}]({url})}}'
                )
            else:
                st.markdown(
                    f'{{"source": "{source}", "page": "{page}", "retrieval_type": "{retrieval_type}", "link": ""}}'
                )


def _safe_agent_config_for_log(
    agent_config: dict, max_docs_preview: int = 2, max_chars: int = 160
) -> dict:
    """
    Build a redacted version of agent config for logging.
    In particular, truncate session_pdf_docs to avoid logging full PDF content.
    """
    safe = dict(agent_config)
    configurable = dict(safe.get("configurable", {}))
    docs = list(configurable.get("session_pdf_docs", []) or [])

    preview = []
    for doc in docs[:max_docs_preview]:
        metadata = dict((doc or {}).get("metadata", {}) or {})
        text = str((doc or {}).get("page_content", "") or "")
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        preview.append({"page_content": text, "metadata": metadata})

    configurable["session_pdf_docs"] = {
        "count": len(docs),
        "preview": preview,
    }
    safe["configurable"] = configurable
    return safe


#
# Main
#
st.title("OCI Enterprise Knowledge Assistant")

# Reset button
if st.sidebar.button("Clear Chat History"):
    reset_conversation()


st.sidebar.header("Options")

st.sidebar.text_input(label="LLM Region", value=config.LLM_REGION, disabled=True)
st.sidebar.text_input(label="Embed Region", value=config.EMBED_REGION, disabled=True)

# the collection used for semantic search
st.session_state.collection_name = st.sidebar.selectbox(
    "Collection name",
    config.COLLECTION_LIST,
)

st.session_state.model_id = st.sidebar.selectbox(
    "Select the Chat Model",
    config.MODEL_LIST,
    index=(
        config.MODEL_LIST.index(st.session_state.model_id)
        if st.session_state.model_id in config.MODEL_LIST
        else 0
    ),
)

st.sidebar.text_input(label="Embed Model", value=config.EMBED_MODEL_ID, disabled=True)
st.sidebar.text_input(label="Session PDF VLM", value=config.VLM_MODEL_ID, disabled=True)

st.session_state.enable_reranker = st.sidebar.checkbox(
    "Enable Reranker", value=True, disabled=False
)
st.session_state.enable_advanced_analysis = st.sidebar.checkbox(
    "Advanced Analysis", value=False, disabled=False
)
config.ENABLE_TRACING = st.sidebar.checkbox(
    "Enable tracing", value=False, disabled=False
)

st.sidebar.header("Session PDF (in-memory)")
session_pdf = st.sidebar.file_uploader(
    "Upload a PDF for this session",
    type=["pdf"],
    key="session_pdf_upload",
)

if st.sidebar.button("Scan PDF in memory"):
    # process the uploaded PDF, extract text with VLM and 
    # add it to an in-memory vector store for retrieval during the session
    if session_pdf is None:
        st.sidebar.warning("Please upload a PDF first.")
    else:
        status_slot = st.sidebar.empty()
        progress_bar = st.sidebar.progress(0)
        tmp_path = ""

        try:
            status_slot.info("Saving uploaded PDF...")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(session_pdf.read())
                tmp_path = tmp_file.name
            progress_bar.progress(20)

            status_slot.info("Scanning PDF pages with VLM...")

            def _on_page_progress(current_page: int, total_pages: int):
                # Reserve [25..95] for per-page OCR progress.
                if total_pages > 0:
                    pct = 25 + int((current_page / total_pages) * 70)
                    progress_bar.progress(min(pct, 95))

            # scan the PDF with VLM, get the text chunks and the page count
            docs, page_count = scan_pdf_to_docs_with_vlm(
                pdf_path=tmp_path,
                vlm_model_id=config.VLM_MODEL_ID,
                max_pages=config.SESSION_PDF_MAX_PAGES,
                source_name=session_pdf.name,
                on_progress=_on_page_progress,
            )

            # addings the scanned docs to an in-memory vector store, to be used for retrieval during the session
            status_slot.info("Building in-memory vector index...")
            progress_bar.progress(97)
            embed_model = get_embedding_model(model_type=config.EMBED_MODEL_TYPE)
            session_vs = InMemoryVectorStore(embedding=embed_model)
            if docs:
                session_vs.add_documents(docs)

            st.session_state.session_pdf_vector_store = session_vs
            st.session_state.session_pdf_name = session_pdf.name
            st.session_state.session_pdf_chunks_count = len(docs)
            st.session_state.session_pdf_docs = docs_serializable(docs)

            progress_bar.progress(100)
            status_slot.success(
                f"Loaded '{session_pdf.name}' in memory ({page_count} pages, {len(docs)} chunks)."
            )
        except Exception as exc:
            logger.error("Error in session PDF scan: %s", exc)
            status_slot.error("PDF scan failed.")
            st.sidebar.error(str(exc))
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)

if st.session_state.session_pdf_name:
    st.sidebar.caption(
        f"In-memory PDF: {st.session_state.session_pdf_name} ({st.session_state.session_pdf_chunks_count} chunks)"
    )


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
                FULL_RESPONSE = ""

                # integration with tracing, start the trace
                with zipkin_span(
                    service_name=config.AGENT_NAME,
                    span_name="stream",
                    transport_handler=http_transport,
                    encoding=Encoding.V2_JSON,
                    sample_rate=100,
                ) as span:
                    # set the agent config
                    agent_config = {
                        "configurable": {
                            "model_id": st.session_state.model_id,
                            "embed_model_type": config.EMBED_MODEL_TYPE,
                            "enable_reranker": st.session_state.enable_reranker,
                            "enable_advanced_analysis": st.session_state.enable_advanced_analysis,
                            "enable_tracing": config.ENABLE_TRACING,
                            "main_language": config.MAIN_LANGUAGE,
                            "collection_name": st.session_state.collection_name,
                            "thread_id": st.session_state.thread_id,
                            "session_pdf_vector_store": st.session_state.session_pdf_vector_store,
                            "session_pdf_chunks_count": st.session_state.session_pdf_chunks_count,
                            "session_pdf_docs": st.session_state.session_pdf_docs,
                            "advanced_analysis_max_actions": config.ADVANCED_ANALYSIS_MAX_ACTIONS,
                            "advanced_analysis_kb_top_k": config.ADVANCED_ANALYSIS_KB_TOP_K,
                            "advanced_analysis_step_max_words": config.ADVANCED_ANALYSIS_STEP_MAX_WORDS,
                        }
                    }

                    logger.info("")
                    logger.info("Agent config: %s", _safe_agent_config_for_log(agent_config))
                    logger.info("")

                    # loop to manage streaming
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
                            if key == "IntentClassifier":
                                logger.info(
                                    "Intent decision: %s (has_session_pdf=%s)",
                                    value.get("search_intent"),
                                    value.get("has_session_pdf"),
                                )
                            if key == "Rerank":
                                st.sidebar.header("References:")
                                render_references(value["citations"])

                # process final result from agent
                if ERROR is None:
                    # visualize the output
                    answer_payload = results[-1]["final_answer"]

                    with st.chat_message(ASSISTANT):
                        response_container = st.empty()
                        FULL_RESPONSE = ""

                        if isinstance(answer_payload, str):
                            FULL_RESPONSE = answer_payload
                            response_container.markdown(FULL_RESPONSE)
                        else:
                            for chunk in answer_payload:
                                FULL_RESPONSE += chunk.content
                                response_container.markdown(FULL_RESPONSE + "▌")
                            response_container.markdown(FULL_RESPONSE)

                    elapsed_time = round((time.time() - time_start), 1)
                    logger.info("Elapsed time: %s sec.", elapsed_time)
                    logger.info("")

                    if config.ENABLE_USER_FEEDBACK:
                        st.session_state.get_feedback = True

                else:
                    st.error(ERROR)

                # Add user/assistant message to chat history
                add_to_chat_history(HumanMessage(content=question))
                if FULL_RESPONSE:
                    add_to_chat_history(AIMessage(content=FULL_RESPONSE))

                # get the feedback
                if st.session_state.get_feedback:
                    st.feedback("stars", key="feedback", on_change=register_feedback)

            except Exception as e:
                ERR_MSG = f"Error in assistant_ui, generate_and_exec {e}"
                logger.error(ERR_MSG)
                st.error(ERR_MSG)

    except Exception as e:
        ERR_MSG = "An error occurred: " + str(e)
        logger.error(ERR_MSG)
        st.error(ERR_MSG)
