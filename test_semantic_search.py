"""
Test Semantic Search...
"""

import json
import asyncio
from fastmcp import Client
import config

ENDPOINT = f"http://localhost:{config.PORT}/mcp/"

# The Client uses StreamableHttpTransport for HTTP URLs
client = Client(ENDPOINT)


async def main():
    """
    Main function to demonstrate the semantic search tool.
    """
    async with client:
        # getthe list of available tools
        tools = await client.list_tools()

        print("")
        print("---Available tools:")
        print("")
        for tool in tools:
            print(f"Tool: {tool.name} - {tool.description}")
            # print the input schema for the tool
            print("Input Schema:")
            pretty_schema = json.dumps(tool.inputSchema, indent=4, sort_keys=True)
            print(pretty_schema)
            print("")

        print("")
        print("\nCalling semantic_search tool...")
        print("")

        query = "What is Oracle AI Vector Search?"

        results = await client.call_tool(
            "semantic_search",
            {
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
