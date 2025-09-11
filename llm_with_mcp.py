"""
Test LLM and MCP3
Based on fastmcp library.
This one provide also support for security in MCP calls, using JWT token.
"""

import json
import asyncio
from typing import List, Dict, Any, Callable

from fastmcp import Client as MCPClient
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

# our code imports
from oci_jwt_client import OCIJWTClient
from oci_models import get_llm
from utils import get_console_logger
from config import IAM_BASE_URL
from config_private import SECRET_OCID
from mcp_servers_config import MCP_SERVERS_CONFIG

logger = get_console_logger()

# ---- Config ----
MCP_URL = MCP_SERVERS_CONFIG["oci-semantic-search"]["url"]
TIMEOUT = 60
# the scope for the JWT token
SCOPE = "urn:opc:idm:__myscopes__"


def default_jwt_supplier() -> str:
    """
    Get a valid JWT token to make the call to MCP server
    """
    # Always return a FRESH token; do not include "Bearer " (FastMCP adds it)
    token, _, _ = OCIJWTClient(IAM_BASE_URL, SCOPE, SECRET_OCID).get_token()
    return token


SYSTEM_PROMPT = """You are an AI assistant equipped with an MCP server and several tools.
Use the collection BOOKS to get the additional information you need.
"""


class AgentWithMCP:
    """
    LLM + MCP orchestrator.
    - Discovers tools from an MCP server (JWT-protected)
    - Binds tool JSON Schemas to the LLM
    - Executes tool calls emitted by the LLM and loops until completion
    """

    def __init__(
        self,
        mcp_url: str,
        jwt_supplier: Callable[[], str],
        timeout: int,
        llm,
    ):
        self.mcp_url = mcp_url
        self.jwt_supplier = jwt_supplier
        self.timeout = timeout
        self.llm = llm
        self.model_with_tools = None
        # optional: cache tools to avoid re-listing every run
        self._tools_cache = None

    # ---------- helpers now INSIDE the class ----------

    @staticmethod
    def _tool_to_schema(t: object) -> dict:
        """
        Convert an MCP tool (name, description, inputSchema) to a JSON-Schema dict
        that LangChain's ChatCohere.bind_tools accepts (top-level schema).
        """
        input_schema = (getattr(t, "inputSchema", None) or {}).copy()
        if input_schema.get("type") != "object":
            input_schema.setdefault("type", "object")
            input_schema.setdefault("properties", {})
        return {
            "title": getattr(t, "name", "tool"),
            "description": getattr(t, "description", "") or "",
            **input_schema,
        }

    async def _list_tools(self):
        """
        Fetch tools from the MCP server using FastMCP. Must be async.
        """
        jwt = self.jwt_supplier()
        logger.info("Listing tools from %s ...", self.mcp_url)
        # FastMCP requires async context + await for client ops. :contentReference[oaicite:1]{index=1}
        async with MCPClient(self.mcp_url, auth=jwt, timeout=self.timeout) as c:
            # returns Tool objects
            return await c.list_tools()

    async def _call_tool(self, name: str, args: Dict[str, Any]):
        """
        Execute a single MCP tool call.
        """
        jwt = self.jwt_supplier()
        logger.info("Calling MCP tool '%s' with args %s", name, args)
        async with MCPClient(self.mcp_url, auth=jwt, timeout=self.timeout) as c:
            return await c.call_tool(name, args or {})

    @classmethod
    async def create(
        cls,
        mcp_url: str = MCP_URL,
        jwt_supplier: Callable[[], str] = default_jwt_supplier,
        timeout: int = TIMEOUT,
        model_id: str = "cohere.command-a-03-2025",
    ):
        """
        Async factory: fetch tools, bind them to the LLM, return a ready-to-use agent.
        Avoids doing awaits in __init__.
        """
        # should return a LangChain Chat model supporting .bind_tools(...)
        llm = get_llm(model_id=model_id)
        self = cls(mcp_url, jwt_supplier, timeout, llm)

        tools = await self._list_tools()
        if not tools:
            logger.warning("No tools discovered at %s", mcp_url)
        self._tools_cache = tools

        schemas = [self._tool_to_schema(t) for t in tools]
        self.model_with_tools = self.llm.bind_tools(schemas)
        return self

    # ---------- main loop ----------
    async def answer(self, question: str) -> str:
        """
        Run the LLM+MCP loop until the model stops calling tools.
        """
        messages: List[Any] = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=question),
        ]

        while True:
            ai: AIMessage = await self.model_with_tools.ainvoke(messages)

            tool_calls = getattr(ai, "tool_calls", None) or []
            if not tool_calls:
                # Final answer
                return ai.content

            messages.append(ai)  # keep the AI msg that requested tools

            # Execute tool calls and append ToolMessage for each
            for tc in tool_calls:
                name = tc["name"]
                args = tc.get("args") or {}
                try:
                    result = await self._call_tool(name, args)
                    payload = (
                        getattr(result, "data", None)
                        or getattr(result, "content", None)
                        or str(result)
                    )
                    messages.append(
                        ToolMessage(
                            content=json.dumps(payload),
                            # must match the call id
                            tool_call_id=tc["id"],
                            name=name,
                        )
                    )
                except Exception as e:
                    messages.append(
                        ToolMessage(
                            content=json.dumps({"error": str(e)}),
                            tool_call_id=tc["id"],
                            name=name,
                        )
                    )


# ---- Example CLI usage ----
if __name__ == "__main__":
    q = "Tell me about Luigi Saetta. I need his e-mail address also."
    agent = asyncio.run(AgentWithMCP.create())
    print(asyncio.run(agent.answer(q)))
