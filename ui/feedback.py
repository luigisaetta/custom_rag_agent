"""
File name: feedback.py
Author: Luigi Saetta
Last modified: 03-03-2026
Python Version: 3.11

Description:
    This module defines feedback callbacks for the Streamlit UI.

Usage:
    Import this module into other scripts to use its functions.
    Example:
        from ui.feedback import register_feedback

License:
    This code is released under the MIT License.
"""

import streamlit as st

from core.rag_feedback import RagFeedback


def register_feedback(logger) -> None:
    """Persist star feedback for latest Q/A pair."""
    n_stars = st.session_state.feedback + 1
    logger.info("Feedback: %d %s", n_stars, "stars")
    logger.info("")

    rag_feedback = RagFeedback()
    rag_feedback.insert_feedback(
        question=st.session_state.chat_history[-2].content,
        answer=st.session_state.chat_history[-1].content,
        feedback=n_stars,
    )
    st.session_state.get_feedback = False
