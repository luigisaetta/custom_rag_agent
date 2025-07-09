"""
Explore an MCP serer and get list and description of tools.

The sever must be accessible through HTTP streaming.
"""

import asyncio
import streamlit as st
from fastmcp import Client

st.set_page_config(page_title="MCP Explorer", layout="wide")
st.title("🚀 MCP Tool Explorer")

# Config
DEFAULT_URL = "http://localhost:9000/mcp/"
server_url = st.text_input("URL MCP:", DEFAULT_URL)
TIMEOUT = 30

# Stato della sessione
if "tools" not in st.session_state:
    st.session_state.tools = []
if "error" not in st.session_state:
    st.session_state.error = None


async def fetch_tools():
    """
    This function call the MCP sevrer to get list and descriptions of tools
    """
    async with Client(server_url, timeout=TIMEOUT) as client:
        return await client.list_tools()


if st.button("🔍 Load tools..."):
    st.session_state.error = None
    st.session_state.tools = []
    with st.spinner("Calling server…"):
        try:
            tools = asyncio.run(fetch_tools())
            st.session_state.tools = tools
        except Exception as e:
            st.session_state.error = e

# Visualize
if st.session_state.error:
    st.error(f"❌ Error: {st.session_state.error}")
elif st.session_state.tools:
    st.success(f"✅ {len(st.session_state.tools)} tools found.")
    cols = st.columns(3)

    for i, t in enumerate(st.session_state.tools):
        with cols[i % 3]:
            st.markdown(f"### **{t.name}**")
            if t.description:
                st.write(t.description)
            # st.write(t)
            if t.inputSchema:
                with st.expander("📘 Input Schema"):
                    st.json(t.inputSchema)
            st.divider()
