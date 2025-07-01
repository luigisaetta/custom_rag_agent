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
        print("Calling get_collection tool...")
        print("")


        results = await client.call_tool(
            "get_collections",
            {
            },
        )

        print("List Collections Results:")
        for result in results:
            print("Collection name: ", result.text)
        print()
        
asyncio.run(main())
