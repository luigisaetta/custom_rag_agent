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

    see:
        https://docs.api.nvidia.com/nim/reference/nvidia-llama-3_2-nv-embedqa-1b-v2-infer
    """

    def __init__(self, api_url: str, model: str, batch_size: int = 10):
        """
        Init

        as of now, no security
        args:
            api_url: the endpoint
            mode: the model id string
        """
        self.api_url = api_url
        self.model = model
        self.batch_size = batch_size

    def embed_documents(
        self,
        texts: List[str],
        # must be passage and not document
        input_type: str = "passage",
        truncate: str = "NONE",
        dimensions=2048,
    ) -> List[List[float]]:
        """
        Embed a list of documents using batching.
        """
        all_embeddings: List[List[float]] = []

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            # process a single batch
            resp = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "input": batch,
                    "input_type": input_type,
                    "truncate": truncate,
                    "dimensions": dimensions,
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json().get("data", [])

            if len(data) != len(batch):
                raise ValueError(f"Expected {len(batch)} embeddings, got {len(data)}")
            all_embeddings.extend(item["embedding"] for item in data)
        return all_embeddings

    def embed_query(self, text: str, dimensions=2048) -> List[float]:
        """
        Embed the query (a str)
        """
        return self.embed_documents([text], input_type="query", dimensions=dimensions)[
            0
        ]


#
# Main
#
API_URL = "http://130.61.225.137:8000/v1/embeddings"
MODEL_ID = "nvidia/llama-3.2-nv-embedqa-1b-v2"

embed_model = CustomRESTEmbeddings(api_url=API_URL, model=MODEL_ID)

QUERY = "Who is Larry Ellison?"

# if embedding chunk use embed_document, if query, embed_query
vec = embed_model.embed_documents([QUERY])

print("Vector is: ", vec)
print("Dimension is: ", np.array(vec).shape)
