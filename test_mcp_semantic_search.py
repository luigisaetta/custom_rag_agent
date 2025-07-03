"""
Test Semantic Search...
"""

import asyncio
import json
from datetime import datetime, timedelta
from fastmcp import Client
import jwt
import config
from config_private import JWT_SECRET, JWT_ALGORITHM

ENDPOINT = f"http://localhost:{config.PORT}/mcp/"

# The Client uses StreamableHttpTransport for HTTP URLs
client = Client(ENDPOINT)


def create_token(user="test-user"):
    """
    create a JWT token
    """
    payload = {
        "sub": user,  # subject (any string identifying the user)
        "exp": datetime.utcnow() + timedelta(hours=1),  # token expires in one hour
    }
    # show how to create a valid JWT token
    _token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return _token


async def main():
    """
    Main function to demonstrate the semantic search tool.
    """
    async with client:
        print("")
        print("\nCalling semantic_search tool...")
        print("")

        query = "What is Oracle AI Vector Search?"

        # create the JWT token
        token = create_token()

        results = await client.call_tool(
            "semantic_search",
            {
                "token": token,
                "query": query,
                "top_k": 5,
                "collection_name": "BOOKS",
            },
        )

        relevant_docs = json.loads(results[0].text)["relevant_docs"]

        print("--- Query: ", query)
        print("Search Results:")
        print("")
        for doc in relevant_docs:
            print(doc["page_content"])
            print("Metadata:", doc["metadata"])
            print("")


asyncio.run(main())
