"""
File name: rag_feedback.py
Author: Luigi Saetta
Date last modified: 2025-03-31
Python Version: 3.11

Description:
    This module implements handling of user's feedback.
    Based on LangGraph.

Usage:
    Import this module into other scripts to use its functions.
    Example:


License:
    This code is released under the MIT License.

Notes:
    This is a part of a demo showing how to implement an advanced
    RAG solution as a LangGraph agent.

Warnings:
    This module is in development, may change in future versions.
"""

from datetime import datetime
import oracledb

from utils import get_console_logger
from config_private import CONNECT_ARGS

logger = get_console_logger()


class RagFeedback:
    """
    To register user feedback in the RAG_FEEDBACK table.
    """

    def __init__(self):
        """
        Init
        """

    def get_connection(self):
        """Establish the Oracle DB connection."""
        return oracledb.connect(**CONNECT_ARGS)

    def table_exists(self, table_name: str) -> bool:
        # utilizza USER_TABLES per lo schema corrente
        sql = """
            SELECT COUNT(*) 
            FROM user_tables 
            WHERE table_name = :tn
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, tn=table_name.upper())

            return cursor.fetchone()[0] > 0

    def insert_feedback(self, question: str, answer: str, feedback: int):
        """Insert a new feedback record into RAG_FEEDBACK table."""
        if feedback < 1 or feedback > 5:
            raise ValueError("Feedback must be a number between 1 and 5.")

        sql = """
            INSERT INTO RAG_FEEDBACK (CREATED_AT, QUESTION, ANSWER, FEEDBACK)
            VALUES (:created_at, :question, :answer, :feedback)
        """

        if self.table_exists("RAG_FEEDBACK"):
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    sql,
                    {
                        "created_at": datetime.now(),
                        "question": question,
                        "answer": answer,
                        "feedback": feedback,
                    },
                )
                conn.commit()
                cursor.close()
        else:
            # table doesn't exists
            logger.info("Table RAG_FEEDBACK doens't exist...")
