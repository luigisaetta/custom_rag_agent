"""
Test similarity search
"""

from agent_state import State
from vector_search import SemanticSearch
from utils import get_console_logger

logger = get_console_logger()

v_search = SemanticSearch()

questions = [
    "Chi è Luigi Saetta?",
    "Cosa è l'aspirina?",
    "Quali sono gli effetti collaterali noti della tachipirina?",
    "What is Oracle Vector Search?",
    "Who is Larry Ellison?",
    "Describe the most relevant innovations in GPT-4",
    "Quali sono gli effetti positivi che l'adozione dell'AI Generativa può portare per l'economia italiana?",
    "Cosa è la tachipirina?",
]

N_ERRORS = 0

print("")
for i, question in enumerate(questions):
    print(f"Test n. {i+1},  Question: {question}")

    input_state = State(user_request=question, standalone_question=question)

    try:
        retriever_docs = v_search.invoke(input_state)

        if len(retriever_docs) == 0:
            logger.error("No record found!")
            N_ERRORS += 1

    except Exception as e:
        logger.info("")
        logger.error("Error in vector_search.invoke %s", e)
        logger.info("")
        N_ERRORS += 1

print("")
print("Total tests: ", len(questions))
print(f"Errors: {N_ERRORS}")
print("")
