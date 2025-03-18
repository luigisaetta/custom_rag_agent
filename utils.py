"""
Utils
"""

import logging
import re
import json


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


def extract_json_from_text(text):
    """
    Extracts JSON content from a given text and returns it as a Python dictionary.

    Args:
        text (str): The input text containing JSON content.

    Returns:
        dict: Parsed JSON data.
    """
    try:
        # Use regex to extract JSON content
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            json_content = json_match.group(0)
            return json.loads(json_content)

        # If no JSON content is found, raise an error
        raise ValueError("No JSON content found in the text.")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")
