"""
To test Embeddings from NVIDIA NIMS
"""

from typing import List
import numpy as np
from langchain_core.embeddings import Embeddings
import requests


class CustomRESTEmbeddings(Embeddings):
    """
    Custom class to wrap an embedding moel with rest interface from NVIDIA NIM
    """

    def __init__(self, api_url: str, model: str):
        self.api_url = api_url
        self.model = model

    def embed_documents(
        self, texts: List[str], input_type="document"
    ) -> List[List[float]]:
        """
        Embed a list of documents
        """
        resp = requests.post(
            self.api_url,
            json={
                "input": texts,
                "model": self.model,
                # can be only document or query
                "input_type": input_type,
            },
            timeout=30,
        )
        resp.raise_for_status()
        # should return {"data":[{"embedding":[...]}...]}
        return [item["embedding"] for item in resp.json()["data"]]

    def embed_query(self, text: str) -> List[float]:
        """
        Embed the query (a str)
        """
        return self.embed_documents([text], input_type="query")[0]


#
# Main
#
API_URL = "http://130.61.225.137:8000/v1/embeddings"
MODEL_ID = "nvidia/llama-3.2-nv-embedqa-1b-v2"

embed_model = CustomRESTEmbeddings(api_url=API_URL, model=MODEL_ID)

QUERY = "Who is Larry Ellison?"

vec = embed_model.embed_query(QUERY)

print("Vector is: ", vec)
print("Dimension is: ", np.array(vec).shape)
