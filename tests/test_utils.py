from types import SimpleNamespace

import pytest

import core.utils as utils


def test_extract_json_from_text_success():
    text = "prefix {\"a\": 1, \"b\": \"x\"} suffix"
    assert utils.extract_json_from_text(text) == {"a": 1, "b": "x"}


def test_extract_json_from_text_raises_when_missing():
    with pytest.raises(ValueError, match="No JSON content found"):
        utils.extract_json_from_text("nothing to parse")


def test_remove_path_from_ref_returns_basename():
    assert utils.remove_path_from_ref("/tmp/docs/file.pdf") == "file.pdf"


def test_docs_serializable_maps_documents():
    docs = [
        SimpleNamespace(page_content="hello", metadata={"source": "a.pdf"}),
        SimpleNamespace(page_content="world", metadata=None),
    ]

    serialized = utils.docs_serializable(docs)

    assert serialized == [
        {"page_content": "hello", "metadata": {"source": "a.pdf"}},
        {"page_content": "world", "metadata": {}},
    ]
