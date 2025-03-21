"""
This module provides a class to register
user feedback in the RAG_FEEDBACK table.
"""

from datetime import datetime
import oracledb

from config_private import CONNECT_ARGS


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

    def insert_feedback(self, question: str, answer: str, feedback: int):
        """Insert a new feedback record into RAG_FEEDBACK table."""
        if feedback < 1 or feedback > 5:
            raise ValueError("Feedback must be a number between 1 and 5.")

        sql = """
            INSERT INTO RAG_FEEDBACK (CREATED_AT, QUESTION, ANSWER, FEEDBACK)
            VALUES (:created_at, :question, :answer, :feedback)
        """

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
