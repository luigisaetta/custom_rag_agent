"""
File name: tests/nvidia_test01.py
Author: Luigi Saetta
Last modified: 25-02-2026
Python Version: 3.11
License: MIT
Description: Manual test script to validate NVIDIA NIM embeddings response shape for Llama embed model.
"""

import numpy as np
from core.custom_rest_embeddings import CustomRESTEmbeddings

#
# Main
#
API_URL = "http://130.61.225.137:8000/v1/embeddings"
MODEL_ID = "nvidia/llama-3.2-nv-embedqa-1b-v2"
DIMENSIONS = 1024

embed_model = CustomRESTEmbeddings(
    api_url=API_URL, model=MODEL_ID, dimensions=DIMENSIONS
)

QUERY = "Who is Larry Ellison?"

# if embedding chunk use embed_document, if query, embed_query
vec = embed_model.embed_documents([QUERY])

print("Vector is: ", vec)
print("Dimension is: ", np.array(vec).shape)
