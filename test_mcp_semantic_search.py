"""
Test Semantic Search...
"""

import asyncio
import json
from fastmcp import Client
from jwt_utils import create_jwt_token
import config

ENDPOINT = f"http://localhost:{config.PORT}/mcp/"

# The Client uses StreamableHttpTransport for HTTP URLs
client = Client(ENDPOINT)


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
        # can pass a user here
        token = create_jwt_token()

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
