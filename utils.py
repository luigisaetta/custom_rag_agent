"""
Utils
"""

import logging
import re


def get_console_logger():
    """
    To get a logger to print on console
    """
    logger = logging.getLogger("ConsoleLogger")

    # to avoid duplication of logging
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)

        formatter = logging.Formatter("%(asctime)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.propagate = False

    return logger


def extract_text_triple_backticks(_text):
    """
    Extracts all text enclosed between triple backticks (```) from a string.

    :param text: The input string to analyze.
    :return: A list containing the texts found between triple backticks.
    """
    logger = get_console_logger()

    pattern = r"```(.*?)```"  # Uses (.*?) to capture text between backticks in a non-greedy way
    # re.DOTALL allows capturing multiline content

    try:
        _result = [block.strip() for block in re.findall(pattern, _text, re.DOTALL)][0]
    except Exception as e:
        logger.info("no triple backtickes in extract_text_triple_backticks: %s", e)

        # try to be resilient, return the entire text
        _result = _text

    return _result
